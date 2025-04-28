import customtkinter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox # Importa tkinter messagebox
import tkinter as tk # Importa tkinter para usar el protocolo de cierre de ventana
import math
import webbrowser

def close_app(self):
    plt.close(self.fig)  # Cierra la figura de matplotlib
    self.destroy() #Destruye la ventana principal

def get_color(value, max_value, initial_color="green"):
    """Calcula un color entre initial_color y rojo basado en el valor,
    comenzando el cambio a rojo al 65% del valor máximo."""

    threshold = max_value * 0.65  # Umbral del 65% (ajustado)

    if value <= threshold:
        # Si el valor está por debajo del umbral, mantiene el color inicial
        if initial_color == "blue":
            return '#0000ff'  # Azul
        else:
            return '#00ff00'  # Verde (o el color inicial por defecto)
    else:
        # Si el valor está por encima del umbral, calcula el ratio para el cambio a rojo
        ratio = (value - threshold) / (max_value - threshold)
        red = int(255 * ratio)
        red = max(0, min(red, 255))  # Asegurar que red esté entre 0 y 255

        if initial_color == "blue":
            blue = 255 - red
            blue = max(0, min(blue, 255))  # Asegurar que blue esté entre 0 y 255
            return f'#{red:02x}00{blue:02x}'  # Azul a rojo
        else:
            green = 255 - red
            green = max(0, min(green, 255))  # Asegurar que green esté entre 0 y 255
            return f'#{red:02x}{green:02x}00'  # Verde a rojo

