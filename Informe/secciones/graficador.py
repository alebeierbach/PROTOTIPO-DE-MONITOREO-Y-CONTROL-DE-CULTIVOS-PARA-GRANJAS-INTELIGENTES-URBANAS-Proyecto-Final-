import pandas as pd
import matplotlib.pyplot as plt

# 1. Carga de los datos
df = pd.read_csv('registroPrototipoFinal.csv')

# 2. Preprocesamiento temporal
# Unificamos las columnas de fecha y hora (ahora en minúsculas)
df['Tiempo'] = pd.to_datetime(df['fecha'] + ' ' + df['hora'])

# Llenamos posibles datos faltantes (NaN) para que las líneas del gráfico no se corten
df['lux_foco'] = df['lux_foco'].fillna(0)
df['temperatura_c'] = df['temperatura_c'].interpolate().fillna(method='bfill')
df['humedad_ambiente_pct'] = df['humedad_ambiente_pct'].interpolate().fillna(method='bfill')

# 3. Configuracion del lienzo y los subgraficos
fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
fig.suptitle('Analisis Dinamico de Telemetria del Prototipo Final', fontsize=16)

# Subgrafico 1: Variables de Iluminacion
axs[0].plot(df['Tiempo'], df['lux_foco'], label='Lux Foco', color='#FF8C00')
axs[0].plot(df['Tiempo'], df['lux'], label='Lux Natural', color='#FFD700', alpha=0.7)
axs[0].set_ylabel('Iluminacion (Lux)')
axs[0].legend(loc='upper right')
axs[0].grid(True, linestyle=':', alpha=0.7)

# Subgrafico 2: Variables Ambientales (Temperatura y Humedad del Aire)
axs[1].plot(df['Tiempo'], df['temperatura_c'], label='Temperatura (C)', color='#DC143C')
axs[1].plot(df['Tiempo'], df['humedad_ambiente_pct'], label='Humedad Ambiente (%)', color='#4169E1')
axs[1].set_ylabel('Variables de Aire')
axs[1].legend(loc='upper right')
axs[1].grid(True, linestyle=':', alpha=0.7)

# Subgrafico 3: Variables de Suelo (Promedio de los dos sensores)
axs[2].plot(df['Tiempo'], df['humedad_pct_promedio'], label='Humedad de Suelo (%)', color='#228B22')
axs[2].set_ylabel('Suelo (%)')
axs[2].legend(loc='upper right')
axs[2].grid(True, linestyle=':', alpha=0.7)

# Subgrafico 4: Estados Digitales (Controladores)
# Las columnas ya vienen en 1 y 0, por lo que las graficamos directamente
axs[3].step(df['Tiempo'], df['luz_encendida'], label='Estado Luminarias', color='#FF8C00', where='post')
axs[3].step(df['Tiempo'], df['riego_pendiente'], label='Estado Riego', color='#00CED1', where='post')
axs[3].set_ylabel('Estado (1=ON, 0=OFF)')
axs[3].set_yticks([0, 1])
axs[3].legend(loc='upper right')
axs[3].grid(True, linestyle=':', alpha=0.7)

# 4. Ajustes finales de formato
plt.xlabel('Linea Temporal')
plt.xticks(rotation=45)
plt.tight_layout()

# Guardar la figura en alta resolucion para el informe de LaTeX
plt.savefig('graficos_telemetria_final.png', dpi=300, bbox_inches='tight')

# Mostrar el grafico en pantalla (opcional)
plt.show()