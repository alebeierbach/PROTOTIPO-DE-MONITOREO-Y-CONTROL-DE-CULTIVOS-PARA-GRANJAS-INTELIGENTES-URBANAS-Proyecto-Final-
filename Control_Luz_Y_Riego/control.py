from datetime import datetime
from typing import Optional, Tuple, List, Dict

from models import MacetaConfig, MacetaEstado, GlobalConfig


def esta_en_horario_activo(hora_actual: int, hora_inicio: int, hora_fin: int) -> bool:
    if hora_inicio < hora_fin:
        return hora_inicio <= hora_actual < hora_fin
    return hora_actual >= hora_inicio or hora_actual < hora_fin


def raw_a_porcentaje(raw_8bit: int, raw_seco: int, raw_mojado: int) -> int:
    humedad = int((raw_8bit - raw_seco) * 100 / (raw_mojado - raw_seco))
    return max(0, min(100, humedad))


def lectura_humedad_valida(raw_8bit: Optional[int]) -> bool:
    if raw_8bit is None:
        return False
    return 0 <= raw_8bit <= 255


def procesar_humedad_suelo(
    raw1: Optional[int],
    raw2: Optional[int],
    global_config: GlobalConfig
) -> Tuple[Optional[int], Optional[int], Optional[int], List[str]]:
    alertas = []

    val1 = lectura_humedad_valida(raw1)
    val2 = lectura_humedad_valida(raw2)

    hum1 = raw_a_porcentaje(raw1, global_config.raw_seco, global_config.raw_mojado) if val1 else None
    hum2 = raw_a_porcentaje(raw2, global_config.raw_seco, global_config.raw_mojado) if val2 else None

    if val1 and val2:
        promedio = int((hum1 + hum2) / 2)

        if abs(hum1 - hum2) > global_config.discrepancia_humedad_pct:
            alertas.append(f"Discrepancia alta entre sensores de humedad: {hum1}% vs {hum2}%")

        return hum1, hum2, promedio, alertas

    if val1 and not val2:
        alertas.append("Fallo sensor de humedad 2, se usa sensor 1")
        return hum1, None, hum1, alertas

    if val2 and not val1:
        alertas.append("Fallo sensor de humedad 1, se usa sensor 2")
        return None, hum2, hum2, alertas

    alertas.append("Fallo en ambos sensores de humedad de suelo")
    return None, None, None, alertas


def lectura_dht_valida(
    temperatura_c: Optional[float],
    humedad_ambiente_pct: Optional[float]
) -> bool:
    if temperatura_c is None or humedad_ambiente_pct is None:
        return False

    if not (-20 <= temperatura_c <= 80):
        return False

    if not (0 <= humedad_ambiente_pct <= 100):
        return False

    return True

def calcular_y_controlar_dli(
    maceta: MacetaConfig, 
    lux_ambiente: Optional[float],
    dli_acumulado: float,
    luz_esta_encendida: bool,
    dt_segundos: float,
    ahora: datetime
) -> Tuple[bool, float, List[str]]:
    alertas = []
    
    # chequeamos que este habilitada la luz antes de cualquier cosa
    if not maceta.luz.enabled:
        return False, dli_acumulado, alertas

    # Extraemos la configuración diurna de la maceta
    hora_inicio = maceta.hora_inicio_dia
    hora_fin = maceta.hora_fin_dia
    dli_objetivo = maceta.dli_objetivo
    lux_foco = maceta.lux_foco
    F_L = maceta.factor_luminaria
    F_L_ambiente = maceta.factor_luminaria_ambiente
    # Cálculo dinámico de PPFD y suma
    ppfd_foco = lux_foco * F_L
    ppfd_ambiente = (lux_ambiente * F_L_ambiente) if lux_ambiente is not None else 0.0
    ppfd_total = ppfd_ambiente + (ppfd_foco if luz_esta_encendida else 0.0)

    # Integramos
    horas_transcurridas = dt_segundos / 3600.0
    incremento_dli = 0.0036 * ppfd_total * horas_transcurridas
    nuevo_dli = dli_acumulado + incremento_dli

    # --- EVALUACIÓN DEL FOTOPERIODO ---
    hora_actual_decimal = ahora.hour + (ahora.minute / 60.0)

    # Verificamos si estamos dentro del horario
    if hora_inicio <= hora_actual_decimal < hora_fin:
        en_horario = True
    else:
        en_horario = False

    if not en_horario:
        return False, nuevo_dli, alertas

    # 4. Calculamos Ti restante y evaluamos cuanto le falta
    Ti_restante = hora_fin - hora_actual_decimal
    dli_faltante = dli_objetivo - nuevo_dli
    
    if dli_faltante <= 0:
        return False, nuevo_dli, alertas # Ya se cumplió la meta de hoy
        
    dli_potencial_foco = 0.0036 * ppfd_foco * Ti_restante
    
    # Decisión final de encendido
    encender_foco = dli_potencial_foco <= dli_faltante
    
    return encender_foco, nuevo_dli, alertas


def decidir_ventilacion(
    maceta: MacetaConfig,
    temperatura_c: Optional[float],
    humedad_ambiente_pct: Optional[float]
) -> Tuple[bool, List[str]]:
    alertas = []

    if not maceta.ventilador.enabled:
        return False, alertas

    if not lectura_dht_valida(temperatura_c, humedad_ambiente_pct):
        alertas.append("Lectura invalida de DHT, se omite logica de ventilacion")
        return False, alertas

    if temperatura_c > maceta.umbral_temperatura_c:
        alertas.append(f"Temperatura alta en {maceta.nombre}: {temperatura_c:.1f} C")
        return True, alertas

    if humedad_ambiente_pct > maceta.umbral_humedad_ambiente_pct:
        return True, alertas

    return False, alertas