class GaugeChart(customtkinter.CTkFrame):
    def __init__(self, master, value, max_value, width=200, height=120, initial_color="green", **kwargs):
        super().__init__(master, **kwargs)
        self.initial_color = initial_color
        self.value = value
        self.max_value = max_value  # Almacenamos el valor máximo
        self.fixed_width = width
        self.fixed_height = height
        self.canvas = customtkinter.CTkCanvas(self, width=self.fixed_width, height=self.fixed_height, highlightthickness=0, bg="#242424")
        self.canvas.pack()
        self.draw_gauge()

        self.label = customtkinter.CTkLabel(self, text=str(self.value), font=("Arial", 36), text_color="white", bg_color="#242424")
        self.label.place(relx=0.5, rely=0.7, anchor="center")

        self.label_min = customtkinter.CTkLabel(self, text="0", font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_min.place(relx=0.05, rely=0.9, anchor="center")

        self.label_max = customtkinter.CTkLabel(self, text=str(self.max_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_max.place(relx=0.95, rely=0.9, anchor="center")

        # Calculamos las etiquetas de referencia proporcionalmente al valor máximo
        self.label_30 = customtkinter.CTkLabel(self, text=str(int(self.max_value * 0.25)), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_30.place(relx=0.12, rely=0.32, anchor="center")

        self.label_50 = customtkinter.CTkLabel(self, text=str(int(self.max_value * 0.5)), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_50.place(relx=0.5, rely=0.05, anchor="center")

        self.label_80 = customtkinter.CTkLabel(self, text=str(int(self.max_value * 0.75)), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_80.place(relx=0.88, rely=0.32, anchor="center")

    def draw_gauge(self):
        self.canvas.delete("gauge_arc")
        center_x = self.fixed_width / 2
        center_y = self.fixed_height * 0.8333
        radius = min(self.fixed_width, self.fixed_height) * 0.6
        start_angle = 180
        end_angle = 0

        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=start_angle, extent=end_angle - start_angle, outline="#3A3A3A", style="arc", width=10)

        value_angle = start_angle + (end_angle - start_angle) * (self.value / self.max_value)
        color = get_color(self.value, self.max_value, self.initial_color)

        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=start_angle, extent=value_angle - start_angle, outline=color, style="arc", width=10, tags="gauge_arc")

    def set_max_value(self, max_value):
        self.max_value = max_value
        self.label_max.configure(text=str(self.max_value))
        self.label_30.configure(text=str(int(self.max_value * 0.4)))
        self.label_80.configure(text=str(int(self.max_value * 0.7)))
        self.draw_gauge()

    def set_value(self, value):
        self.value = value
        self.label.configure(text=str(self.value))  # Actualiza la etiqueta del valor
        self.draw_gauge()

class QuarterGaugeChart(customtkinter.CTkFrame):
    def __init__(self, master, value, max_value, width=200, height=200, initial_color="green", **kwargs):
        super().__init__(master, **kwargs)
        self.initial_color = initial_color
        self.value = value
        self.max_value = max_value
        self.fixed_width = width
        self.fixed_height = height
        self.canvas = customtkinter.CTkCanvas(self, width=self.fixed_width, height=self.fixed_height, highlightthickness=0, bg="#242424")
        self.canvas.pack()
        self.draw_gauge()

        self.label = customtkinter.CTkLabel(self, text=str(self.value), font=("Arial", 36), text_color="white", bg_color="#242424")
        self.label.place(relx=0.6, rely=0.6, anchor="center")

        self.label_min = customtkinter.CTkLabel(self, text="0", font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_min.place(relx=0.27, rely=0.9, anchor="center")

        self.label_max = customtkinter.CTkLabel(self, text=str(self.max_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_max.place(relx=0.9, rely=0.1, anchor="center")

        self.label_50 = customtkinter.CTkLabel(self, text=str(int(self.max_value * 0.5)), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_50.place(relx=0.3, rely=0.22, anchor="center")

    def draw_gauge(self):
        self.canvas.delete("gauge_arc")
        center_x = self.fixed_width * 0.8
        center_y = self.fixed_height * 0.8
        radius = min(self.fixed_width, self.fixed_height) * 0.7
        start_angle = 180
        end_angle = 90

        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=start_angle, extent=end_angle - start_angle, outline="#3A3A3A", style="arc", width=10)

        value_angle = start_angle + (end_angle - start_angle) * (self.value / self.max_value)
        color = get_color(self.value, self.max_value, self.initial_color)

        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=start_angle, extent=value_angle - start_angle, outline=color, style="arc", width=10, tags="gauge_arc")

    def set_max_value(self, max_value):
        self.max_value = max_value
        self.label_max.configure(text=str(self.max_value))
        self.label_30.configure(text=str(int(self.max_value * 0.3)))
        self.label_80.configure(text=str(int(self.max_value * 0.8)))
        self.draw_gauge()

    def set_value(self, value):
        self.value = value
        self.label.configure(text=str(self.value))
        self.draw_gauge()

class SingleBarChart(customtkinter.CTkFrame):
    def __init__(self, master, value, min_value, max_value, label, width=200, height=150, initial_color="green", **kwargs):
        super().__init__(master, **kwargs)
        self.initial_color = initial_color
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.fixed_width = width
        self.fixed_height = height
        self.canvas = customtkinter.CTkCanvas(self, width=self.fixed_width, height=self.fixed_height, highlightthickness=0, bg="#242424")
        self.canvas.pack()
        self.draw_bar()

        self.label_min = customtkinter.CTkLabel(self, text=str(self.min_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_min.place(relx=0.1, rely=0.89, anchor="sw")

        self.label_max = customtkinter.CTkLabel(self, text=str(self.max_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_max.place(relx=0, rely=0.05, anchor="nw")

        self.label_text = customtkinter.CTkLabel(self, text=self.label, font=("Arial", 12), text_color="white", bg_color="#242424")
        self.label_text.place(relx=0.5, rely=1, anchor="s")

    def draw_bar(self):
        self.canvas.delete("bar")
        self.canvas.delete("value_text")

        bar_width = self.fixed_width * 0.4
        start_x = self.fixed_width * 0.3
        start_y = self.fixed_height * 0.85

        # Ajustamos la altura de la barra para que sea proporcional al rango de valores
        bar_height = ((self.value - self.min_value) / (self.max_value - self.min_value)) * self.fixed_height * 0.8
        x1 = start_x
        y1 = start_y
        x2 = x1 + bar_width 
        y2 = start_y - bar_height * 0.85

        color = get_color(self.value, self.max_value, self.initial_color)  # Calcula el color

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="bar")
        self.canvas.create_text(x1 + bar_width / 2, y2 - 10, text=str(self.value), fill="white", tags="value_text")

    def set_value(self, value):
        self.value = value
        self.draw_bar()

    def set_min_max_value(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.label_min.configure(text=str(self.min_value))
        self.label_max.configure(text=str(self.max_value))
        self.draw_bar()

class H_BarChart(customtkinter.CTkFrame):
    def __init__(self, master, value, min_value, max_value, label, width=200, height=150, initial_color="green", **kwargs):
        super().__init__(master, **kwargs)
        self.initial_color = initial_color
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.fixed_width = width
        self.fixed_height = height
        self.canvas = customtkinter.CTkCanvas(self, width=self.fixed_width, height=self.fixed_height, highlightthickness=0, bg="#242424")
        self.canvas.pack()
        self.draw_bar()

        self.label_min = customtkinter.CTkLabel(self, text=str(self.min_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_min.place(relx=0.05, rely=0.2, anchor="w")

        self.label_max = customtkinter.CTkLabel(self, text=str(self.max_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_max.place(relx=0.95, rely=0.2, anchor="e")

        self.label_text = customtkinter.CTkLabel(self, text=self.label, font=("Arial", 12), text_color="white", bg_color="#242424")
        self.label_text.place(relx=0.5, rely=0.9, anchor="s")

    def draw_bar(self):
        self.canvas.delete("bar")
        self.canvas.delete("value_text")

        bar_height = self.fixed_height * 0.5
        start_x = self.fixed_width * 0.05
        start_y = self.fixed_height * 0.25

        # Ajustamos el ancho de la barra para que sea proporcional al rango de valores
        bar_width = ((self.value - self.min_value) / (self.max_value - self.min_value)) * self.fixed_width * 0.8
        x1 = start_x
        y1 = start_y
        x2 = start_x + bar_width
        y2 = start_y + bar_height

        color = get_color(self.value, self.max_value, self.initial_color)  # Calcula el color

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="bar")
        self.canvas.create_text(x2 + 10, y1 + bar_height / 2, text=str(self.value), fill="white", anchor="w", tags="value_text")

    def set_value(self, value):
        self.value = value
        self.draw_bar()

    def set_min_max_value(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.label_min.configure(text=str(self.min_value))
        self.label_max.configure(text=str(self.max_value))
        self.draw_bar()

    def set_value(self, value):
        self.value = value
        self.draw_bar()

class BidirectionalBarChart(customtkinter.CTkFrame):
    def __init__(self, master, value, min_value, max_value, label, width=200, height=150, **kwargs):
        super().__init__(master, **kwargs)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.fixed_width = width
        self.fixed_height = height
        self.canvas = customtkinter.CTkCanvas(self, width=self.fixed_width, height=self.fixed_height, highlightthickness=0, bg="#242424")
        self.canvas.pack()
        self.draw_bar()

        self.label_min = customtkinter.CTkLabel(self, text=str(self.min_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_min.place(relx=0.05, rely=0.2, anchor="w")

        self.label_max = customtkinter.CTkLabel(self, text=str(self.max_value), font=("Arial", 12), text_color="gray", bg_color="#242424")
        self.label_max.place(relx=0.95, rely=0.2, anchor="e")

        self.label_text = customtkinter.CTkLabel(self, text=self.label, font=("Arial", 12), text_color="white", bg_color="#242424")
        self.label_text.place(relx=0.5, rely=0.9, anchor="s")

    def draw_bar(self):
        self.canvas.delete("bar")
        self.canvas.delete("value_text")

        bar_height = self.fixed_height * 0.5
        center_x = self.fixed_width / 2
        start_y = self.fixed_height * 0.25

        # Calcular el ancho de la barra proporcional al rango de valores
        total_range = self.max_value - self.min_value
        value_range = self.value - self.min_value
        bar_width = (value_range / total_range) * self.fixed_width

        if self.value > 0:
            x1 = center_x
            y1 = start_y
            x2 = center_x + (self.value / self.max_value) * (self.fixed_width / 2.6) #Correccion aqui
            y2 = start_y + bar_height
            text_x = x2 + 10
            text_anchor = "w"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#64B5F6", tags="bar")
            self.canvas.create_text(text_x, y1 + bar_height / 2, text=str(self.value), fill="white", anchor=text_anchor, tags="value_text")
        elif self.value < 0:
            x1 = center_x + (self.value / abs(self.min_value)) * (self.fixed_width / 2.6) #Correccion aqui
            y1 = start_y
            x2 = center_x
            y2 = start_y + bar_height
            text_x = x1 - 10
            text_anchor = "e"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#Ff0000", tags="bar")
            self.canvas.create_text(text_x, y1 + bar_height / 2, text=str(self.value), fill="white", anchor=text_anchor, tags="value_text")

        # Dibujar la línea central (cero)
        self.canvas.create_line(center_x, start_y, center_x, start_y + bar_height, fill="gray", width=2)

    def set_value(self, value):
        self.value = value
        self.draw_bar()

    def set_min_max_value(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.label_min.configure(text=str(self.min_value))
        self.label_max.configure(text=str(self.max_value))
        self.draw_bar()

class ThreeDGraph(customtkinter.CTkFrame):
    def __init__(self, master, figsize=(4, 3), **kwargs):  # Agrega figsize como parámetro
        super().__init__(master, **kwargs)
        self.fig = plt.figure(figsize=figsize)  # Usa el figsize proporcionado
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_rot = 0
        self.y_rot = 0
        self.z_rot = 0
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 2
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.draw_graph()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=customtkinter.TOP, fill=customtkinter.BOTH, expand=1)

    def draw_graph(self):
        self.ax.cla()
        x = np.linspace(-5, 5, 5)
        y = np.linspace(-5, 5, 5)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        self.ax.plot_surface(X, Y, Z, alpha=0.2, color='gray', rstride=1, cstride=1)

        self.ax.quiver(0, 0, 0, 5, 0, 0, color='red', arrow_length_ratio=0.1)
        self.ax.quiver(0, 0, 0, 0, 5, 0, color='green', arrow_length_ratio=0.1)
        self.ax.quiver(0, 0, 0, 0, 0, 5, color='blue', arrow_length_ratio=0.1)

        self.ax.set_xlabel('X', labelpad=1)
        self.ax.set_ylabel('Y', labelpad=1)
        self.ax.set_zlabel('Z', labelpad=1)

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])

        z = np.linspace(0, 4, 25)
        theta = np.linspace(0, 2 * np.pi, 8)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = 1 * np.cos(theta_grid)
        y_grid = 1 * np.sin(theta_grid)

        x_rotated, y_rotated, z_rotated = self.rotate_points(x_grid, y_grid, z_grid, self.x_rot, self.y_rot, self.z_rot)

        x_normalized, y_normalized, z_normalized = self.normalize_size(x_rotated, y_rotated, z_rotated)

        self.ax.plot_surface(x_normalized, y_normalized, z_normalized, alpha=0.3, color='red', rstride=1, cstride=1)
        self.canvas.draw()

    def rotate_points(self, x, y, z, x_rot, y_rot, z_rot):
        # Desplazar al punto de rotación
        x_shifted = x - self.rot_x
        y_shifted = y - self.rot_y
        z_shifted = z - self.rot_z

        Rx = np.array([[1, 0, 0], [0, np.cos(x_rot), -np.sin(x_rot)], [0, np.sin(x_rot), np.cos(x_rot)]])
        Ry = np.array([[np.cos(y_rot), 0, np.sin(y_rot)], [0, 1, 0], [-np.sin(y_rot), 0, np.cos(y_rot)]])
        Rz = np.array([[np.cos(z_rot), -np.sin(z_rot), 0], [np.sin(z_rot), np.cos(z_rot), 0], [0, 0, 1]])

        R = np.dot(Rz, np.dot(Ry, Rx))

        points = np.stack([x_shifted.flatten(), y_shifted.flatten(), z_shifted.flatten()])
        rotated_points = np.dot(R, points)

        # Desplazar de vuelta a la posición original
        x_rotated = rotated_points[0].reshape(x.shape) + self.rot_x
        y_rotated = rotated_points[1].reshape(y.shape) + self.rot_y
        z_rotated = rotated_points[2].reshape(z.shape) + self.rot_z

        return x_rotated, y_rotated, z_rotated

    def normalize_size(self, x, y, z):
        center_x = np.mean(x)
        center_y = np.mean(y)
        center_z = np.mean(z)

        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2 + (z - center_z)**2)
        average_distance = np.mean(distances)

        scale_factor = 2 / average_distance

        x_normalized = (x - center_x) * scale_factor + center_x
        y_normalized = (y - center_y) * scale_factor + center_y
        z_normalized = (z - center_z) * scale_factor + center_z

        return x_normalized, y_normalized, z_normalized

    def update_rotation(self, x, y, z):
        self.x_rot = math.radians(x)
        self.y_rot = math.radians(y)
        self.z_rot = math.radians(z)
        self.draw_graph()

class CoordenadasFrame(customtkinter.CTkFrame):
    def __init__(self, master, width=300, height=150, **kwargs):
        super().__init__(master, **kwargs)

        self.fixed_width = width
        self.fixed_height = height

        self.grid_columnconfigure(0, weight=1)  # Centra la columna 0
        self.grid_columnconfigure(1, weight=1)  # Centra la columna 1
        self.grid_rowconfigure(0, weight=1)     # Centra la fila 0
        self.grid_rowconfigure(1, weight=1)     # Centra la fila 1
        self.grid_rowconfigure(2, weight=1)     # Centra la fila 2

        self.latitud_label = customtkinter.CTkLabel(self, text="Latitud:", text_color="white")
        self.latitud_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")  # Alinea a la derecha

        self.latitud_entry = customtkinter.CTkEntry(self, width=int(self.fixed_width * 0.4))
        self.latitud_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")  # Alinea a la izquierda

        self.longitud_label = customtkinter.CTkLabel(self, text="Longitud:", text_color="white")
        self.longitud_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")  # Alinea a la derecha

        self.longitud_entry = customtkinter.CTkEntry(self, width=int(self.fixed_width * 0.4))
        self.longitud_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")  # Alinea a la izquierda

        self.buscar_button = customtkinter.CTkButton(self, text="Buscar Ubicación", command=self.buscar_ubicacion)
        self.buscar_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")  # Centra el botón

        self.configure(width=self.fixed_width, height=self.fixed_height)

    def buscar_ubicacion(self):
        try:
            latitud = float(self.latitud_entry.get())
            longitud = float(self.longitud_entry.get())
            if -90 <= latitud <= 90 and -180 <= longitud <= 180: #Validacion agregada
                url = f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"
                webbrowser.open_new_tab(url)
            else:
                tkinter.messagebox.showerror("Error", "Latitud debe estar entre -90 y 90, y longitud entre -180 y 180.")
        except ValueError:
            tkinter.messagebox.showerror("Error", "Ingresa coordenadas válidas.")
