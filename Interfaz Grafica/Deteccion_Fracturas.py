#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil 
from tkinter import Canvas
from datetime import datetime
import PIL
from PIL import Image
from PIL import ImageTk
from PIL import Image as PILImage, ImageDraw
import torch
from ultralytics import YOLO


# In[2]:


import cv2
import numpy as np
from matplotlib import pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output


# In[3]:


#DETECTAR DISPOSITIVO
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
#CARGA DEL MODELO ENTRENADO
modelo_yolo = YOLO("model.pt") 
modelo_yolo.to(device)


# In[4]:


from aspose.imaging import Image as AsposeImage
from aspose.imaging.fileformats.png import *
from aspose.imaging.imageoptions import *
# Función para convertir imágenes
def convert_dicom_to_png(input_dicom, output_png):
    with AsposeImage.load(input_dicom) as image:
        image.save(str(output_png), PngOptions())


# In[5]:


def realizar_prediccion(imagen_path, extension):
    results = modelo_yolo.predict(imagen_path)
    fracture_detected = False
    confidence = 0

    img = PILImage.open(imagen_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # Calcular grosor dinámico basado en el tamaño de la imagen
    width, height = img.size
    thickness = max(2, min(width, height) // 200) - 5  # Ajuste automático del grosor

    # Dibujar bounding boxes
    for result in results[0].boxes:
        confidence = result.conf[0].item() * 100
        fracture_detected = True
        x1, y1, x2, y2 = map(int, result.xyxy[0]) 

        # Dibujar cuadro punteado
        dash_length = max(5, thickness * 2) 
        for x in range(x1, x2, dash_length * 2):
            draw.line([(x, y1), (min(x + dash_length, x2), y1)], fill="red", width=thickness)
            draw.line([(x, y2), (min(x + dash_length, x2), y2)], fill="red", width=thickness)
        for y in range(y1, y2, dash_length * 2):
            draw.line([(x1, y), (x1, min(y + dash_length, y2))], fill="red", width=thickness)
            draw.line([(x2, y), (x2, min(y + dash_length, y2))], fill="red", width=thickness)

    path_new_image = imagen_path.replace(f".{extension}", f"_prediccion.{extension}")
    img.save(path_new_image)

    return path_new_image, fracture_detected, confidence


# In[ ]:





# In[6]:


#Funciones de procesamiento de imagen
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))

def zoom_image(image, zoom_factor):
    (h, w) = image.shape[:2]
    new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

