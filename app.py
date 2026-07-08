import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from skills.meeting_transcriber.scripts.transcribe import transcribir_audio
from skills.meeting_transcriber.scripts.diarize_local import diarizar_audio_local
from skills.meeting_transcriber.scripts.merge_transcript_diarization import (
    generar_transcripcion_con_participantes,
)


class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente de IA - Transcriptor de Reuniones")
        self.root.geometry("900x680")
        self.root.resizable(False, False)

        self.ruta_audio = tk.StringVar()
        self.estado = tk.StringVar(value="Seleccione un archivo de audio para comenzar.")

        self.num_participantes = tk.StringVar(value="2")
        self.duracion_ventana = tk.StringVar(value="6.0")
        self.incluir_timestamps = tk.BooleanVar(value=True)

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = tk.Label(
            self.root,
            text="Agente de IA para Transcripción de Reuniones",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=15)

        descripcion = tk.Label(
            self.root,
            text="Seleccione una grabación para generar una transcripción con participantes.",
            font=("Arial", 11)
        )
        descripcion.pack(pady=5)

        frame_archivo = tk.Frame(self.root)
        frame_archivo.pack(pady=15)

        entrada_archivo = tk.Entry(
            frame_archivo,
            textvariable=self.ruta_audio,
            width=80,
            font=("Arial", 10)
        )
        entrada_archivo.grid(row=0, column=0, padx=5)

        boton_buscar = tk.Button(
            frame_archivo,
            text="Buscar audio",
            command=self.seleccionar_archivo,
            width=15
        )
        boton_buscar.grid(row=0, column=1, padx=5)

        frame_configuracion = tk.LabelFrame(
            self.root,
            text="Configuración de participantes",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        frame_configuracion.pack(pady=10)

        etiqueta_participantes = tk.Label(
            frame_configuracion,
            text="Cantidad aproximada de participantes:",
            font=("Arial", 10)
        )
        etiqueta_participantes.grid(row=0, column=0, padx=8, pady=5, sticky="e")

        entrada_participantes = tk.Entry(
            frame_configuracion,
            textvariable=self.num_participantes,
            width=10,
            font=("Arial", 10)
        )
        entrada_participantes.grid(row=0, column=1, padx=8, pady=5)

        etiqueta_ventana = tk.Label(
            frame_configuracion,
            text="Duración de ventana en segundos:",
            font=("Arial", 10)
        )
        etiqueta_ventana.grid(row=0, column=2, padx=8, pady=5, sticky="e")

        entrada_ventana = tk.Entry(
            frame_configuracion,
            textvariable=self.duracion_ventana,
            width=10,
            font=("Arial", 10)
        )
        entrada_ventana.grid(row=0, column=3, padx=8, pady=5)

        ayuda = tk.Label(
            frame_configuracion,
            text="Guía: 1-3 participantes = 6 a 8s | 4-8 participantes = 4 a 6s | 9+ participantes = 3 a 4s",
            font=("Arial", 9),
            fg="gray"
        )
        ayuda.grid(row=1, column=0, columnspan=4, pady=5)

        check_timestamps = tk.Checkbutton(
            frame_configuracion,
            text="Incluir lapsos de tiempo en la transcripción final",
            variable=self.incluir_timestamps,
            font=("Arial", 10)
        )
        check_timestamps.grid(row=2, column=0, columnspan=4, pady=5)

        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        self.boton_transcribir = tk.Button(
            frame_botones,
            text="Iniciar transcripción",
            command=self.iniciar_transcripcion,
            width=22,
            height=2
        )
        self.boton_transcribir.grid(row=0, column=0, padx=10)

        boton_outputs = tk.Button(
            frame_botones,
            text="Abrir outputs",
            command=self.abrir_outputs,
            width=22,
            height=2
        )
        boton_outputs.grid(row=0, column=1, padx=10)

        etiqueta_estado = tk.Label(
            self.root,
            textvariable=self.estado,
            font=("Arial", 10, "italic"),
            wraplength=850
        )
        etiqueta_estado.pack(pady=10)

        self.caja_texto = scrolledtext.ScrolledText(
            self.root,
            width=105,
            height=22,
            font=("Arial", 10)
        )
        self.caja_texto.pack(pady=10)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar grabación de reunión",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.m4a *.flac"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            self.ruta_audio.set(archivo)
            self.estado.set("Archivo seleccionado. Puede iniciar la transcripción.")

    def obtener_configuracion(self):
        try:
            participantes = int(self.num_participantes.get())

            if participantes <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Valor inválido",
                "La cantidad de participantes debe ser un número entero mayor que 0."
            )
            return None

        try:
            ventana = float(self.duracion_ventana.get())

            if ventana <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Valor inválido",
                "La duración de ventana debe ser un número mayor que 0."
            )
            return None

        return participantes, ventana

    def iniciar_transcripcion(self):
        ruta = self.ruta_audio.get()

        if not ruta:
            messagebox.showwarning(
                "Archivo requerido",
                "Debe seleccionar un archivo de audio."
            )
            return

        configuracion = self.obtener_configuracion()

        if configuracion is None:
            return

        participantes, ventana = configuracion

        incluir_tiempos = self.incluir_timestamps.get()

        self.boton_transcribir.config(state="disabled")
        self.estado.set("Procesando audio... Esto puede tardar varios minutos.")
        self.caja_texto.delete("1.0", tk.END)

        hilo = threading.Thread(
            target=self.procesar_audio,
            args=(ruta, participantes, ventana, incluir_tiempos),
            daemon=True
        )
        hilo.start()

    def procesar_audio(self, ruta, participantes, ventana, incluir_tiempos):
        try:
            self.actualizar_estado("1/3 Transcribiendo audio...")
            ruta_transcripcion = transcribir_audio(ruta)

            self.actualizar_estado("2/3 Identificando participantes localmente...")
            ruta_diarizacion = diarizar_audio_local(
                ruta,
                num_participantes=participantes,
                duracion_ventana=ventana
            )

            self.actualizar_estado("3/3 Generando transcripción con participantes...")
            ruta_final = generar_transcripcion_con_participantes(
                ruta_transcripcion,
                ruta_diarizacion,
                incluir_timestamps=incluir_tiempos
            )

            with open(ruta_final, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

            self.root.after(0, self.mostrar_resultado, contenido)

            self.actualizar_estado(
                f"Proceso finalizado. Transcripción con participantes: {ruta_final}"
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Proceso finalizado",
                    "La transcripción con participantes fue generada correctamente."
                )
            )

        except Exception as error:
            self.actualizar_estado("Ocurrió un error durante el procesamiento.")
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(error))
            )

        finally:
            self.root.after(
                0,
                lambda: self.boton_transcribir.config(state="normal")
            )

    def actualizar_estado(self, mensaje):
        self.root.after(0, lambda: self.estado.set(mensaje))

    def mostrar_resultado(self, contenido):
        self.caja_texto.delete("1.0", tk.END)
        self.caja_texto.insert(tk.END, contenido)

    def abrir_outputs(self):
        carpeta_outputs = os.path.abspath("outputs")
        os.makedirs(carpeta_outputs, exist_ok=True)
        os.startfile(carpeta_outputs)


if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptorApp(root)
    root.mainloop()