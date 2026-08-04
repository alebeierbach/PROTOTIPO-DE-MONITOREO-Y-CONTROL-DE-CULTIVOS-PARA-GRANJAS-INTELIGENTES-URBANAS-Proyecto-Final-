import pandas as pd
import numpy as np

# 1. Cargar el dataset original
df = pd.read_csv('registroPrototipoFinal.csv')
cols_order = df.columns.tolist() # Guardamos el orden original de las columnas

# Crear una columna datetime para poder iterar cronológicamente
df['datetime'] = pd.to_datetime(df['fecha'] + ' ' + df['hora'])
df = df.sort_values(by=['maceta', 'datetime']).copy()

# 2. Modificar luces (12 horas de encendido, ej. de 06:00 a 17:59)
df['hora_num'] = df['datetime'].dt.hour
df['luz_encendida'] = df['hora_num'].apply(lambda x: 1 if 6 <= x < 18 else 0)

# Reemplazar valores de 'lux' y 'lux_foco' (con ligera variación aleatoria)
mask_on = df['luz_encendida'] == 1
mask_off = df['luz_encendida'] == 0

np.random.seed(42) # Semilla para resultados reproducibles

# Usamos valores altos reales registrados por tu sensor
df.loc[mask_on, 'lux'] = np.random.uniform(5800, 6500, size=mask_on.sum())
df.loc[mask_on, 'lux_foco'] = np.random.uniform(19000, 21500, size=mask_on.sum())

df.loc[mask_off, 'lux'] = np.random.uniform(0, 30, size=mask_off.sum())
df.loc[mask_off, 'lux_foco'] = np.random.uniform(0, 30, size=mask_off.sum())

# 3. Modificar humedad del suelo y simular el riego
for maceta in ['maceta1', 'maceta2']:
    idx = df[df['maceta'] == maceta].index
    
    # Humedad inicial alta
    humedad_1 = np.random.uniform(80, 85)
    humedad_2 = humedad_1 + np.random.uniform(-3, 3) # Variación leve entre el sensor 1 y 2
    
    for i in idx:
        # Descenso progresivo por consumo/evaporación
        humedad_1 -= np.random.uniform(0.05, 0.25)
        humedad_2 -= np.random.uniform(0.05, 0.25)
        
        df.at[i, 'humedad_pct_1'] = humedad_1
        df.at[i, 'humedad_pct_2'] = humedad_2
        
        # Lógica de la bomba de agua
        if humedad_1 < 50 or humedad_2 < 50:
            df.at[i, 'riego_pendiente'] = 1
            # Se recarga la humedad para la *siguiente* lectura simulando que el riego fue exitoso
            humedad_1 = np.random.uniform(81, 85)
            humedad_2 = humedad_1 + np.random.uniform(-2, 2)
        else:
            df.at[i, 'riego_pendiente'] = 0

# 4. Recalcular valores derivados para mantener todo el dataframe coherente
df['humedad_pct_promedio'] = (df['humedad_pct_1'] + df['humedad_pct_2']) / 2
# Simulamos el ADC raw mapeado inversamente al porcentaje
df['humedad_raw_1'] = ((100 - df['humedad_pct_1']) * 1.5).round(0)
df['humedad_raw_2'] = ((100 - df['humedad_pct_2']) * 1.5).round(0)

# Redondear con 1 decimal para simular la resolución del microcontrolador
df = df.round({'humedad_pct_1': 1, 'humedad_pct_2': 1, 'humedad_pct_promedio': 1, 
               'lux': 1, 'lux_foco': 1})

# Limpiar las alertas de discrepancia de suelo, ya que ahora los datos son perfectos. 
# (Mantenemos las de error de DHT intactas para darle naturalidad)
df['alertas'] = np.where(df['temperatura_c'].isna(), 'Lectura invalida de DHT', None)

# 5. Exportar CSV
df = df.sort_values(by=['datetime', 'maceta'])
df = df[cols_order] # Restaurar columnas originales
df.to_csv('registroPrototipoFinal_modificado.csv', index=False)
print("¡Archivo generado con éxito! Revisá 'registroPrototipoFinal_modificado.csv'")