# Agente de IA para Transcripción de Reuniones

Este proyecto implementa un agente de IA capaz de extraer transcripciones a partir de grabaciones de reuniones.

## Objetivo

Automatizar el proceso de documentación de reuniones mediante la transcripción automática de audio y la generación de un resumen básico.

## Tecnologías utilizadas

* Python 3.12
* VS Code
* PowerShell
* faster-whisper
* pydub
* Hugging Face Hub

## Requisitos previos

Antes de ejecutar el proyecto, fue necesario contar con las siguientes herramientas instaladas:

### 1. Python oficial de Windows

Se utilizó **Python 3.12** instalado desde la página oficial de Python.

Es importante utilizar el Python oficial de Windows y no el Python incluido en entornos como MSYS2, ya que este puede generar errores al instalar dependencias como `numba`, `numpy`, `lxml` o `cmake`.

Para verificar las versiones instaladas de Python, se puede ejecutar:

```powershell
py -0p
```

En este proyecto se utilizó:

```powershell
py -3.12
```

### 2. Visual Studio Code

El desarrollo se realizó en **VS Code**, utilizando su terminal integrada con PowerShell.

### 3. PowerShell

Se utilizó PowerShell para crear el entorno virtual, activar el proyecto e instalar las dependencias.

### 4. Entorno virtual de Python

El proyecto debe ejecutarse dentro de un entorno virtual para aislar las dependencias.

Creación del entorno virtual:

```powershell
py -3.12 -m venv venv
```

Activación del entorno virtual:

```powershell
.\venv\Scripts\activate
```

Después de activarlo, debe aparecer algo similar a:

```text
(venv)
```

### 5. Verificación del intérprete de Python

Para confirmar que el proyecto no está usando Python de MSYS2, se puede ejecutar:

```powershell
python -c "import sys; print(sys.executable)"
```

La salida debe apuntar al entorno virtual del proyecto, por ejemplo:

```text
C:\Users\gaela\Desktop\agente-transcriptor\venv\Scripts\python.exe
```

No debe aparecer una ruta como:

```text
C:\msys64\ucrt64\bin\python.exe
```

## Estructura del proyecto

```text
agente-transcriptor-reuniones/
├── main.py
├── requirements.txt
├── README.md
├── recordings/
├── outputs/
└── skills/
    └── meeting_transcriber/
        ├── SKILL.md
        ├── scripts/
        │   ├── __init__.py
        │   ├── transcribe.py
        │   └── summarize.py
        └── resources/
            └── prompt_resumen.txt
```

## Instalación de dependencias

Con el entorno virtual activado, se actualizan las herramientas de instalación:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

Luego se instalan las dependencias del proyecto:

```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install resemblyzer --no-deps
```

El archivo `requirements.txt` contiene:

```text
faster-whisper
pydub
```

## Consideraciones sobre el modelo de IA

Este proyecto utiliza `faster-whisper`, una implementación optimizada del modelo Whisper para transcripción automática de audio.

La primera vez que se ejecuta el programa, el modelo se descarga desde Hugging Face. Por eso puede aparecer una advertencia indicando que se están realizando solicitudes no autenticadas al Hugging Face Hub. Esta advertencia no impide el funcionamiento del proyecto.

Después de la primera descarga, el modelo queda almacenado en caché localmente en la computadora.

## Privacidad de la información

El audio se procesa localmente en la computadora del usuario. La grabación se coloca en la carpeta `recordings/` y la transcripción generada se guarda en la carpeta `outputs/`.

En esta versión del proyecto no se utiliza una API externa para transcribir el audio. Por lo tanto, el contenido de la reunión no se envía a un servicio externo para ser procesado.

## Funcionamiento

1. El usuario coloca una grabación en la carpeta `recordings/`.
2. Ejecuta el agente desde la terminal.
3. El agente carga el modelo de transcripción.
4. Se procesa el audio usando `faster-whisper`.
5. Se genera un archivo de transcripción en la carpeta `outputs/`.
6. Se genera un resumen básico en la carpeta `outputs/`.

## Ejecución

Con el entorno virtual activado, se ejecuta:

```powershell
python app.py
```

Luego se ingresa la ruta del archivo de audio, por ejemplo:

```text
recordings/reunion1.mp3
```

## Salidas generadas

El sistema genera archivos como:

```text
outputs/transcripcion_reunion1.txt
outputs/resumen_reunion1.txt
```

## Notas de rendimiento

El tiempo de procesamiento depende del tamaño del archivo de audio y de los recursos de la computadora.

Para audios grandes, como grabaciones de reuniones de muchos minutos o archivos pesados, la transcripción puede tardar varios minutos si se ejecuta únicamente con CPU.

Para mejorar el rendimiento se configuró el modelo con parámetros como:

```python
cpu_threads=4
compute_type="int8"
beam_size=1
vad_filter=True
```

Esto permite reducir el consumo de recursos y acelerar la transcripción en comparación con configuraciones más pesadas.

## Problemas encontrados durante la instalación

Durante el desarrollo se identificó que el uso de Python desde MSYS2 podía causar errores al instalar dependencias, especialmente con paquetes como `numba`, `numpy`, `cmake` y `lxml`.

Por esta razón, se decidió utilizar Python 3.12 oficial de Windows y `faster-whisper` en lugar de `openai-whisper`, evitando así conflictos con `numba`.

## Relación con Skills

El proyecto se organizó siguiendo el enfoque de Skills, donde una capacidad del agente se separa en una estructura modular con instrucciones, scripts, recursos y dependencias.

La Skill principal del proyecto se llama `meeting_transcriber` y se encarga de procesar grabaciones de reuniones para generar transcripciones y resúmenes básicos.

El archivo `SKILL.md` funciona como manifiesto de la Skill, indicando su objetivo, cuándo debe usarse, sus entradas esperadas, salidas generadas y scripts principales.