def decidir_riego(maceta: MacetaConfig, raw_promedio_suavizado: Optional[float]) -> Tuple[bool, List[str]]:
    alertas = []
    
    if raw_promedio_suavizado is None:
        return False, alertas
        
    # Lógica de riego en RAW (mayor o igual al umbral). Devuelve true o false para elegir el riego en booleano
    riego = raw_promedio_suavizado >= maceta.umbral_humedad_suelo_raw
    
    if riego:
        alertas.append(f"Tierra seca (Raw: {raw_promedio_suavizado:.1f} >= {maceta.umbral_humedad_suelo_raw}). Riego activado.")
        
    return riego, alertas

def procesar_maceta(
    maceta: MacetaConfig,
    estado: MacetaEstado,
    lecturas: Dict[str, Optional[float]],
    global_config: GlobalConfig,
    dli_acumulado_actual: float = 0.0, 
    dt_segundos: float = 0.0,          
    ahora: Optional[datetime] = None
) -> Tuple[MacetaEstado, float]:       
    if ahora is None:
        ahora = datetime.now()

    nuevo_estado = MacetaEstado()

    # --- 1. RECUPERAR MEMORIA Y FILTRAR ERRORES ---
    nuevo_estado.historial_raw_1 = estado.historial_raw_1.copy()
    nuevo_estado.historial_raw_2 = estado.historial_raw_2.copy()

    raw1_actual = lecturas.get("humedad_raw_1")
    raw2_actual = lecturas.get("humedad_raw_2")

    # Guardamos solo si es válido y DISTINTO de 128
    if raw1_actual is not None and raw1_actual != 128:
        nuevo_estado.historial_raw_1.append(raw1_actual)
        if len(nuevo_estado.historial_raw_1) > 3:
            nuevo_estado.historial_raw_1.pop(0)

    if raw2_actual is not None and raw2_actual != 128:
        nuevo_estado.historial_raw_2.append(raw2_actual)
        if len(nuevo_estado.historial_raw_2) > 3:
            nuevo_estado.historial_raw_2.pop(0)

    # --- 2. CALCULAR VALORES SUAVIZADOS ---
    # Solo calculamos el promedio si tenemos la lista llena (3 mediciones completas)
    raw1_suavizado = sum(nuevo_estado.historial_raw_1) / 3 if len(nuevo_estado.historial_raw_1) == 3 else None
    raw2_suavizado = sum(nuevo_estado.historial_raw_2) / 3 if len(nuevo_estado.historial_raw_2) == 3 else None

    # Promedio unificado de la maceta para decidir el riego
    raws_validos = [r for r in (raw1_suavizado, raw2_suavizado) if r is not None]
    raw_promedio_suavizado = sum(raws_validos) / len(raws_validos) if raws_validos else None
    
    # Convertimos el suavizado a porcentaje solo para registro/CSV
    hum1, hum2, promedio_pct, alertas_humedad = procesar_humedad_suelo(
        raw1_suavizado, raw2_suavizado, global_config
    )

    # Guardamos el estado para el programa
    nuevo_estado.humedad_suelo_raw_1 = raw1_actual  # Guardamos el real para ver si saltan los 128
    nuevo_estado.humedad_suelo_raw_2 = raw2_actual
    nuevo_estado.humedad_suelo_1_pct = hum1
    nuevo_estado.humedad_suelo_2_pct = hum2
    nuevo_estado.humedad_suelo_promedio_pct = promedio_pct

    # --- 3. PROCESAR RESTO DE SENSORES ---
    lux = lecturas.get("lux")              
    temperatura_c = lecturas.get("temperatura_c")
    humedad_ambiente_pct = lecturas.get("humedad_ambiente_pct")
    nuevo_estado.lux = lux

    if lectura_dht_valida(temperatura_c, humedad_ambiente_pct):
        nuevo_estado.temperatura_c = temperatura_c
        nuevo_estado.humedad_ambiente_pct = humedad_ambiente_pct
    else:
        nuevo_estado.temperatura_c = None
        nuevo_estado.humedad_ambiente_pct = None
        if maceta.dht.enabled:
            alertas_humedad.append("Lectura invalida de DHT")

    # --- 4. CONTROL DE LUZ (DLI) Y CLIMA ---
    luz_encendida, nuevo_dli, alertas_luz = calcular_y_controlar_dli(
        maceta=maceta,
        lux_ambiente=lux,
        dli_acumulado=dli_acumulado_actual,
        luz_esta_encendida=estado.luz_encendida,
        dt_segundos=dt_segundos,
        ahora=ahora
    )
    nuevo_estado.dli_acumulado = nuevo_dli

    ventilador_encendido, alertas_vent = decidir_ventilacion(
        maceta,
        nuevo_estado.temperatura_c,
        nuevo_estado.humedad_ambiente_pct
    )

    # --- 5. GATILLO DE RIEGO (Usando el Raw Suavizado) ---
    riego_pendiente, alertas_riego = decidir_riego(
        maceta,
        raw_promedio_suavizado
    )

    nuevo_estado.luz_encendida = luz_encendida
    nuevo_estado.ventilador_encendido = ventilador_encendido
    nuevo_estado.riego_pendiente = riego_pendiente
    nuevo_estado.alertas = alertas_humedad + alertas_luz + alertas_vent + alertas_riego

    return nuevo_estado, nuevo_dli
