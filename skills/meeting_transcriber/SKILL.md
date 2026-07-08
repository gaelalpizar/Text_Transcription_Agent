---
name: meeting-transcriber
description: Extrae transcripciones de grabaciones de reuniones en formato de audio o video. Se activa cuando el usuario solicita transcribir, resumir o analizar una reunión grabada.
version: 1.0.0
tools:
  - python
---

# Meeting Transcriber Skill

## Objetivo

Esta Skill permite procesar grabaciones de reuniones para obtener una transcripción textual con identificación aproximada de participantes.

## Cuándo usar esta Skill

Usar esta Skill cuando el usuario solicite:

- Transcribir una grabación de reunión.
- Convertir audio hablado a texto.
- Obtener el contenido textual de una reunión grabada.
- Extraer posibles acuerdos o ideas importantes.

## Flujo de trabajo

1. Recibir la ruta de un archivo de audio.
2. Cargar el modelo de transcripción.
3. Procesar el audio.
4. Guardar la transcripción en la carpeta outputs.
5. Identificar los participantes en la transcripción.
6. Guardar la transcripción con participantes en la carpeta outputs.

## Entradas esperadas

- Archivos .mp3, .wav, .m4a o similares.

## Salidas esperadas

- transcripcion_nombrearchivo.txt
- diarizacion_local_nombrearchivo.txt
- transcripcion_con_participantes_nombrearchivo.txt

## Scripts principales

- scripts/transcribe.py
- scripts/summarize.py