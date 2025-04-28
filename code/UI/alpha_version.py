import serial
import serial.tools.list_ports
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Variable global para la conexión serial
ser = None
buffer_recepcion = ""

# Diccionario para almacenar valores de sensores
sensores = {"A1": "", "A2": "", "A3": ""}

def leer_serial():
    global buffer_recepcion
    while ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"Datos recibidos: {data}")  # Imprime los datos para depuración
                data = data.replace("34\u0001", "")  # Omitir la combinación "34"
                if data:
                    buffer_recepcion += data  # Añadir los datos al buffer
                    procesar_buffer()  # Procesar el buffer
                    mostrar_mensaje(data, "izquierda")
        except Exception as e:
            mostrar_mensaje(f"Error leyendo datos: {e}", "izquierda")
            break

# Función para enviar datos al puerto serial
def enviar_comando():
    comando = entrada_comando.get()  # Obtener el comando desde la entrada
    if comando:
        if modo_hex.get():  # Si el modo hexadecimal está activado
            try:
                # Obtener MAC y Channel
                mac = entrada_mac.get().replace(" ", "")  # Eliminar espacios
                channel = entrada_channel.get().replace(" ", "")  # Eliminar espacios

                # Validar MAC y Channel
                if not mac or len(mac) != 4 or not all(c in "0123456789ABCDEFabcdef" for c in mac):
                    messagebox.showerror("Error", "MAC debe ser 2 valores hexadecimales (ejemplo: 31 32)")
                    return
                if not channel or len(channel) != 2 or not all(c in "0123456789ABCDEFabcdef" for c in channel):
                    messagebox.showerror("Error", "Channel debe ser 1 valor hexadecimal (ejemplo: 02)")
                    return

                # Combinar MAC, Channel y comando
                mensaje_completo = mac + channel + comando.replace(" ", "")
                bytes_comando = bytes.fromhex(mensaje_completo)  # Convertir a bytes hexadecimales
                ser.write(bytes_comando)  # Enviar bytes crudos
                mostrar_mensaje(mensaje_completo, "derecha")  # Mostrar en el lado derecho
            except ValueError as e:
                messagebox.showerror("Error", f"Formato hexadecimal inválido: {e}")
        else:  # Modo texto (ASCII)
            ser.write((comando + "\r\n").encode('ascii'))  # Enviar texto con CR/LF
            mostrar_mensaje(comando, "derecha")  # Mostrar en el lado derecho

        entrada_comando.delete(0, tk.END)  # Limpiar la entrada

# Función para validar la entrada en modo hexadecimal
def validar_hexa(texto):
    if not modo_hex.get():  # Si no está en modo hexadecimal, permitir cualquier texto
        return True

    # Permitir solo caracteres hexadecimales (0-9, A-F, a-f) y espacios
    caracteres_permitidos = set("0123456789ABCDEFabcdef ")
    return all(caracter in caracteres_permitidos for caracter in texto)

# Función para mostrar mensajes en el área de texto
def mostrar_mensaje(mensaje, lado):
    texto_recibido.config(state=tk.NORMAL)  # Habilitar la edición del área de texto

    # Configurar el color y la alineación según el lado
    if lado == "derecha":
        texto_recibido.tag_config("derecha", foreground="white", justify="right")
        texto_recibido.insert(tk.END, f"{mensaje}\n", "derecha")
    else:
        texto_recibido.tag_config("izquierda", foreground="white", justify="left")
        texto_recibido.insert(tk.END, f"{mensaje}\n", "izquierda")

    texto_recibido.config(state=tk.DISABLED)  # Deshabilitar la edición del área de texto
    texto_recibido.yview(tk.END)              # Desplazar al final

