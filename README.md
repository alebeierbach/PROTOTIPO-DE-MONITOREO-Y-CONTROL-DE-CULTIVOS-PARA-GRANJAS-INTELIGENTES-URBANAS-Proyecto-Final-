# Prototipo de Monitoreo y Control de Cultivos para Granjas Inteligentes Urbanas 🌱

Proyecto Integrador presentado para la obtención del título de grado en **Ingeniería Electrónica** — Facultad de Ciencias Exactas, Físicas y Naturales, **Universidad Nacional de Córdoba (UNC)**.

Este trabajo, desarrollado en el marco de la línea de investigación del **LIADE** (Laboratorio de Investigación Aplicada y Desarrollo) sobre Agricultura Urbana y Periurbana (AUP), presenta el diseño, construcción y validación experimental de un prototipo de granja urbana vertical automatizada.

El sistema monitorea y controla de forma autónoma las principales variables ambientales del cultivo —temperatura, humedad relativa, humedad de sustrato e iluminación— mediante una Raspberry Pi 4 como unidad de procesamiento central, gestionando riego, iluminación LED y ventilación forzada para cultivos de **rúcula** y **espinaca** en sustrato.

> ⚠️ **El código final y estable del proyecto se encuentra en la carpeta [`VersionFinal_conWeb`](./VersionFinal_conWeb).**
> Las demás carpetas del repositorio corresponden a versiones previas, pruebas intermedias y scripts de análisis utilizados durante el desarrollo, y no reflejan necesariamente el estado final del sistema.

---

## 📋 Descripción general

El prototipo combina hardware de bajo costo con una arquitectura de software modular para lograr un sistema de cultivo automatizado, escalable y accesible para usuarios sin conocimientos técnicos avanzados. Entre sus características principales:

- **Adquisición de datos**: sensores de temperatura y humedad ambiente (DHT22), iluminancia (BH1750) y humedad de sustrato (sensor capacitivo + ADC PCF8591).
- **Actuación**: paneles LED de espectro completo, electrobomba y válvulas solenoides para riego localizado, y ventilación forzada — todos gobernados mediante relés de estado sólido (SSR) y electromecánicos.
- **Control automático**: lógica de umbral e histéresis para riego y ventilación, y un algoritmo de presupuesto acumulado para regular el fotoperíodo artificial en función del DLI (Integral Diaria de Luz) objetivo de cada cultivo.
- **Telemetría y monitoreo remoto**: envío periódico de datos a [ThingSpeak](https://thingspeak.com/) y una interfaz web local (Flask) para configuración y visualización remota de parámetros.
- **Registro histórico**: almacenamiento local en formato CSV de todas las variables medidas y el estado de los actuadores.

---

## 🗂️ Estructura del repositorio
├── VersionFinal_conWeb/ # ⭐ Código final y estable del prototipo
│ ├── models.py # Estructuras de configuración y estado del sistema
│ ├── config_loader.py # Carga y validación de config.toml
│ ├── hardware.py # Capa de abstracción de hardware (GPIO / I2C)
│ ├── control.py # Lógica de control (riego, ventilación, DLI)
│ ├── main.py # Ciclo de orquestación principal
│ ├── web.py # Servidor Flask de configuración remota
│ ├── templates/ # Plantillas HTML de la interfaz web
│ └── config.toml # Archivo de configuración externalizado
│
├── <versiones_previas>/ # Prototipos y pruebas anteriores
├── <analisis>/ # Scripts de análisis (ej. validación numérica DLI en MATLAB)
└── README.md

---

## ⚙️ Requisitos

- Raspberry Pi 4 Model B con Raspberry Pi OS.
- Python 3.x
- Bibliotecas principales: `Flask`, `Adafruit-Blinka` (soporte GPIO/I2C vía CircuitPython), entre otras.
- Cuenta de [ThingSpeak](https://thingspeak.com/) (opcional, para telemetría en la nube).
- [ngrok](https://ngrok.com/) (opcional, para exponer la interfaz web mediante túnel inverso).

```bash
pip install -r requirements.txt
```

---

## 🚀 Puesta en marcha

El sistema se ejecuta como tres servicios independientes de `systemd`, con arranque automático al energizar el equipo:

- `indoor_main.service` — ciclo de control principal (`main.py`)
- `indoor_web.service` — servidor de configuración web (`web.py`)
- `ngrok.service` — túnel de acceso remoto

```bash
sudo systemctl enable indoor_main.service indoor_web.service ngrok.service
sudo systemctl start indoor_main.service indoor_web.service ngrok.service
```

Los parámetros de operación (umbrales de humedad, DLI objetivo, tiempos de riego, etc.) se configuran en `config.toml`, editable directamente o mediante la interfaz web.

---

## 📊 Resultados

El prototipo fue validado experimentalmente durante varios meses de cultivo real, alcanzando un desarrollo vegetativo estable de ambos cultivos y un consumo energético eficiente gracias al bajo ciclo de trabajo de los actuadores de mayor potencia. El detalle completo de los ensayos, gráficos de telemetría y análisis de consumo se encuentra documentado en el informe final del Proyecto Integrador.

---

## 👥 Autoría y contexto institucional

Proyecto Integrador desarrollado en el marco del proyecto de investigación del LIADE: *"Granjas inteligentes para ciudades inteligentes y sostenibles. Desarrollos de la Industria 4.0 para la gestión de la agricultura urbana y periurbana (AUP) sostenible de ciudades inteligentes"*.

Presentado para la obtención del título de **Ingeniero/a Electrónico/a** — Facultad de Ciencias Exactas, Físicas y Naturales, Universidad Nacional de Córdoba (UNC).

<!-- AJUSTAR: agregar nombre del autor/es y año -->
**Autores:** [Ramirez, Valentin Jose y Beierbach, Alejo Adrian]
**Año:** [2026]

---

## 📄 Licencia

<!-- AJUSTAR: agregar licencia si corresponde, o quitar esta sección -->
