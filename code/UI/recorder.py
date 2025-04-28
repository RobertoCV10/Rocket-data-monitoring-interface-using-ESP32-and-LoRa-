import cv2
import os
import natsort
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

def seleccionar_carpeta():
    """Abre un diálogo para que el usuario seleccione una carpeta."""
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    carpeta_seleccionada = filedialog.askdirectory()
    return carpeta_seleccionada

def obtener_fps():
    """Abre un diálogo para que el usuario ingrese los FPS."""
    root = tk.Tk()
    root.withdraw()
    fps = simpledialog.askfloat("FPS del Video", "Introduce los fotogramas por segundo (ej. 30.0):", initialvalue=30.0)
    return fps

def obtener_nombre_video():
    """Abre un diálogo para que el usuario ingrese el nombre del video."""
    root = tk.Tk()
    root.withdraw()
    nombre = simpledialog.askstring("Nombre del Video", "Introduce el nombre para el archivo de video (ej. mi_video.avi):", initialvalue="video.avi")
    return nombre

def crear_video_ordenado(carpeta_imagenes, nombre_video="video.avi", fps=30.0):
    """
    Crea un video a partir de las imágenes en una carpeta, ordenadas alfabéticamente.

    Args:
        carpeta_imagenes (str): La ruta a la carpeta que contiene las imágenes.
        nombre_video (str, opcional): El nombre del archivo de video a crear. Por defecto es "video.avi".
        fps (float, opcional): Los fotogramas por segundo del video. Por defecto es 30.0.
    """
    imagenes = [f for f in os.listdir(carpeta_imagenes) if os.path.isfile(os.path.join(carpeta_imagenes, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    imagenes_ordenadas = natsort.natsorted(imagenes)

    if not imagenes_ordenadas:
        messagebox.showerror("Error", f"No se encontraron imágenes compatibles en la carpeta: {carpeta_imagenes}")
        return

    primera_imagen = cv2.imread(os.path.join(carpeta_imagenes, imagenes_ordenadas[0]))
    if primera_imagen is None:
        messagebox.showerror("Error", f"No se pudo leer la primera imagen en: {carpeta_imagenes}")
        return
    altura, ancho, capas = primera_imagen.shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(nombre_video, fourcc, fps, (ancho, altura))

    messagebox.showinfo("Progreso", "Creando video...")
    for imagen in imagenes_ordenadas:
        ruta_imagen = os.path.join(carpeta_imagenes, imagen)
        frame = cv2.imread(ruta_imagen)
        if frame is not None:
            video.write(frame)
        else:
            print(f"Advertencia: No se pudo leer la imagen {imagen}. Será omitida.")

    cv2.destroyAllWindows()
    video.release()
    messagebox.showinfo("Éxito", f"Video '{nombre_video}' creado exitosamente en la misma carpeta que las imágenes.")

if __name__ == "__main__":
    ruta_carpeta = seleccionar_carpeta()
    if ruta_carpeta:
        fps_deseados = obtener_fps()
        if fps_deseados is not None:
            nombre_archivo_video = obtener_nombre_video()
            if nombre_archivo_video:
                crear_video_ordenado(ruta_carpeta, nombre_archivo_video, fps_deseados)
            else:
                messagebox.showinfo("Información", "Se canceló la creación del video (nombre no proporcionado).")
        else:
            messagebox.showinfo("Información", "Se canceló la creación del video (FPS no proporcionados).")
    else:
        messagebox.showinfo("Información", "No se seleccionó ninguna carpeta. La creación del video se canceló.")