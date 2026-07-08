import os
import re
from pathlib import Path
from faster_whisper import WhisperModel


def cargar_glosario(ruta_glosario: str) -> str:
    """
    Carga el glosario institucional para usarlo como contexto inicial del modelo.
    """

    ruta = Path(ruta_glosario)

    if not ruta.exists():
        return ""

    contenido = ruta.read_text(encoding="utf-8")

    return (
        "Contexto institucional de la Universidad de Costa Rica. "
        "Usar correctamente las siguientes siglas, códigos y nombres de unidades cuando aparezcan en el audio. "
        "Ejemplos: UCR significa Universidad de Costa Rica, ORI significa Oficina de Registro e Información. "
        "Glosario:\n"
        + contenido
    )


def cargar_diccionario_glosario(ruta_glosario: str) -> dict:
    """
    Convierte líneas tipo:
    IF | Escuela de Computación e Informática

    en un diccionario:
    {"IF": "Escuela de Computación e Informática"}
    """

    ruta = Path(ruta_glosario)

    if not ruta.exists():
        return {}

    diccionario = {}

    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()

        if not linea or "|" not in linea:
            continue

        sigla, nombre = linea.split("|", 1)

        sigla = sigla.strip()
        nombre = nombre.strip()

        if sigla and nombre:
            diccionario[sigla] = nombre

    return diccionario


def corregir_siglas_y_nombres(texto: str, glosario: dict) -> str:
    """
    Aplica correcciones básicas usando el glosario.
    Sirve para normalizar nombres completos y algunas siglas frecuentes.
    """

    # Correcciones manuales frecuentes detectadas en pruebas
    correcciones_manual = {
        "oori": "ORI",
        "o ori": "ORI",
        "orí": "ORI",
        "u c r": "UCR",
        "ucr": "UCR",
        "user e c c c": "UCR",
        "usere.c.c.c": "UCR",
        "ingreso.usere.c.c.c": "ingreso.ucr.ac.cr",
        "ingreso punto usere punto c punto c": "ingreso.ucr.ac.cr",
        "resinto": "recinto",
        "vecinto": "recinto",
        "vecintos": "recintos",
        "ex-regero": "extranjero",
        "ex regero": "extranjero",
        "cacilla": "casilla",
        "glazos": "plazos",
        "clavos": "claves",
    }

    for incorrecto, correcto in correcciones_manual.items():
        texto = re.sub(
            re.escape(incorrecto),
            correcto,
            texto,
            flags=re.IGNORECASE
        )

    # Si aparece el nombre completo de una unidad, puede agregar la sigla entre paréntesis.
    # Ejemplo: Escuela de Computación e Informática -> Escuela de Computación e Informática (IF)
    for sigla, nombre in glosario.items():
        patron_nombre = re.escape(nombre)

        if re.search(patron_nombre, texto, flags=re.IGNORECASE):
            texto = re.sub(
                patron_nombre,
                f"{nombre} ({sigla})",
                texto,
                flags=re.IGNORECASE
            )

    return texto


def transcribir_audio(
    ruta_audio: str,
    carpeta_salida: str = "outputs",
    ruta_glosario: str = "skills/meeting_transcriber/resources/glosario_ucr.txt"
) -> str:
    ruta_audio = Path(ruta_audio)

    if not ruta_audio.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_audio}")

    os.makedirs(carpeta_salida, exist_ok=True)

    print("Cargando glosario institucional...")
    prompt_inicial = cargar_glosario(ruta_glosario)
    glosario = cargar_diccionario_glosario(ruta_glosario)

    print("Cargando modelo de transcripción...")

    modelo = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        num_workers=1
    )

    print("Transcribiendo audio...")

    segmentos, info = modelo.transcribe(
        str(ruta_audio),
        language="es",
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
        initial_prompt=prompt_inicial
    )

    nombre_archivo = ruta_audio.stem
    ruta_salida = Path(carpeta_salida) / f"transcripcion_{nombre_archivo}.txt"

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        for segmento in segmentos:
            texto = segmento.text.strip()

            if texto:
                texto = corregir_siglas_y_nombres(texto, glosario)
                archivo.write(f"{segmento.start:.2f}|{segmento.end:.2f}|{texto}\n")

    print(f"Transcripción guardada en: {ruta_salida}")

    return str(ruta_salida)