import customtkinter
import tkinter as tk
import tkinter.messagebox
from tkinter import scrolledtext
import threading
import matplotlib.pyplot as plt
from widgets import GaugeChart, QuarterGaugeChart, SingleBarChart, H_BarChart, BidirectionalBarChart, ThreeDGraph, CoordenadasFrame
import time
import random
import serial
import serial.tools.list_ports
from PIL import Image

class WidgetFactory:
    @staticmethod
    def crear_gauge_chart(master, max_value=1024, width=200, height=120, initial_color="green"):
        return GaugeChart(master, value=0, max_value=max_value, width=width, height=height, initial_color=initial_color, fg_color="#242424")

    @staticmethod
    def crear_quarter_gauge_chart(master, max_value=1024, width=200, height=200, initial_color="green"):
        return QuarterGaugeChart(master, value=0, max_value=max_value, width=width, height=height, initial_color=initial_color, fg_color="#242424")

    @staticmethod
    def crear_single_bar_chart(master, max_value=1024, width=200, height=150, initial_color="green"):
        return SingleBarChart(master, value=0, min_value=0, max_value=max_value, label="Valor Vertical", width=width, height=height, initial_color=initial_color, fg_color="#242424")

    @staticmethod
    def crear_h_bar_chart(master, max_value=876, width=200, height=150, initial_color="green"):
        return H_BarChart(master, value=50, min_value=0, max_value=max_value, label="Valor Horizontal", width=width, height=height, initial_color=initial_color, fg_color="#242424")

    @staticmethod
    def crear_bidirectional_bar_chart(master, min_value=-255, max_value=255, width=200, height=150):
        return BidirectionalBarChart(master, value=0, min_value=min_value, max_value=max_value, label="Valor Bidireccional", width=width, height=height, fg_color="#242424")

    @staticmethod
    def crear_three_d_graph(master, figsize=(2, 1.5)):
        return ThreeDGraph(master, figsize=figsize, fg_color="#242424")

    @staticmethod
    def crear_coordenadas_frame(master, width=300, height=150):
        return CoordenadasFrame(master, width=width, height=height, fg_color="#3A3A3A")

    @staticmethod
    def crear_close_button(master):
        return customtkinter.CTkButton(master, text="Cerrar")

class WidgetContainer:
    def __init__(self, master, widget_type, sensor_id=None, **kwargs):
        self.widget_type = widget_type
        self.kwargs = kwargs
        self.sensor_id = sensor_id  # Añadir el sensor_id
        self.create_widget(master)

    def create_widget(self, master):
        if self.widget_type == "gauge":
            self.widget = WidgetFactory.crear_gauge_chart(master, **self.kwargs)
        elif self.widget_type == "quarter_gauge":
            self.widget = WidgetFactory.crear_quarter_gauge_chart(master, **self.kwargs)
        elif self.widget_type == "bar":
            self.widget = WidgetFactory.crear_single_bar_chart(master, **self.kwargs)
        elif self.widget_type == "hbar":
            self.widget = WidgetFactory.crear_h_bar_chart(master, **self.kwargs)
        elif self.widget_type == "bidirectional":
            self.widget = WidgetFactory.crear_bidirectional_bar_chart(master, **self.kwargs)
        elif self.widget_type == "3d":
            self.widget = WidgetFactory.crear_three_d_graph(master, **self.kwargs)
        elif self.widget_type == "coordenadas":
            self.widget = WidgetFactory.crear_coordenadas_frame(master, **self.kwargs)

    def get_widget(self):
        return self.widget

    def update_widget(self, value):
        if hasattr(self.widget, "set_value"):
            self.widget.set_value(value)

