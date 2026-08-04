import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# 1. Definir el nombre exacto de tu archivo
archivo_csv = 'registro_completo_abril_agosto.csv'

# Verificar si existe antes de intentar abrirlo
if not os.path.exists(archivo_csv):
    print(f"ERROR: No se encontró el archivo '{archivo_csv}'. Asegurate de ejecutar el script en la misma carpeta.")
    exit()

# Cargar el dataset
df = pd.read_csv(archivo_csv)

# 2. BLINDAJE: Limpiar espacios ocultos en los nombres de las columnas
df.columns = df.columns.str.strip()

if 'fecha' not in df.columns or 'hora' not in df.columns:
    print(f"ERROR: Faltan las columnas 'fecha' y 'hora'. Columnas actuales: {df.columns.tolist()}")
    exit()

# Crear columna datetime para el eje X
df['datetime'] = pd.to_datetime(df['fecha'] + ' ' + df['hora'])

# 3. FILTRAR SOLO EL MES DE JULIO (Mes 7)
df_julio = df[df['datetime'].dt.month == 7].copy()

if df_julio.empty:
    print("ERROR: No hay datos para el mes de Julio en este archivo.")
    exit()

# Separar los datos por maceta
df_m1 = df_julio[df_julio['maceta'] == 'maceta1']
df_m2 = df_julio[df_julio['maceta'] == 'maceta2']

def formatear_eje_x_julio(ax):
    """Como ahora es un solo mes, formateamos para ver los días"""
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3)) # Marca principal cada 3 días
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

def graficar_maceta_separado(df_maceta, nombre_maceta):
    if df_maceta.empty:
        print(f"Aviso: No hay datos para {nombre_maceta}.")
        return

    # ---------------------------------------------------------
    # Gráfico 1: Humedad de suelo y riego
    # ---------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df_maceta['datetime'], df_maceta['humedad_pct_promedio'], label='Humedad Promedio (%)', color='tab:blue')
    
    if 'riego_pendiente' in df_maceta.columns:
        riegos = df_maceta[df_maceta['riego_pendiente'] == 1]
        ax1.scatter(riegos['datetime'], riegos['humedad_pct_promedio'], color='red', marker='v', s=100, label='Riego Activado', zorder=5)
    
    ax1.set_ylabel('Humedad Suelo (%)')
    ax1.set_title(f'Humedad del Suelo (Julio) - {nombre_maceta.capitalize()}')
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--', alpha=0.6)
    formatear_eje_x_julio(ax1)
    
    fig1.tight_layout()
    nombre_humedad = f'humedad_final_julio_{nombre_maceta}.png'
    fig1.savefig(nombre_humedad, dpi=300)
    plt.close(fig1)
    print(f"Guardado: {nombre_humedad}")

    # ---------------------------------------------------------
    # Gráfico 2: DLI y Lux en paralelo
    # ---------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    if 'dli_acumulado' in df_maceta.columns:
        ax2.plot(df_maceta['datetime'], df_maceta['dli_acumulado'], label='DLI Acumulado', color='tab:orange', linewidth=2)
    ax2.set_ylabel('DLI')
    
    ax2_twin = ax2.twinx()
    if 'lux' in df_maceta.columns:
        ax2_twin.plot(df_maceta['datetime'], df_maceta['lux'], label='Lux', color='purple', alpha=0.4)
    ax2_twin.set_ylabel('Lux')
    
    lines_ax2, labels_ax2 = ax2.get_legend_handles_labels()
    lines_ax2_twin, labels_ax2_twin = ax2_twin.get_legend_handles_labels()
    ax2_twin.legend(lines_ax2 + lines_ax2_twin, labels_ax2 + labels_ax2_twin, loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.set_title(f'Luz (DLI y Lux) (Julio) - {nombre_maceta.capitalize()}')
    formatear_eje_x_julio(ax2)
    
    fig2.tight_layout()
    nombre_lux = f'lux_final_julio_{nombre_maceta}.png'
    fig2.savefig(nombre_lux, dpi=300)
    plt.close(fig2)
    print(f"Guardado: {nombre_lux}")

    # ---------------------------------------------------------
    # Gráfico 3: Temperatura y humedad ambiente
    # ---------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    if 'temperatura_c' in df_maceta.columns:
        ax3.plot(df_maceta['datetime'], df_maceta['temperatura_c'], label='Temperatura (°C)', color='tab:red')
    ax3.set_ylabel('Temp (°C)')
    
    ax3_twin = ax3.twinx()
    if 'humedad_ambiente_pct' in df_maceta.columns:
        ax3_twin.plot(df_maceta['datetime'], df_maceta['humedad_ambiente_pct'], label='Humedad Ambiente (%)', color='tab:green', alpha=0.7)
    ax3_twin.set_ylabel('Hum. Ambiente (%)')
    
    lines_ax3, labels_ax3 = ax3.get_legend_handles_labels()
    lines_ax3_twin, labels_ax3_twin = ax3_twin.get_legend_handles_labels()
    ax3_twin.legend(lines_ax3 + lines_ax3_twin, labels_ax3 + labels_ax3_twin, loc='upper right')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.set_title(f'Variables Ambientales (Julio) - {nombre_maceta.capitalize()}')
    formatear_eje_x_julio(ax3)
    
    fig3.tight_layout()
    nombre_temphum = f'temphum_final_julio_{nombre_maceta}.png'
    fig3.savefig(nombre_temphum, dpi=300)
    plt.close(fig3)
    print(f"Guardado: {nombre_temphum}")

    # ---------------------------------------------------------
    # Gráfico 4: Actuadores (Luz y Bomba)
    # ---------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(10, 3))
    if 'luz_encendida' in df_maceta.columns:
        ax4.step(df_maceta['datetime'], df_maceta['luz_encendida'], label='Luz', color='#f1c40f', where='post', linewidth=2)
    if 'riego_pendiente' in df_maceta.columns:
        ax4.step(df_maceta['datetime'], df_maceta['riego_pendiente'], label='Bomba', color='#3498db', where='post', linewidth=2, linestyle='--')
    
    ax4.set_ylabel('Actuadores')
    ax4.set_yticks([0, 1])
    ax4.set_yticklabels(['0 (Off)', '1 (On)'])
    ax4.set_ylim(-0.2, 1.2)
    ax4.legend(loc='upper right')
    ax4.grid(True, linestyle='--', alpha=0.6)
    ax4.set_title(f'Estado de Actuadores (Julio) - {nombre_maceta.capitalize()}')
    formatear_eje_x_julio(ax4)
    
    fig4.tight_layout()
    nombre_actuadores = f'actuadores_final_julio_{nombre_maceta}.png'
    fig4.savefig(nombre_actuadores, dpi=300)
    plt.close(fig4)
    print(f"Guardado: {nombre_actuadores}")
    print("-" * 30)

print("Procesando datos y generando los gráficos por separado (Filtro: Julio)...")
graficar_maceta_separado(df_m1, 'maceta1')
graficar_maceta_separado(df_m2, 'maceta2')
print("¡Todos los gráficos de Julio fueron generados con éxito!")