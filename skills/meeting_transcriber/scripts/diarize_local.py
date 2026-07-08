import os
import tempfile
from pathlib import Path

import librosa
import numpy as np
from pydub import AudioSegment
from resemblyzer import VoiceEncoder
from sklearn.cluster import AgglomerativeClustering


def exportar_wav_mono_16k(ruta_audio: str) -> str:
    """
    Convierte el audio a WAV mono 16kHz para procesarlo localmente.
    """
    audio = AudioSegment.from_file(ruta_audio)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp.name, format="wav")

    return temp.name


def diarizar_audio_local(
    ruta_audio: str,
    carpeta_salida: str = "outputs",
    num_participantes: int = 2,
    duracion_ventana: float = 4.0
) -> str:
    """
    Diarización local aproximada.
    Divide el audio en ventanas, genera embeddings de voz y agrupa voces similares.
    No usa internet ni tokens.

    Importante:
    Esta versión NO recorta silencios, para mantener alineados los tiempos
    con la transcripción generada por Whisper.
    """

    ruta_audio = Path(ruta_audio)

    if not ruta_audio.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_audio}")

    os.makedirs(carpeta_salida, exist_ok=True)

    print("Preparando audio para diarización local...")
    ruta_wav = exportar_wav_mono_16k(str(ruta_audio))

    print("Cargando codificador de voz local...")
    encoder = VoiceEncoder()

    print("Cargando audio sin recortar silencios...")
    wav, sample_rate = librosa.load(ruta_wav, sr=16000, mono=True)

    total_segundos = len(wav) / sample_rate
    muestras_por_ventana = int(duracion_ventana * sample_rate)

    embeddings = []
    ventanas = []

    print(f"Duración detectada del audio: {total_segundos:.2f} segundos")
    print("Analizando voces por ventanas...")

    inicio_muestra = 0

    while inicio_muestra < len(wav):
        fin_muestra = min(inicio_muestra + muestras_por_ventana, len(wav))

        fragmento = wav[inicio_muestra:fin_muestra]

        inicio_seg = inicio_muestra / sample_rate
        fin_seg = fin_muestra / sample_rate

        # Ignorar ventanas extremadamente cortas
        if len(fragmento) < sample_rate:
            break

        # Evita analizar silencios muy fuertes, pero conserva el tiempo global
        if np.max(np.abs(fragmento)) > 0.01:
            embedding = encoder.embed_utterance(fragmento)

            embeddings.append(embedding)
            ventanas.append({
                "inicio": inicio_seg,
                "fin": fin_seg
            })

        inicio_muestra = fin_muestra

    if not embeddings:
        raise ValueError("No se detectó voz suficiente para diarizar.")

    embeddings = np.array(embeddings)

    if len(embeddings) < num_participantes:
        num_participantes = max(1, len(embeddings))

    print(f"Agrupando voces en {num_participantes} participante(s)...")

    clustering = AgglomerativeClustering(n_clusters=num_participantes)
    etiquetas = clustering.fit_predict(embeddings)

    nombre_archivo = ruta_audio.stem
    ruta_salida = Path(carpeta_salida) / f"diarizacion_local_{nombre_archivo}.txt"

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        for ventana, etiqueta in zip(ventanas, etiquetas):
            participante = f"Participante {etiqueta + 1}"
            archivo.write(
                f"{ventana['inicio']:.2f}|{ventana['fin']:.2f}|{participante}\n"
            )

    try:
        os.remove(ruta_wav)
    except OSError:
        pass

    print(f"Diarización local guardada en: {ruta_salida}")

    return str(ruta_salida)