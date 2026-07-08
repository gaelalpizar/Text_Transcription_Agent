from pathlib import Path


def segundos_a_timestamp(segundos: float) -> str:
    segundos = int(segundos)
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60

    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


def leer_transcripcion(ruta_transcripcion: str):
    segmentos = []

    with open(ruta_transcripcion, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea:
                continue

            partes = linea.split("|", 2)

            if len(partes) != 3:
                continue

            inicio, fin, texto = partes

            segmentos.append({
                "inicio": float(inicio),
                "fin": float(fin),
                "texto": texto
            })

    return segmentos


def leer_diarizacion_local(ruta_diarizacion: str):
    segmentos = []

    with open(ruta_diarizacion, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea:
                continue

            partes = linea.split("|", 2)

            if len(partes) != 3:
                continue

            inicio, fin, participante = partes

            segmentos.append({
                "inicio": float(inicio),
                "fin": float(fin),
                "participante": participante
            })

    return segmentos


def obtener_participante_para_segmento(segmento_texto, segmentos_hablantes):
    mejor_participante = "Participante desconocido"
    mayor_traslape = 0

    inicio_texto = segmento_texto["inicio"]
    fin_texto = segmento_texto["fin"]
    centro_texto = (inicio_texto + fin_texto) / 2

    for segmento_hablante in segmentos_hablantes:
        inicio = max(inicio_texto, segmento_hablante["inicio"])
        fin = min(fin_texto, segmento_hablante["fin"])

        traslape = max(0, fin - inicio)

        if traslape > mayor_traslape:
            mayor_traslape = traslape
            mejor_participante = segmento_hablante["participante"]

    if mayor_traslape > 0:
        return mejor_participante

    menor_distancia = float("inf")

    for segmento_hablante in segmentos_hablantes:
        centro_hablante = (segmento_hablante["inicio"] + segmento_hablante["fin"]) / 2
        distancia = abs(centro_texto - centro_hablante)

        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_participante = segmento_hablante["participante"]

    return mejor_participante


def suavizar_bloques(bloques, duracion_minima=8.0):
    """
    Une bloques muy cortos con el bloque anterior o siguiente.
    Esto evita cambios falsos de participante por ruido, pausas o variaciones de tono.
    """

    if len(bloques) <= 1:
        return bloques

    bloques_suavizados = []

    for bloque in bloques:
        duracion = bloque["fin"] - bloque["inicio"]

        if (
            duracion < duracion_minima
            and bloques_suavizados
        ):
            # Unir bloque corto con el anterior
            bloques_suavizados[-1]["fin"] = bloque["fin"]
            bloques_suavizados[-1]["textos"].extend(bloque["textos"])
        else:
            bloques_suavizados.append(bloque)

    return bloques_suavizados


def generar_transcripcion_con_participantes(
    ruta_transcripcion: str,
    ruta_diarizacion: str,
    carpeta_salida: str = "outputs",
    incluir_timestamps: bool = True
) -> str:
    transcripcion = leer_transcripcion(ruta_transcripcion)
    diarizacion = leer_diarizacion_local(ruta_diarizacion)

    ruta_transcripcion = Path(ruta_transcripcion)
    nombre_base = ruta_transcripcion.stem.replace("transcripcion_", "")

    ruta_salida = Path(carpeta_salida) / f"transcripcion_con_participantes_{nombre_base}.txt"

    bloques = []

    participante_actual = None
    inicio_bloque = None
    fin_bloque = None
    textos_bloque = []

    for segmento in transcripcion:
        participante = obtener_participante_para_segmento(segmento, diarizacion)

        if participante != participante_actual:
            if participante_actual is not None:
                bloques.append({
                    "inicio": inicio_bloque,
                    "fin": fin_bloque,
                    "participante": participante_actual,
                    "textos": textos_bloque
                })

            participante_actual = participante
            inicio_bloque = segmento["inicio"]
            textos_bloque = []

        fin_bloque = segmento["fin"]
        textos_bloque.append(segmento["texto"])

    if participante_actual is not None:
        bloques.append({
            "inicio": inicio_bloque,
            "fin": fin_bloque,
            "participante": participante_actual,
            "textos": textos_bloque
        })

    bloques = suavizar_bloques(bloques, duracion_minima=8.0)

    lineas_finales = []

    for bloque in bloques:
        texto = " ".join(bloque["textos"])

        if incluir_timestamps:
            inicio_txt = segundos_a_timestamp(bloque["inicio"])
            fin_txt = segundos_a_timestamp(bloque["fin"])

            linea = f"[{inicio_txt} - {fin_txt}] {bloque['participante']}: {texto}"
        else:
            linea = f"{bloque['participante']}: {texto}"

        lineas_finales.append(linea)

    ruta_salida.write_text("\n".join(lineas_finales), encoding="utf-8")

    print(f"Transcripción con participantes guardada en: {ruta_salida}")

    return str(ruta_salida)