# Función para conectar al puerto serial
def conectar_serial():
    global ser
    puerto = combo_puertos.get()
    baudrate = combo_baudrates.get()

    try:
        ser = serial.Serial(
            port=puerto,
            baudrate=int(baudrate),
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        mostrar_mensaje(f"Conectado a {puerto} a {baudrate} baudios.", "izquierda")
        boton_conectar.config(state=tk.DISABLED)
        boton_desconectar.config(state=tk.NORMAL)
        entrada_comando.config(state=tk.NORMAL)
        boton_enviar.config(state=tk.NORMAL)

        # Iniciar hilo para leer datos
        hilo_lectura = threading.Thread(target=leer_serial, daemon=True)
        hilo_lectura.start()

    except serial.SerialException as e:
        messagebox.showerror("Error", f"No se pudo conectar: {e}")

# Función para desconectar el puerto serial
def desconectar_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
        mostrar_mensaje("Desconectado.", "izquierda")
        boton_conectar.config(state=tk.NORMAL)
        boton_desconectar.config(state=tk.DISABLED)
        entrada_comando.config(state=tk.DISABLED)
        boton_enviar.config(state=tk.DISABLED)

# Función para actualizar la lista de puertos COM
def actualizar_puertos():
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    combo_puertos['values'] = puertos
    if puertos:
        combo_puertos.current(0)
    else:
        combo_puertos.set("")

# Función para cerrar la aplicación
def cerrar_aplicacion():
    if ser and ser.is_open:
        ser.close()
    ventana.destroy()

# Función para procesar el buffer y extraer datos de sensores
def procesar_buffer():
    global buffer_recepcion
    while True:
        for sensor_id in sensores.keys():
            index = buffer_recepcion.find(sensor_id)
            if index != -1 and len(buffer_recepcion) > index + len(sensor_id):
                resto = buffer_recepcion[index + len(sensor_id):]
                valor = ""
                for char in resto:
                    if char.isdigit():
                        valor += char
                    else:
                        break
                sensores[sensor_id] = valor
                buffer_recepcion = buffer_recepcion.replace(sensor_id + valor, "")
                actualizar_sensores()
                break
        else:
            break

# Función para actualizar los valores en la interfaz
def actualizar_sensores():
    etiqueta_sensor1.config(text=f"Sensor 1: {sensores['A1']}")
    etiqueta_sensor2.config(text=f"Sensor 2: {sensores['A2']}")
    etiqueta_sensor3.config(text=f"Sensor 3: {sensores['A3']}")

# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("RobGam Didactics")

# Colores para la interfaz
COLOR_FONDO = "#27374D"
COLOR_PRIMARIO = "#1B1A55"
COLOR_SECUNDARIO = "#526D82"
COLOR_TEXTO = "#DDE6ED"

# Definir los estilos para los marcos
style = ttk.Style()

# Estilo para el LabelFrame del marco de configuración
style.configure("TFrame",
                background=COLOR_SECUNDARIO)  # Color de fondo del marco

ventana.configure(bg=COLOR_FONDO)

# Marco para la configuración del puerto y baudrate
marco_configuracion = ttk.LabelFrame(ventana, text="Configuración", style="TFrame")
marco_configuracion.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew" )

# Lista de puertos COM
ttk.Label(marco_configuracion, text="Puerto COM:", foreground=COLOR_TEXTO, background=COLOR_FONDO).grid(row=0, column=0, padx=5, pady=5)
combo_puertos = ttk.Combobox(marco_configuracion, width=15)
combo_puertos.grid(row=0, column=1, padx=5, pady=5)
actualizar_puertos()

# Botón para actualizar puertos
boton_actualizar = ttk.Button(marco_configuracion, text="Actualizar", command=actualizar_puertos, style="TButton")
boton_actualizar.grid(row=0, column=2, padx=5, pady=5)

# Lista de baudrates
ttk.Label(marco_configuracion, text="Baudrate:", foreground=COLOR_TEXTO, background=COLOR_FONDO).grid(row=1, column=0, padx=5, pady=5)
combo_baudrates = ttk.Combobox(marco_configuracion, width=15)
combo_baudrates['values'] = [9600, 115200]
combo_baudrates.current(0)
combo_baudrates.grid(row=1, column=1, padx=5, pady=5)

# Botones para conectar y desconectar
boton_conectar = ttk.Button(marco_configuracion, text="Conectar", command=conectar_serial, style="TButton")
boton_conectar.grid(row=1, column=2, padx=5, pady=5)

boton_desconectar = ttk.Button(marco_configuracion, text="Desconectar", command=desconectar_serial, state=tk.DISABLED, style="TButton")
boton_desconectar.grid(row=1, column=3, padx=5, pady=5)

# Opción para enviar en hexadecimal
modo_hex = tk.BooleanVar()
check_hex = ttk.Checkbutton(marco_configuracion, text="Enviar en HEX", variable=modo_hex, command=lambda: actualizar_modo_hex())
check_hex.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

# Campos para MAC y Channel
ttk.Label(marco_configuracion, text="MAC (2 valores HEX):").grid(row=3, column=0, padx=5, pady=5)
entrada_mac = ttk.Entry(marco_configuracion, width=15)
entrada_mac.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(marco_configuracion, text="Channel (1 valor HEX):").grid(row=4, column=0, padx=5, pady=5)
entrada_channel = ttk.Entry(marco_configuracion, width=15)
entrada_channel.grid(row=4, column=1, padx=5, pady=5)

# Función para actualizar el modo hexadecimal
def actualizar_modo_hex():
    if modo_hex.get():
        entrada_comando.config(validate="key", validatecommand=(ventana.register(validar_hexa), "%P"))
    else:
        entrada_comando.config(validate="none")

# Estilo para botones
style = ttk.Style()
style.configure("TButton", background=COLOR_PRIMARIO, foreground=COLOR_TEXTO)

# Área de texto para mostrar los mensajes
texto_recibido = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=60, height=20, state=tk.DISABLED, bg="#03001C", fg=COLOR_TEXTO)
texto_recibido.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Entrada para enviar comandos
entrada_comando = tk.Entry(ventana, width=50, state=tk.DISABLED, bg="#03001C", fg=COLOR_TEXTO)
entrada_comando.grid(row=2, column=0, padx=10, pady=10)

# Botón para enviar comandos
boton_enviar = tk.Button(ventana, text="Enviar", command=enviar_comando, state=tk.DISABLED, bg="#03001C", fg=COLOR_TEXTO)
boton_enviar.grid(row=2, column=1, padx=10, pady=10)

# Etiquetas de sensores
marco_sensores = ttk.LabelFrame(ventana, text="Lectura de Sensores", style="TFrame")
marco_sensores.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

etiqueta_sensor1 = ttk.Label(marco_sensores, text="Sensor 1: ", foreground=COLOR_TEXTO, background=COLOR_FONDO)
etiqueta_sensor1.grid(row=0, column=0, padx=5, pady=5)

etiqueta_sensor2 = ttk.Label(marco_sensores, text="Sensor 2: ", foreground=COLOR_TEXTO, background=COLOR_FONDO)
etiqueta_sensor2.grid(row=1, column=0, padx=5, pady=5)

etiqueta_sensor3 = ttk.Label(marco_sensores, text="Sensor 3: ", foreground=COLOR_TEXTO, background=COLOR_FONDO)
etiqueta_sensor3.grid(row=2, column=0, padx=5, pady=5)

# Configurar la acción al cerrar la ventana
ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

# Iniciar la interfaz gráfica
ventana.mainloop()