class Dashboard(customtkinter.CTk):
    WINDOW_TITLE = "Modular Dashboard"
    PADDING = 5
    UPDATE_INTERVAL = 100
    BORDER_COLOR = "#555555"
    BORDER_WIDTH = 2
    GRID_ROWS = 5
    GRID_COLS = 4
    HEADER_FOOTER_HEIGHT = 100

    def __init__(self):
        super().__init__()
        self.configure(bg="#2c3e50")
        self.title(self.WINDOW_TITLE)
        
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.grid_frames = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        self.widgets = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        self.delete_buttons = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]  # Botones de eliminación
        self.serial_buffer = ""  # Inicializar el búfer serial
        self.create_header()
        self.create_grid()
        self.create_footer()
        self.start_ui_update()
        self.sensor_mapping = {}  # Inicializar sensor_mapping aquí

        self.menu_button = None
        self.submenu_frame = None
        self.delete_mode = False  # Modo de eliminación activado/desactivado
        self.delete_button_submenu = None  # Referencia al botón "Eliminar" en el submenú
        self.delete_button_original_fg_color = None  # Guardar color original
        self.delete_button_original_hover_color = None # Guardar color original hover

    def create_header(self):
        self.header_frame = customtkinter.CTkFrame(self, border_color=self.BORDER_COLOR, border_width=self.BORDER_WIDTH, fg_color="#3A3A3A")
        self.header_frame.grid(row=0, column=0, columnspan=self.GRID_COLS, padx=self.PADDING, pady=self.PADDING, sticky="nsew")
        self.header_frame.configure(height=self.HEADER_FOOTER_HEIGHT)
        self.header_frame.grid_propagate(False)

        self.menu_button = customtkinter.CTkButton(self.header_frame, text="Menú", command=self.toggle_submenu, corner_radius=10)
        self.menu_button.pack(side="left", padx=10, pady=5)

        # Cargar y mostrar el PNG
        try:
            image = customtkinter.CTkImage(Image.open("icon.png"), size=(300, 50))  # Ajusta el tamaño según sea necesario
            image_label = customtkinter.CTkLabel(self.header_frame, image=image, text="")
            image_label.pack(side="right", padx=7, pady=5)
        except FileNotFoundError:
            print("Error: No se encontró la imagen 'tu_imagen.png'")

    def toggle_submenu(self):
        if self.submenu_frame:
            self.submenu_frame.destroy()
            self.submenu_frame = None
        else:
            self.submenu_frame = customtkinter.CTkFrame(self.header_frame, fg_color="#2c3e50")
            self.submenu_frame.pack(side="left", padx=5, pady=5)

            self.delete_button_submenu = customtkinter.CTkButton(self.submenu_frame, text="Eliminar", command=self.toggle_delete_mode, corner_radius=5, width=80, height=25)
            self.delete_button_submenu.pack(pady=5)
            self.delete_button_original_fg_color = self.delete_button_submenu.cget("fg_color") # Obtener color original
            self.delete_button_original_hover_color = self.delete_button_submenu.cget("hover_color") # Obtener color original hover

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            print("Modo de eliminación activado")
            self.delete_button_submenu.configure(text="Aplicar", fg_color="green", hover_color="#006400")
            for row in range(1, self.GRID_ROWS - 1):
                for col in range(self.GRID_COLS):
                    if self.widgets[row][col]:
                        self.create_delete_button(row, col)
        else:
            print("Modo de eliminación desactivado")
            self.delete_button_submenu.configure(text="Eliminar", fg_color=self.delete_button_original_fg_color, hover_color=self.delete_button_original_hover_color) # Restaurar color original
            for row in range(1, self.GRID_ROWS - 1):
                for col in range(self.GRID_COLS):
                    self.destroy_delete_button(row, col)

    def create_delete_button(self, row, col):
        button = customtkinter.CTkButton(self.grid_frames[row][col], text="X", command=lambda r=row, c=col: self.delete_graph(r, c), width=20, height=20, corner_radius=3, fg_color="red", hover_color="#8B0000")
        button.place(relx=0.95, rely=0.05, anchor="ne")  # Posición en la esquina superior derecha
        self.delete_buttons[row][col] = button

    def destroy_delete_button(self, row, col):
        if self.delete_buttons[row][col]:
            self.delete_buttons[row][col].destroy()
            self.delete_buttons[row][col] = None

    def delete_graph(self, row, col):
        if self.delete_mode and self.widgets[row][col]:
            self.widgets[row][col].get_widget().destroy()
            self.widgets[row][col] = None
            self.destroy_delete_button(row, col)
            print(f"Gráfico eliminado en ({row}, {col})")


    def create_grid(self):
        for row in range(1, self.GRID_ROWS - 1):
            for col in range(self.GRID_COLS):
                frame = customtkinter.CTkFrame(self, border_color=self.BORDER_COLOR, border_width=self.BORDER_WIDTH, fg_color="#2c3e50")
                frame.grid(row=row, column=col, padx=self.PADDING, pady=self.PADDING, sticky="nsew")
                frame.bind("<Button-1>", lambda event, r=row, c=col: self.on_grid_click(r, c))
                self.grid_frames[row][col] = frame

    def create_footer(self):
        self.footer_frame = customtkinter.CTkFrame(self, border_color=self.BORDER_COLOR, border_width=self.BORDER_WIDTH, fg_color="#3A3A3A")
        self.footer_frame.grid(row=self.GRID_ROWS - 1, column=0, columnspan=self.GRID_COLS, padx=self.PADDING, pady=self.PADDING, sticky="nsew")
        self.footer_frame.configure(height=150)  # Aumentar la altura del pie de página

        # Parte Izquierda
        left_frame = customtkinter.CTkFrame(self.footer_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=10, pady=5)

        com_frame = customtkinter.CTkFrame(left_frame, fg_color="transparent")
        com_frame.pack(pady=5)

        com_label = customtkinter.CTkLabel(com_frame, text="COM:")
        com_label.pack(side="left")

        self.com_var = tk.StringVar()
        self.com_menu = customtkinter.CTkOptionMenu(com_frame, variable=self.com_var, values=self.get_available_com_ports())
        self.com_menu.pack(side="left")

        baud_frame = customtkinter.CTkFrame(left_frame, fg_color="transparent")
        baud_frame.pack(pady=5)

        baud_label = customtkinter.CTkLabel(baud_frame, text="Baudios:")
        baud_label.pack(side="left")

        self.baud_var = tk.IntVar(value=9600)  # Valor predeterminado: 9600
        baud_values = [9600, 115200, 38400, 57600]  # Velocidades de baudios más comunes
        # Convertir los valores a cadenas
        baud_values_str = [str(baud) for baud in baud_values]
        self.baud_menu = customtkinter.CTkOptionMenu(baud_frame, variable=self.baud_var, values=baud_values_str)
        self.baud_menu.pack(side="left")

        com_buttons_frame = customtkinter.CTkFrame(left_frame, fg_color="transparent")
        com_buttons_frame.pack(pady=5)

        connect_button = customtkinter.CTkButton(com_buttons_frame, text="Conectar", command=self.connect_com)
        connect_button.pack(side="left", padx=5)

        update_button = customtkinter.CTkButton(com_buttons_frame, text="Actualizar", command=self.update_com_list)
        update_button.pack(side="left", padx=5)

        # Parte Central (Chat Serial)
        center_frame = customtkinter.CTkFrame(self.footer_frame, fg_color="transparent")
        center_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        serial_frame = customtkinter.CTkFrame(center_frame, fg_color="transparent")
        serial_frame.pack(fill="x", expand=True)

        # Área de texto para mostrar los mensajes
        self.chat_text = scrolledtext.ScrolledText(serial_frame, wrap=tk.WORD, height=5)
        self.chat_text.pack(fill="x", expand=True)
        self.chat_text.config(state=tk.DISABLED)

        # Configurar etiquetas (tags) para los mensajes
        self.chat_text.tag_config("derecha", foreground="blue", justify="right")
        self.chat_text.tag_config("izquierda", foreground="green", justify="left")

        serial_input_frame = customtkinter.CTkFrame(center_frame, fg_color="transparent")
        serial_input_frame.pack(fill="x", expand=True)

        self.serial_input = customtkinter.CTkEntry(serial_input_frame, state=tk.DISABLED) # Deshabilitar entrada al inicio
        self.serial_input.pack(side="left", fill="x", expand=True, pady=6)

        self.send_button = customtkinter.CTkButton(serial_input_frame, text="Enviar", command=self.send_serial_data, state=tk.DISABLED) # Deshabilitar botón al inicio
        self.send_button.pack(side="left", padx=5)

        # Botón de desconexión
        self.disconnect_button = customtkinter.CTkButton(serial_input_frame, text="Desconectar", command=self.disconnect_com, state=tk.DISABLED)
        self.disconnect_button.pack(side="left", padx=5)

        # Parte Derecha
        right_frame = customtkinter.CTkFrame(self.footer_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=5)

        debugger_frame = customtkinter.CTkFrame(right_frame, fg_color="transparent")
        debugger_frame.pack(pady=5)

        debugger_label = customtkinter.CTkLabel(debugger_frame, text="Debugger:")
        debugger_label.pack()

        self.debugger_text = tk.Text(debugger_frame, height=5, width=30)
        self.debugger_text.pack()

    def get_available_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device + (" - " + port.description if port.description else "") for port in ports]

    def update_com_list(self):
        self.com_menu.configure(values=self.get_available_com_ports())

    def send_serial_data(self):
        command = self.serial_input.get()
        if command:
            self.ser.write((command + "\r\n").encode('ascii'))
            self.display_message(command, "derecha")
            self.serial_input.delete(0, tk.END)

    def receive_serial_data(self, data):
        if data:
            print(f"Datos recibidos: {data}")  # Depuración
            self.display_message(data, "izquierda")

    def display_message(self, message, side):
        self.chat_text.config(state=tk.NORMAL)
        if side == "derecha":
            self.chat_text.insert(tk.END, f"{message}\n", "derecha")
        else:
            self.chat_text.insert(tk.END, f"{message}\n", "izquierda")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.yview(tk.END)
        self.update_idletasks()  # Forzar la actualización de la interfaz gráfica

    def read_serial_data(self):
            if hasattr(self, 'ser') and self.ser.is_open:
                try:
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
                        self.serial_buffer += data
                        if '\n' in self.serial_buffer:
                            lines = self.serial_buffer.split('\n')
                            for line in lines[:-1]:
                                line = line.strip()
                                if "L2-" in line:
                                    self.process_sensor_data(line) #procesar datos de sensores
                                else:
                                    self.receive_serial_data(line) #mostrar mensaje en crudo
                            self.serial_buffer = lines[-1]
                except serial.SerialException as e:
                    self.debugger_text.insert(tk.END, f"Error al leer datos seriales: {e}\n")
            self.after(100, self.read_serial_data)

    def process_sensor_data(self, data):
            sensor_pairs = data.split('\t')
            for pair in sensor_pairs:
                pair = pair.strip()
                if "S" in pair:
                    sensor_id = None
                    value = None
                    try:
                        # Eliminar "L2-" y dividir por ":" o "="
                        pair = pair.replace("L2-", "").replace("L2 ", "")
                        if ":" in pair:
                            parts = pair.split(":")
                        elif "=" in pair:
                            parts = pair.split("=")
                        else:
                            print(f"Formato desconocido: {pair}")
                            continue

                        if len(parts) == 2:
                            sensor_part, value_str = parts
                            sensor_part = sensor_part.strip()
                            value_str = value_str.strip()

                            # Extraer el sensor ID (S seguido de dígitos)
                            import re
                            match = re.search(r'S\d+', sensor_part)
                            if match:
                                sensor_id = match.group(0)

                            try:
                                value = float(value_str)
                            except ValueError:
                                print(f"Error al convertir el valor: {value_str} en {pair}")
                        else:
                            print(f"Formato incorrecto: {pair}")
                    except Exception as e:
                        print(f"Error al procesar: {pair} - {e}")

                    if sensor_id is not None and value is not None:
                        print(f"Sensor ID: {sensor_id}, Value: {value}")
                        try:
                            int_value = int(value)
                            for row in range(1, self.GRID_ROWS - 1):
                                for col in range(self.GRID_COLS):
                                    if self.widgets[row][col] and self.widgets[row][col].sensor_id == sensor_id:
                                        self.widgets[row][col].update_widget(int_value)
                                        if sensor_id == "S9":  # Si es S9, actualizar la rotación
                                            if hasattr(self.widgets[row][col].get_widget(), "update_rotation"):
                                                self.widgets[row][col].get_widget().update_rotation(0, value, 0)  # Usar 'value' para la rotación en Y
                        except ValueError:
                            print(f"Error al convertir a entero para el widget: {value}")
                elif "GPS no responde" not in pair and pair.strip():
                    self.receive_serial_data(pair)
                                
    def connect_com(self):
        com_port = self.com_var.get().split(" - ")[0]  # Obtener solo el nombre del puerto
        baud_rate = self.baud_var.get()  # Obtener la velocidad en baudios seleccionada
        try:
            self.ser = serial.Serial(com_port, baud_rate)  # Ajusta la velocidad en baudios según sea necesario
            self.debugger_text.insert(tk.END, f"Conectado a {com_port}\n")
        except serial.SerialException as e:
            self.debugger_text.insert(tk.END, f"Error al conectar: {e}\n")
        if hasattr(self, 'ser') and self.ser.is_open:
            self.read_serial_data()
            self.serial_input.configure(state=tk.NORMAL)  # Habilitar entrada
            self.send_button.configure(state=tk.NORMAL) # Habilitar botón "Enviar"
            self.disconnect_button.configure(state=tk.NORMAL) # Habilitar botón "Desconectar"

    def disconnect_com(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.debugger_text.insert(tk.END, "Puerto serial desconectado.\n")
        self.serial_input.configure(state=tk.DISABLED) # Deshabilitar entrada
        self.send_button.configure(state=tk.DISABLED) # Deshabilitar botón "Enviar"
        self.disconnect_button.configure(state=tk.DISABLED) # Deshabilitar botón "Desconectar"

    def on_grid_click(self, row, col):
        if not self.delete_mode:  # Verificar si el modo de eliminación está desactivado
            dialog = WidgetSelectionDialog(self, row, col)
            dialog.mainloop()
        else:
            print("No se pueden añadir widgets en modo de eliminación")

    def add_widget(self, widget_type, master, row, col, **kwargs):
            if self.widgets[row][col]:
                self.widgets[row][col].get_widget().destroy()

            sensor_id = None  # Inicializar sensor_id
            sensor_name = kwargs.pop("sensor", None)  # Extraer 'sensor' de kwargs y eliminarlo

            if sensor_name:
                sensor_id = self.get_sensor_id(sensor_name)  # Obtener el ID del sensor
                self.sensor_mapping[sensor_id] = (row, col)  # Mapear el sensor al widget

            widget_container = WidgetContainer(master, widget_type, sensor_id=sensor_id, **kwargs)  # Pasar sensor_id
            self.widgets[row][col] = widget_container
            widget = widget_container.get_widget()
            widget.pack(padx=self.PADDING, pady=self.PADDING, fill="both", expand=True)

    def get_sensor_id(self, sensor_name):
            sensor_mapping = {
                "Sensor 1": "S1",
                "Sensor 2": "S2",
                "Sensor 3": "S3",
                "Sensor 4": "S4",
                "Sensor 5": "S5",
                "Sensor 6": "S6",
                "Sensor 7": "S7",
                "Sensor 8": "S8",
                "Sensor 9": "S9",
                "Sensor 10": "S10"
            }
            return sensor_mapping.get(sensor_name)

    def start_ui_update(self):
        self.after(self.UPDATE_INTERVAL, self.update_ui)

    def update_ui(self):
        self.after(self.UPDATE_INTERVAL, self.update_ui)

class WidgetSelectionDialog(customtkinter.CTkToplevel):
    def __init__(self, master, row, col):
        super().__init__(master)
        self.master = master # Guardar una referencia a master
        self.row = row
        self.col = col
        self.title("Seleccionar Widget")
        self.geometry("300x250")

        self.geometry(f"+{master.winfo_rootx() + master.winfo_width()//2 - self.winfo_reqwidth()//2}+{master.winfo_rooty() + master.winfo_height()//2 - self.winfo_reqheight()//2}") # Centrar ventana
        self.transient(master)  # Ventana hija de master
        self.grab_set()  # Bloquear interacción con master
        self.focus_set()  # Dar foco a la ventana
        self.sensor_var = tk.StringVar()  # Variable para el sensor seleccionado
        self.sensor_mapping = {}  # Diccionario para mapear sensores a nombres

        self.widget_var = tk.StringVar(value="gauge")
        self.color_var = tk.StringVar(value="green")
        self.max_value_var = tk.StringVar(value="1024")
        self.min_value_var = tk.StringVar(value="-1024")

        self.create_widgets()
        self.update_options()

    def create_widgets(self):
        widget_label = customtkinter.CTkLabel(self, text="Widget:")
        widget_label.pack(pady=5)
        widget_menu = customtkinter.CTkOptionMenu(self, variable=self.widget_var, values=["gauge", "quarter_gauge", "bar", "hbar", "bidirectional", "3d", "coordenadas"], command=self.update_options)
        widget_menu.pack(pady=5)

        self.sensor_frame = customtkinter.CTkFrame(self)
        self.sensor_frame.pack(pady=5)
        sensor_label = customtkinter.CTkLabel(self.sensor_frame, text="Sensor:")
        sensor_label.pack(side="left")
        sensor_names = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5", "Sensor 6", "Sensor 7", "Sensor 8", "Sensor 9"]
        self.sensor_menu = customtkinter.CTkOptionMenu(self.sensor_frame, variable=self.sensor_var, values=sensor_names)
        self.sensor_menu.pack(side="left")

        self.max_value_frame = customtkinter.CTkFrame(self)
        self.max_value_frame.pack(pady=5)
        max_value_label = customtkinter.CTkLabel(self.max_value_frame, text="Valor Máximo:")
        max_value_label.pack(side="left")
        self.max_value_entry = customtkinter.CTkEntry(self.max_value_frame, textvariable=self.max_value_var)
        self.max_value_entry.pack(side="left")

        self.min_value_frame = customtkinter.CTkFrame(self)
        self.min_value_frame.pack(pady=5)
        min_value_label = customtkinter.CTkLabel(self.min_value_frame, text="Valor Mínimo:")
        min_value_label.pack(side="left")
        self.min_value_entry = customtkinter.CTkEntry(self.min_value_frame, textvariable=self.min_value_var)
        self.min_value_entry.pack(side="left")

        self.color_frame = customtkinter.CTkFrame(self)
        self.color_frame.pack(pady=5)
        color_label = customtkinter.CTkLabel(self.color_frame, text="Color:")
        color_label.pack(side="left")
        self.color_menu = customtkinter.CTkOptionMenu(self.color_frame, variable=self.color_var, values=["green", "blue"])
        self.color_menu.pack(side="left")

        confirm_button = customtkinter.CTkButton(self, text="Confirmar", command=self.confirm_selection)
        confirm_button.pack(pady=10)

    def update_options(self, event=None):
        widget_type = self.widget_var.get()
        if widget_type == "3d":
            self.sensor_menu.configure(values=["Sensor 9"])
            self.sensor_frame.pack(pady=5)
        elif widget_type == "coordenadas":
            self.sensor_menu.configure(values=["Sensor 10"])
            self.sensor_frame.pack(pady=5)
        else:
            self.sensor_menu.configure(values=["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5", "Sensor 6", "Sensor 7", "Sensor 8"])
            self.sensor_frame.pack(pady=5)

        if widget_type == "bidirectional":
            self.color_frame.pack_forget()
            self.max_value_frame.pack(pady=5)
            self.min_value_frame.pack(pady=5)
        elif widget_type == "3d":
            self.color_frame.pack_forget()
            self.max_value_frame.pack_forget()
            self.min_value_frame.pack_forget()
        elif widget_type == "coordenadas":
            self.color_frame.pack_forget()
            self.max_value_frame.pack_forget()
            self.min_value_frame.pack_forget()
        else:
            self.color_frame.pack(pady=5)
            self.max_value_frame.pack(pady=5)
            self.min_value_frame.pack_forget()

    def confirm_selection(self):
        widget_type = self.widget_var.get()
        selected_sensor = self.sensor_var.get()  # Obtener el sensor seleccionado

        if widget_type == "3d":
            self.master.add_widget(widget_type, self.master.grid_frames[self.row][self.col], self.row, self.col, sensor=selected_sensor)
        else:
            if widget_type == "bidirectional":
                try:
                    max_value = int(self.max_value_var.get())
                    min_value = -abs(int(self.min_value_var.get()))
                    self.master.add_widget(widget_type, self.master.grid_frames[self.row][self.col], self.row, self.col, max_value=max_value, min_value=min_value, sensor=selected_sensor)
                except ValueError:
                    print("Error: Los valores máximo y mínimo deben ser enteros.")
            elif widget_type == "coordenadas":
                self.master.add_widget(widget_type, self.master.grid_frames[self.row][self.col], self.row, self.col, sensor=selected_sensor)
            else:
                try:
                    color = self.color_var.get()
                    max_value = int(self.max_value_var.get())
                    self.master.add_widget(widget_type, self.master.grid_frames[self.row][self.col], self.row, self.col, max_value=max_value, initial_color=color, sensor=selected_sensor)
                except ValueError:
                    print("Error: El valor máximo debe ser un entero.")
        self.destroy()

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()