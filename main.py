from skills.meeting_transcriber.scripts.transcribe import transcribir_audio
from skills.meeting_transcriber.scripts.diarize_local import diarizar_audio_local
from skills.meeting_transcriber.scripts.merge_transcript_diarization import generar_transcripcion_con_participantes


def pedir_entero(mensaje: str, valor_default: int) -> int:
    valor = input(mensaje)

    if not valor.strip():
        return valor_default

    try:
        valor = int(valor)

        if valor <= 0:
            return valor_default

        return valor

    except ValueError:
        return valor_default


def pedir_decimal(mensaje: str, valor_default: float) -> float:
    valor = input(mensaje)

    if not valor.strip():
        return valor_default

    try:
        valor = float(valor)

        if valor <= 0:
            return valor_default

        return valor

    except ValueError:
        return valor_default


def main():
    print("======================================")
    print(" Agente de IA - Transcriptor de Reuniones")
    print("======================================\n")

    ruta_audio = input("Ingrese la ruta del archivo de audio: ")

    num_participantes = pedir_entero(
        "Ingrese la cantidad aproximada de participantes [default: 2]: ",
        2
    )

    duracion_ventana = pedir_decimal(
        "Ingrese la duración de ventana en segundos [default: 6.0]: ",
        6.0
    )

    try:
        print("\nConfiguración seleccionada:")
        print(f"Participantes aproximados: {num_participantes}")
        print(f"Duración de ventana: {duracion_ventana} segundos")

        print("\n1. Transcribiendo audio...")
        ruta_transcripcion = transcribir_audio(ruta_audio)

        print("\n2. Identificando participantes localmente...")
        ruta_diarizacion = diarizar_audio_local(
            ruta_audio,
            num_participantes=num_participantes,
            duracion_ventana=duracion_ventana
        )

        print("\n3. Generando transcripción con participantes...")
        ruta_final = generar_transcripcion_con_participantes(
            ruta_transcripcion,
            ruta_diarizacion
        )

        print("\nProceso finalizado correctamente.")
        print(f"Transcripción base: {ruta_transcripcion}")
        print(f"Diarización local: {ruta_diarizacion}")
        print(f"Transcripción con participantes: {ruta_final}")

    except Exception as error:
        print("\nOcurrió un error:")
        print(error)


if __name__ == "__main__":
    main()