def adjust_contrast(image, alpha=1.0, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def cv_to_tk(image_cv):
    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    return ImageTk.PhotoImage(pil_img)


# In[ ]:





# In[7]:


def move_to_directory(filepath, target_directory="converted_images"):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    new_path = os.path.join(target_directory, os.path.basename(filepath))
    shutil.move(filepath, new_path)
    return new_path


# In[8]:


def revision_rapida(root):
    file_path = filedialog.askopenfilename(
    filetypes=[
        ("Archivos DICOM", "*.dcm"),
        ("Imágenes JPG", "*.jpg"),
        ("Imágenes PNG", "*.png"),
        ("Todos los archivos permitidos", "*.dcm *.jpg *.png"),
        ]
    )
    if not file_path:
        return

    if file_path:     
                    _, extension = os.path.splitext(file_path)  
                    extension = extension.lower()  
                    if extension == ".dcm":
                        output_png = os.path.join("converted_images", "rapida.png")
                        convert_dicom_to_png(file_path, output_png)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(output_png, "dcm")
                    elif extension == ".png":
                        output_png = os.path.join("converted_images", "rapida.png")
                        shutil.copy(file_path, output_png)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(output_png,"png")
                    else:                                              
                        output_png = os.path.join("converted_images", "rapida.jpg")
                        shutil.copy(file_path, output_png)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(output_png,"jpg")
                    
    resultado_texto = "Fractura detectada" if fractura_detectada else "No se detectó fractura"
    messagebox.showinfo("Resultado", resultado_texto)
    mostrar_imagen(nueva_imagen_path,fractura_detectada,confidence,root)


# In[9]:


# Agregar Paciente
def agregar_paciente(root):
    
    def guardar_lista_pacientes(pacientes):

        with open("pacientes.txt", "w") as archivo:
            for paciente in pacientes:
                linea = ", ".join(
                    f"{key}: {', '.join(value) if key == 'Imagen' else str(value)}"
                    for key, value in paciente.items()
                )
                archivo.write(linea + "\n")

    
    def guardar_paciente(datos_paciente, imagen):
            
            #Guarda los datos del paciente y la imagen asociada en el archivo pacientes.txt.            
            pacientes = cargar_pacientes()
            imagen_nueva = os.path.basename(imagen)
                 
            for paciente in pacientes:
                if paciente["Nombre"] == datos_paciente["Nombre"] and paciente["Apellido"] == datos_paciente["Apellido"]:
                    
                    imagenes_actuales = paciente.get("Imagen", "").split(",") if paciente.get("Imagen") else []
                    if imagen_nueva not in imagenes_actuales:
                        imagenes_actuales.append(imagen_nueva)
                        paciente["Imagen"] = ",".join(imagenes_actuales)               
                    guardar_lista_pacientes(pacientes)
                    messagebox.showinfo("Información", "Nueva imagen asociada al paciente.")
               
                    return

        
            now = datetime.now()
            fecha_actual = f"{now.day}//{now.month}//{now.year}"
            datos_paciente["Fecha"] = fecha_actual
            datos_paciente["Imagen"] = imagen
        
            with open("pacientes.txt", "a") as file:
                for key, value in datos_paciente.items():
          
                        file.write(f"{key}: {value}\n")
          
                file.write("\n")


    def guardar_datos():
        # Recoger los datos del formulario
        datos_paciente = {
            "Nombre": entry_nombre.get(),
            "Apellido": entry_apellido.get(),
            "Edad": entry_edad.get(),
            "Sexo": combo_sexo.get(),
        }

        # Verificar si faltan datos
        if not all(datos_paciente.values()):
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        # Muestra el diálogo para cargar un archivo DICOM

        # Definir los tipos de archivos permitidos
        archivo_dicom = filedialog.askopenfilename(
            filetypes=[
                ("Archivos DICOM", "*.dcm"),
                ("Imágenes JPG", "*.jpg"),
                ("Imágenes PNG", "*.png"),
                ("Todos los archivos permitidos", "*.dcm *.jpg *.png"),
            ]
        )
        if archivo_dicom:
        
                    _, extension = os.path.splitext(archivo_dicom) 
                    extension = extension.lower()  

                    if extension == ".dcm":

                        # Convertir el archivo DICOM a PNG
                        nombre_imagen = os.path.basename(archivo_dicom).replace(".dcm", ".png")
                        nombre_imagen = datos_paciente["Nombre"] + datos_paciente["Apellido"] + nombre_imagen
                        ruta_salida = os.path.join("converted_images", nombre_imagen)
                        convert_dicom_to_png(archivo_dicom, ruta_salida)
                        # Realizar predicción
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(ruta_salida,"dicom")
                        name =nombre_imagen[0:-4] + '_prediccion' + '.png'
                        # Guarda los datos del paciente con la imagen asociada
                        datos_paciente["Prob"] = confidence
                        guardar_paciente(datos_paciente, name)
        
                    elif extension == '.png':
                        nombre_imagen = os.path.basename(archivo_dicom)
                        nombre_imagen = datos_paciente["Nombre"] + datos_paciente["Apellido"] + nombre_imagen
                        ruta_salida = os.path.join("converted_images", nombre_imagen)
                        shutil.copy(archivo_dicom, ruta_salida)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(ruta_salida,"png")
                        name =nombre_imagen[0:-4] + "_prediccion.png"
                        #Guarda los datos del paciente con la imagen asociada
                        datos_paciente["Prob"] = confidence
                        guardar_paciente(datos_paciente, name)
                    else:
                        nombre_imagen = os.path.basename(archivo_dicom)
                        nombre_imagen = datos_paciente["Nombre"] + datos_paciente["Apellido"] + nombre_imagen
                        ruta_salida = os.path.join("converted_images", nombre_imagen)
                        shutil.copy(archivo_dicom, ruta_salida)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(ruta_salida,"jpg")
                        name =nombre_imagen[0:-4] + "_prediccion.jpg"
                        # Guarda los datos del paciente con la imagen asociada
                        datos_paciente["Prob"] = confidence
                        guardar_paciente(datos_paciente, name)
                        
                    # Mostrar resultados
                    resultado_texto = "Fractura detectada" if fractura_detectada else "No se detectó fractura"
                    messagebox.showinfo("Resultado", f"Paciente guardado.\n{resultado_texto}")
            

                    cerrar_ventana_secundaria(ventana_ap, root)
                    
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo DICOM.")


      
    ventana_ap = tk.Toplevel()
    ventana_ap.title("Agregar Paciente")
    ventana_ap.geometry("600x500")
    ventana_ap.configure(bg="#003366")
    #ventana_ap.protocol("WM_DELETE_WINDOW", cerrar_ventana_secundaria(ventana_ap, root))
    
    # Esta función reemplaza el comportamiento de la X
    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres cerrar esta ventana?"):
            ventana_ap.destroy()
            root.deiconify()  # Vuelve a mostrar la ventana principal si es necesario

    ventana_ap.protocol("WM_DELETE_WINDOW", on_closing)

    
    header_canvas = tk.Canvas(ventana_ap, height=100, bg="#00509E", highlightthickness=0)
    header_canvas.pack(fill="x")
    header_canvas.create_text(
            300, 50, text="Ingresar datos del Paciente", fill="white", font=("Arial", 20, "bold")
    )
        
    main_frame = tk.Frame(ventana_ap, bg="#004080", padx=20, pady=20, highlightthickness=2, highlightbackground="#00509E")
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    
    # Widgets del formulario
    tk.Label(main_frame, text="Nombre:", bg="#004080", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_nombre = ttk.Entry(main_frame, width=30)
    entry_nombre.grid(row=0, column=1, pady=10)
        
    tk.Label(main_frame, text="Apellido:", bg="#004080", fg="white", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_apellido = ttk.Entry(main_frame, width=30)
    entry_apellido.grid(row=1, column=1, pady=10)
        
    tk.Label(main_frame, text="Edad:", bg="#004080", fg="white", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_edad = ttk.Entry(main_frame, width=30)
    entry_edad.grid(row=2, column=1, pady=10)
        
    tk.Label(main_frame, text="Sexo:", bg="#004080", fg="white", font=("Arial", 12, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    combo_sexo = ttk.Combobox(main_frame, values=["Masculino", "Femenino"], state="readonly", width=28)
    combo_sexo.grid(row=3, column=1, pady=10)
    

    btn_guardar = tk.Button(
            ventana_ap, text="Guardar y Cargar Imagen", font=("Arial", 12, "bold"), bg="#FF7F50", fg="white",width=20, height=2,
            activebackground="#003366", activeforeground="white", relief="flat", padx=10, borderwidth=0,
            command=guardar_datos
    )
    btn_guardar.pack(pady=20)


# In[10]:


def cargar_pacientes():
    
    #Cargar los datos de los pacientes desde el archivo pacientes.txt.

    pacientes = []
    if not os.path.exists("pacientes.txt"):
        return pacientes

    with open("pacientes.txt", "r") as file:
        datos_paciente = {}
        for line in file:
            if line.strip() == "":
                if datos_paciente:
                    pacientes.append(datos_paciente)
                    datos_paciente = {}
            else:
                clave, valor = line.strip().split(": ", 1)
                datos_paciente[clave] = valor

        if datos_paciente:  
            pacientes.append(datos_paciente)

    return pacientes


# In[11]:


def eliminar_paciente(paciente, ventana_detalle, lista_pacientes, pacientes, root):
    
    #Eliminar un paciente de los registros y borra su imagen asociada.

    respuesta = messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a {paciente['Nombre']} {paciente['Apellido']}?")
    if respuesta:
        pacientes.remove(paciente)

        with open("pacientes.txt", "w") as file:
            for p in pacientes:
                for clave, valor in p.items():
                    file.write(f"{clave}: {valor}\n")
                file.write("\n")

        if "Imagen" in paciente and paciente["Imagen"]:
            ruta_imagen = os.path.join("converted_images", paciente["Imagen"])
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)

        messagebox.showinfo("Éxito", "Paciente eliminado correctamente.")
        
        cerrar_ventana_secundaria(ventana_detalle, root)


        lista_pacientes.delete(0, END)
        for i, p in enumerate(pacientes):
            lista_pacientes.insert(i, f"{p['Nombre']} {p['Apellido']}")


# In[12]:


def nueva_inspeccion(paciente, ventana_detalle, root):
    
    #Realizar una nueva inspección para un paciente seleccionado.
  
    archivo_dcm = filedialog.askopenfilename(
            filetypes=[
                ("Archivos DICOM", "*.dcm"),
                ("Imágenes JPG", "*.jpg"),
                ("Imágenes PNG", "*.png"),
                ("Todos los archivos permitidos", "*.dcm *.jpg *.png"),
            ]
    )
  
    if not archivo_dcm:
        return

    if archivo_dcm:
      
                    _, extension = os.path.splitext(archivo_dcm)  
                    extension = extension.lower()  

                    if extension == ".dcm":
                        nombre_imagen = f"{paciente['Nombre']}_{paciente['Apellido']}_nueva.png".replace(" ", "_")              
                        # Convertir DICOM a PNG
                        output_png = os.path.join("converted_images", nombre_imagen)
                        convert_dicom_to_png(archivo_dcm, output_png)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(output_png, "dcm")
                        
                    elif extension == ".png":
                        nombre_imagen = f"{paciente['Nombre']}_{paciente['Apellido']}_nueva.png".replace(" ", "_")
                        output_png = os.path.join("converted_images", nombre_imagen)

                        shutil.copy(archivo_dcm, output_png)
                        nueva_imagen_path, fractura_detectada,confidence = realizar_prediccion(output_png,"png")

                    else:
                        
                        nombre_imagen = f"{paciente['Nombre']}_{paciente['Apellido']}_nueva.jpg".replace(" ", "_")
                        output_png = os.path.join("converted_images", nombre_imagen)
                        shutil.copy(archivo_dcm, output_png)
                        nueva_imagen_path, fractura_detectada,confidence= realizar_prediccion(output_png,"jpg")
                        

                    
                    a = nombre_imagen[-4:]
                    paciente["Imagen"] = nombre_imagen[0:-4] +"_prediccion" + a
                    paciente["Prob"] = confidence
                
                    
                    pacientes = cargar_pacientes()
                    with open("pacientes.txt", "w") as file:
                        for p in pacientes:
                            if p["Nombre"] == paciente["Nombre"] and p["Apellido"] == paciente["Apellido"]:
                                p["Imagen"] = nombre_imagen[0:-4] +"_prediccion" + a
                                p["Prob"] = confidence
                            for clave, valor in p.items():
                                file.write(f"{clave}: {valor}\n")
                            file.write("\n")
                
                    resultado_texto = "Fractura detectada" if fractura_detectada else "No se detectó fractura"
                    messagebox.showinfo("Resultado", f"Paciente guardado.\n{resultado_texto}")
                    cerrar_ventana_secundaria(ventana_detalle, root)


# In[13]:


def mostrar_paciente(paciente, lista_pacientes, ventana_lista, root):
    
    #Mostrar los datos del paciente seleccionado y las imágenes asociadas.

    ventana_lista.withdraw()
    ventana_detalle = tk.Toplevel()
    ventana_detalle.title(f"Detalle de {paciente['Nombre']} {paciente['Apellido']}")
    ventana_detalle.geometry("1000x700")
    ventana_detalle.resizable(False,False)
    ventana_detalle.configure(bg="#003366")  # Azul marino
    
    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres cerrar esta ventana?"):
            ventana_detalle.destroy()
            root.deiconify()  
            
    ventana_detalle.protocol("WM_DELETE_WINDOW", on_closing)
    
    datos_frame = tk.Frame(ventana_detalle,bg="#003366")
    datos_frame.pack(side="left", padx=15, pady=40, fill='y')
    tk.Label(datos_frame, text="Datos del Paciente", font=("Arial", 15, "bold")).pack()
    for key, value in paciente.items():
        if key != "Imagen":
            tk.Label(datos_frame, text=f"{key}: {value}", anchor="w").pack(fill='x')

    tk.Button(datos_frame, text="Eliminar Paciente", bg="#e04356", fg="white", font=("Arial", 10, "bold"),
           command=lambda: eliminar_paciente(paciente, ventana_detalle, lista_pacientes, cargar_pacientes(),root)).pack(pady=15)

    tk.Button(datos_frame, text="Nueva Inspección", bg="#36a37f", fg="white", font=("Arial", 10, "bold"),
           command=lambda: nueva_inspeccion(paciente, ventana_detalle, root)).pack(pady= 15)

    tk.Button(datos_frame, text="Atrás", bg="#405eb8", fg="white", font=("Arial", 10, "bold"),
           command=lambda: volver_a_lista(ventana_detalle, ventana_lista)).pack(pady=15)


    center_frame = ttk.Frame(ventana_detalle, style="TFrame")
    center_frame.pack(side="left", fill="both", expand=True)



    if "Imagen" in paciente and paciente["Imagen"]:
        ruta_imagen = os.path.join("converted_images", paciente["Imagen"])
        if os.path.exists(ruta_imagen):
            image_np_original = cv2.imread(ruta_imagen)
            image_np_original = cv2.resize(image_np_original, (1000, 1000))
            image_np_filtered = image_np_original.copy()
            # Marco de imagen
            canvas_ = Canvas(center_frame, bg="black", width=600, height=600)
            canvas_.pack(fill="both", expand=True)
            canvas_width, canvas_height = 750, 750
            
            tk_image = cv_to_tk(image_np_filtered)
            # Variables globales para el panning
            drag_data = {"x": 0, "y": 0, "item": None}
            tk_image = cv_to_tk(image_np_filtered)
            ventana_detalle.tk_image = tk_image
            # Crear la imagen en el canvas en el centro
            image_container = canvas_.create_image(canvas_width//2, canvas_height//2, image=tk_image)
         
        else:
            tk.Label(center_frame, text="Imagen no encontrada").pack()
    else:
        tk.Label(center_frame, text="Sin imágenes asociadas").pack()


    canvas_.bind("<ButtonPress-1>", lambda event: start_drag(event, canvas_,drag_data))
    canvas_.bind("<B1-Motion>", lambda event: do_drag(event, canvas_, image_container,drag_data))
    
    #style = ttk.Style()
    #style.theme_use('clam')
    canvas2 = Canvas(center_frame, width=500, height=140, highlightthickness=0, bg="#003366")
    canvas2.pack(fill="x", expand=True)

        
    # Obtener el ancho del canvas dinámicamente
    canvas_width = 500       
    if float(paciente["Prob"]) == 0.0:
            mensaje = "No se han encontrado anomalías"
    else:
            confianza = str(paciente["Prob"])
            mensaje = f"Anomalía detectada con {confianza[:5]}% de seguridad"
        
    canvas2.create_text(
            canvas_width // 2, 50,  
            text=mensaje,
            font=("Arial", 12, "bold"),
            fill="#fafbfd",
            anchor="center")


    # Controles (Sliders)

    control_frame = ttk.LabelFrame(ventana_detalle, text="Ajustes", padding=10, style="TLabelframe")
    control_frame.pack(side="right", fill="y")

    angle_scale = ttk.Scale(control_frame, from_=0, to=360, orient=tk.HORIZONTAL)
    angle_scale.set(0)
    ttk.Label(control_frame, text="Ángulo").pack(anchor="w", pady=5)
    angle_scale.pack(fill="x")

    zoom_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL)
    zoom_scale.set(0)
    ttk.Label(control_frame, text="Zoom").pack(anchor="w", pady=5)
    zoom_scale.pack(fill="x")

    contrast_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL)
    contrast_scale.set(1.0)
    ttk.Label(control_frame, text="Contraste").pack(anchor="w", pady=5)
    contrast_scale.pack(fill="x")

    brightness_scale = ttk.Scale(control_frame, from_=-100, to=100, orient=tk.HORIZONTAL)
    brightness_scale.set(0)
    ttk.Label(control_frame, text="Brillo").pack(anchor="w", pady=5)
    brightness_scale.pack(fill="x")
    
    # Asignar la función update_image a los sliders usando lambda
    for scale in (angle_scale, zoom_scale, contrast_scale, brightness_scale):
        scale.config(command=lambda _, c=canvas_, ic=image_container, img=image_np_filtered, 
                     a=angle_scale, z=zoom_scale, co=contrast_scale, b=brightness_scale: 
                     update_image(c, ic, img, a, z, co, b))





# In[14]:


def volver_a_lista(ventana_actual, ventana_lista):
    #Cierra la ventana actual y regresa a la ventana de la lista de pacientes.
    ventana_actual.destroy()
    ventana_lista.deiconify()


# In[15]:


def ver_pacientes(root):
    
    pacientes = cargar_pacientes()
    #if not pacientes:
    #    messagebox.showinfo("Información", "No hay pacientes registrados.")
    #    root.deiconify()
        #return

    ventana_pacientes = tk.Toplevel()
    ventana_pacientes.title("Lista de Pacientes")
    ventana_pacientes.geometry("600x500")
    ventana_pacientes.configure(bg="#003366")
    
    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres cerrar esta ventana?"):
            ventana_pacientes.destroy()
            root.deiconify()  

    ventana_pacientes.protocol("WM_DELETE_WINDOW", on_closing)
    header_canvas = tk.Canvas(ventana_pacientes, height=80, bg="#00509E", highlightthickness=0)
    header_canvas.pack(fill="x")
    header_canvas.create_text(
        300, 40, text="Lista de Pacientes", fill="white", font=("Arial", 20, "bold")
    )

    # Frame principal
    main_frame = tk.Frame(ventana_pacientes, bg="#004080", padx=20, pady=20, highlightbackground="#00509E", highlightthickness=2)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)
    lista_frame = tk.Frame(main_frame, bg="#004080")
    lista_frame.pack(fill="both", expand=True, pady=10)

    # Scrollbar 
    scrollbar = tk.Scrollbar(lista_frame)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    # Listbox 
    lista_pacientes = tk.Listbox(
        lista_frame, yscrollcommand=scrollbar.set, bg="#003366", fg="white",
        font=("Arial", 12), selectbackground="#00509E", selectforeground="white",
        relief="flat", highlightthickness=1, highlightbackground="#00509E"
    )
    lista_pacientes.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
    scrollbar.config(command=lista_pacientes.yview)


    for i, paciente in enumerate(pacientes):
        lista_pacientes.insert(i, f"{paciente['Nombre']} {paciente['Apellido']}")

    buttons = Canvas(main_frame, width=500, height=140, highlightthickness=0, bg="#003366")
    buttons.pack(fill="x", expand=True)

    def seleccionar_paciente(root):
        seleccion = lista_pacientes.curselection()
        if seleccion:
            paciente = pacientes[seleccion[0]]
            mostrar_paciente(paciente, lista_pacientes, ventana_pacientes, root)

    create_button(buttons, 100, 50, 130, 25, "Seleccionar",  lambda: seleccionar_paciente (root) , "#87CEEB", "#B22222")
    create_button(buttons, 300, 50, 130, 25, "Cerrar", lambda: cerrar_ventana_secundaria(ventana_pacientes, root), "#87CEEB", "#B22222")


# In[16]:


def create_button(canvas, x, y, width, height, text, command, color1, color2):
   
    radius = height // 2
    canvas.create_oval(x, y, x + 2 * radius, y + 2 * radius, fill=color1, outline=color1)
    canvas.create_oval(x + width - 2 * radius, y, x + width, y + 2 * radius, fill=color1, outline=color1)
    canvas.create_rectangle(x + radius, y, x + width - radius, y + height, fill=color1, outline=color1)   
    canvas.create_oval(x + 2, y + 2, x + 2 * radius - 2, y + 2 * radius - 2, fill=color2, outline=color2)
    canvas.create_oval(x + width - 2 * radius + 2, y + 2, x + width - 2, y + 2 * radius - 2, fill=color2, outline=color2)
    canvas.create_rectangle(x + radius + 2, y + 2, x + width - radius - 2, y + height - 2, fill=color2, outline=color2)
    
   
    text_id = canvas.create_text(x + width // 2, y + height // 2, text=text, font=("Arial", 12, "bold"), fill="white")
    
    def on_click(event):
        command()
    canvas.tag_bind(text_id, "<Button-1>", on_click)


# In[17]:


# Función para actualizar la imagen 
def update_image(canvas, image_container, image_np, angle_scale, zoom_scale, contrast_scale, brightness_scale):

    global image_np_filtered
    if image_np is None:
        return

    # Obtener los valores de los controles
    angle = angle_scale.get()
    zoom_factor = zoom_scale.get()
    contrast = contrast_scale.get()
    brightness = brightness_scale.get()

    # Aplica las transformaciones
    transformed = rotate_image(image_np, angle)
    transformed = zoom_image(transformed, zoom_factor)
    transformed = adjust_contrast(transformed, contrast, brightness)

    image_np_filtered = transformed.copy()
    tk_image = cv_to_tk(transformed)

    # Actualiza el canvas
    canvas.itemconfig(image_container, image=tk_image)
    canvas.image = tk_image  

def start_drag(event, canvas,drag_data):
    # Guardar la posición inicial del mouse
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def do_drag(event, canvas, image_container,drag_data):
    # Calcular la diferencia y mover la imagen en el canvas
    dx = event.x - drag_data["x"]
    dy = event.y - drag_data["y"]
    canvas.move(image_container, dx, dy)
    drag_data["x"] = event.x
    drag_data["y"] = event.y


# In[18]:


def cerrar_ventana_secundaria(ventana_secundaria, root):
    ventana_secundaria.destroy()
    root.deiconify()  # Muestra nuevamente la ventana principal


# In[19]:


def mostrar_imagen(imagen_path,fractura_detectada,confidence, root):

    global image_np_filtered
    ventana_imagen = tk.Toplevel(bg="#003366")
    ventana_imagen.title("Resultado de Predicción")
    ventana_imagen.geometry("1100x820")  # Tamaño fijo
    ventana_imagen.resizable(False,False)
    

    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres cerrar esta ventana?"):
            ventana_imagen.destroy()
            root.deiconify()  # Vuelve a mostrar la ventana principal si es necesario

    ventana_imagen.protocol("WM_DELETE_WINDOW", on_closing)


    
    # Crear un estilo
    style = ttk.Style()
    style.configure("TFrame", background="#003366") 
    style.configure("TLabelframe", background="#003366")  
    style.configure("TLabelframe.Label", background="#003366", foreground="white")  
    
    # Contenedor principal (izquierda y derecha)
    main_frame = ttk.Frame(ventana_imagen, style="TFrame")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    # LADO IZQUIERDO: Imagen + Mensaje 
    left_frame = ttk.Frame(main_frame, style="TFrame")
    left_frame.pack(side="left", fill="both", expand=True, pady=30)

    ruta_imagen = imagen_path 
    image_np_original = cv2.imread(ruta_imagen)
    if image_np_original is None:
        raise Exception("No se pudo cargar la imagen, verifica la ruta.")
    image_np_original = cv2.resize(image_np_original, (1200, 1200))
    image_np_filtered = image_np_original.copy()
    

    # Marco de imagen
    canvas_ = Canvas(left_frame, bg="black", width=630, height=610)
    canvas_.pack(fill="both", expand=True)
    
    # Canvas y Variables para panning
    canvas_width, canvas_height = 800, 800
    
    tk_image = cv_to_tk(image_np_filtered)
    # Variables globales para el panning
    drag_data = {"x": 0, "y": 0, "item": None}
    tk_image = cv_to_tk(image_np_filtered)
    ventana_imagen.tk_image = tk_image

    image_container = canvas_.create_image(canvas_width//2, canvas_height//2, image=tk_image)

    canvas_.bind("<ButtonPress-1>", lambda event: start_drag(event, canvas_,drag_data))
    canvas_.bind("<B1-Motion>", lambda event: do_drag(event, canvas_, image_container,drag_data))
    
    #Estilos para los controles
    #style = ttk.Style()
    #style.theme_use('clam')

    canvas2 = Canvas(left_frame, width=500, height=140, highlightthickness=0, bg="#003366")
    canvas2.pack(fill="x", expand=True)


    # Obtener el ancho del canvas dinámicamente
    canvas_width = 500  
    
    if fractura_detectada:
        confianza = str(confidence)
        mensaje = f"Anomalía detectada con {confianza[:5]}% de seguridad"
    else:
        mensaje = "No se han encontrado anomalías"
    

    canvas2.create_text(
        canvas_width // 2, 50, 
        text=mensaje,
        font=("Arial", 12, "bold"),
        fill="#fafbfd",
        anchor="center"
    )
    

    button_x = canvas_width // 2 - 65  
    create_button(canvas2, button_x, 100, 130, 25, "Cerrar", lambda: cerrar_ventana_secundaria(ventana_imagen, root), "#87CEEB", "#B22222")

 
    # LADO DERECHO: Controles (Sliders)

    control_frame = ttk.LabelFrame(main_frame, text="Ajustes", padding=10, style="TLabelframe")
    control_frame.pack(side="right", fill="y", padx=30, pady=80)
    
    # Sliders con etiquetas
    angle_scale = ttk.Scale(control_frame, from_=0, to=360, orient=tk.HORIZONTAL)
    angle_scale.set(0)
    ttk.Label(control_frame, text="Ángulo").pack(anchor="w", pady=5)
    angle_scale.pack(fill="x")

    zoom_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL)
    zoom_scale.set(0)
    ttk.Label(control_frame, text="Zoom").pack(anchor="w", pady=5)
    zoom_scale.pack(fill="x")

    contrast_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL)
    contrast_scale.set(1.0)
    ttk.Label(control_frame, text="Contraste").pack(anchor="w", pady=5)
    contrast_scale.pack(fill="x")

    brightness_scale = ttk.Scale(control_frame, from_=-100, to=100, orient=tk.HORIZONTAL)
    brightness_scale.set(0)
    ttk.Label(control_frame, text="Brillo").pack(anchor="w", pady=5)
    brightness_scale.pack(fill="x")
    
    # Asignar la función update_image a los sliders usando lambda
    for scale in (angle_scale, zoom_scale, contrast_scale, brightness_scale):
        scale.config(command=lambda _, c=canvas_, ic=image_container, img=image_np_filtered, 
                     a=angle_scale, z=zoom_scale, co=contrast_scale, b=brightness_scale: 
                     update_image(c, ic, img, a, z, co, b))


    def save_image():
        # Abrir diálogo para guardar
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            # Convertir la imagen filtrada (BGR) a RGB y guardar usando PIL
            image_rgb = cv2.cvtColor(image_np_filtered, cv2.COLOR_BGR2RGB)
            Image.fromarray(image_rgb).save(file_path)
            messagebox.showinfo("Guardar imagen", f"Imagen guardada en:\n{file_path}")

    save_button = ttk.Button(control_frame, text="Guardar Cambios",
                             command=save_image)
    save_button.pack(side="bottom", pady=10,padx=30)  # Se coloca debajo de los sliders


# In[21]:


def main_window():
    root = tk.Tk()
    root.title("Detección de Fracturas")
    root.geometry("800x500")
    root.resizable(False, False) 
    #root.protocol("WM_DELETE_WINDOW", root.destroy)
    canvas = Canvas(root, width=500, height=300, bg="#003366", highlightthickness=0)
    canvas.pack(fill="both", expand=True)


    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Estás seguro de que quieres cerrar esta ventana?"):
            root.destroy()
        
    canvas.create_text(
        400, 50,  
        text="Sistema de Detección de Fracturas", 
        font=("Arial", 24, "bold"),  
        fill="#fafbfd",
    )
    # Funciones que abren ventanas secundarias y ocultan la principal
    def open_revision_rapida():
        root.withdraw()  # Oculta la ventana principal
        revision_rapida(root)  # Se pasa la referencia de root

    def open_agregar_paciente():
        root.withdraw()
        agregar_paciente(root)

    def open_ver_pacientes():
        root.withdraw()
        ver_pacientes(root)
        
    create_button(canvas, 300, 150, 240, 40, "Revisión Rápida", open_revision_rapida, "#87CEEB", "#FF7F50")
    create_button(canvas, 300, 250, 240, 40, "Agregar Paciente", open_agregar_paciente, "#87CEEB", "#B22222")
    create_button(canvas, 300, 350, 240, 40, "Ver Pacientes", open_ver_pacientes, "#87CEEB", "#6A5ACD")

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main_window()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




