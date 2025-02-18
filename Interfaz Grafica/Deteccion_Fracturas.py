#!/usr/bin/env python
# coding: utf-8

# In[4]:


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil  # Para mover archivos
from tkinter import Canvas


# In[5]:


from datetime import datetime
import PIL
from PIL import Image
from PIL import ImageTk
from PIL import Image as PILImage, ImageDraw


# In[6]:p


import torch
from ultralytics import YOLO

#DETECTAR DISPOSITIVO
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
#CARGA DEL MODELO ENTRENADO
modelo_yolo = YOLO("MODELO.pt") 
modelo_yolo.to(device)



# In[7]:


#from aspose.imaging import *
from aspose.imaging import Image as AsposeImage
from aspose.imaging.fileformats.png import *
from aspose.imaging.imageoptions import *
# Función para convertir imágenes
def convert_dicom_to_png(input_dicom, output_png):
    with AsposeImage.load(input_dicom) as image:
        image.save(str(output_png), PngOptions())


# In[ ]:





# In[8]:


def realizar_prediccion(imagen_path,extension):
    
    results = modelo_yolo.predict(imagen_path)
    fracture_detected = False
    confidence = 0
    
    img = PILImage.open(imagen_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    #DIBUJAR BOUDNING BOXES
    for result in results[0].boxes:
        confidence = result.conf[0].item() *100
        fracture_detected = True
        x1, y1, x2, y2 = map(int, result.xyxy[0]) 
        draw.rectangle([x1, y1, x2, y2], outline="red", width=4)   

    if extension == "jpg":
        path_new_image = imagen_path.replace(".jpg", "_prediccion.jpg")
        img.save(path_new_image)
    else:
        path_new_image = imagen_path.replace(".png", "_prediccion.png")
        img.save(path_new_image)
        
    return path_new_image, fracture_detected, confidence


# In[ ]:





# In[9]:


def mostrar_imagen(imagen_path,fractura_detectada,confidence):

    ventana_imagen = tk.Toplevel(bg="#003366")
    ventana_imagen.title("Resultado de Predicción")
    ventana_imagen.resizable(False,False)

    img = PILImage.open(imagen_path)
    img.thumbnail((800, 500))  
    img_tk = ImageTk.PhotoImage(img)


    label_imagen = tk.Label(ventana_imagen, image=img_tk, bg="#003366")
    label_imagen.image = img_tk  
    label_imagen.pack()

    canvas = Canvas(ventana_imagen, width=500, height=150, bg="#003366", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    if fractura_detectada == True:
        confianza = str(confidence)
        canvas.create_text(
            250, 50,  
            text="Anomalia detectectada con " + confianza[0:5] +"% de seguridad",  
            font=("Arial", 12, "bold"),  
            fill="#fafbfd", 
        )
    else:
           canvas.create_text(
            250, 50, 
            text="No se han encontrado anomalias",
            font=("Arial", 12, "bold"), 
            fill="#fafbfd", 
        )
    create_button(canvas, 200, 100, 130, 25, "Cerrar", ventana_imagen.destroy, "#87CEEB", "#B22222")




# In[10]:


def move_to_directory(filepath, target_directory="converted_images"):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    new_path = os.path.join(target_directory, os.path.basename(filepath))
    shutil.move(filepath, new_path)
    return new_path


# In[11]:


def revision_rapida():
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
    mostrar_imagen(nueva_imagen_path,fractura_detectada,confidence)


# In[12]:


# Agregar Paciente
def agregar_paciente():
    
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
        # Recoge los datos del formulario
        datos_paciente = {
            "Nombre": entry_nombre.get(),
            "Apellido": entry_apellido.get(),
            "Edad": entry_edad.get(),
            "Sexo": combo_sexo.get(),
        }

        # Verifica si faltan datos
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

                        # Convierte el archivo DICOM a PNG
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
            

                    ventana_ap.destroy()
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo DICOM.")


      
    ventana_ap = tk.Toplevel()
    ventana_ap.title("Agregar Paciente")
    ventana_ap.geometry("600x500")
    ventana_ap.configure(bg="#003366")
  

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


# In[13]:


def cargar_pacientes():
    
    #Carga los datos de los pacientes desde el archivo pacientes.txt.

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


# In[14]:


def eliminar_paciente(paciente, ventana_detalle, lista_pacientes, pacientes):
    
    #Elimina un paciente de los registros y borra su imagen asociada.

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
        ventana_detalle.destroy()

        lista_pacientes.delete(0, END)
        for i, p in enumerate(pacientes):
            lista_pacientes.insert(i, f"{p['Nombre']} {p['Apellido']}")


# In[15]:

def nueva_inspeccion(paciente, ventana_detalle):
    
    #Realiza una nueva inspección para un paciente seleccionado.
  
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
                    ventana_detalle.destroy()


# In[16]:


def mostrar_paciente(paciente, lista_pacientes, ventana_lista):
    
    #Muestra los datos del paciente seleccionado y las imágenes asociadas.

    ventana_lista.withdraw()
    ventana_detalle = tk.Toplevel()
    ventana_detalle.title(f"Detalle de {paciente['Nombre']} {paciente['Apellido']}")
    ventana_detalle.geometry("800x600")
    ventana_detalle.configure(bg="#003366")  # Azul marino

    datos_frame = tk.Frame(ventana_detalle,bg="#003366")
    datos_frame.pack(side=tk.LEFT, padx=25, pady=40, fill='y')
    
    tk.Label(datos_frame, text="Datos del Paciente", font=("Arial", 15, "bold")).pack()
    for key, value in paciente.items():
        if key != "Imagen":
            tk.Label(datos_frame, text=f"{key}: {value}", anchor="w").pack(fill='x')

    imagen_frame = tk.Frame(ventana_detalle,height=100,width=100,bg="#003366")
    imagen_frame.pack(side=tk.RIGHT, padx=5, pady=40, fill='both', expand=True)
        
    if "Imagen" in paciente and paciente["Imagen"]:
        ruta_imagen = os.path.join("converted_images", paciente["Imagen"])
        if os.path.exists(ruta_imagen):
            img = ImageTk.PhotoImage(Image.open(ruta_imagen).resize((480, 450)))
            lbl_imagen = tk.Label(imagen_frame, image=img)
            lbl_imagen.image = img  # Necesario para evitar que Python elimine la referencia
            lbl_imagen.pack()
        else:
            tk.Label(imagen_frame, text="Imagen no encontrada").pack()
    else:
        tk.Label(imagen_frame, text="Sin imágenes asociadas").pack()
        
    if float(paciente["Prob"]) == 0.0:
        label_title = tk.Label(imagen_frame, text = "No se han detectado fracturas", font=("Arial", 13, "bold"), bg="#003366", 
                               fg="white").pack(pady = 15)
    else: 
        confidence = str(paciente["Prob"])
        label_title = tk.Label(imagen_frame, text = "Fractura detectada con un " + confidence[0:5] + "% de confianza", font=("Arial", 13, "bold"), bg="#003366", 
                               fg="white").pack(pady = 15)

    tk.Button(datos_frame, text="Eliminar Paciente", bg="#e04356", fg="white", font=("Arial", 10, "bold"),
           command=lambda: eliminar_paciente(paciente, ventana_detalle, lista_pacientes, cargar_pacientes())).pack(pady=15)

    tk.Button(datos_frame, text="Nueva Inspección", bg="#36a37f", fg="white", font=("Arial", 10, "bold"),
           command=lambda: nueva_inspeccion(paciente, ventana_detalle)).pack(pady= 15)

    tk.Button(datos_frame, text="Atrás", bg="#405eb8", fg="white", font=("Arial", 10, "bold"),
           command=lambda: volver_a_lista(ventana_detalle, ventana_lista)).pack(pady=15)
    


# In[17]:


def volver_a_lista(ventana_actual, ventana_lista):
    
    #Cierra la ventana actual y regresa a la ventana de la lista de pacientes.

    ventana_actual.destroy()
    ventana_lista.deiconify()


# In[18]:


def ver_pacientes():
    
    pacientes = cargar_pacientes()
    if not pacientes:
        messagebox.showinfo("Información", "No hay pacientes registrados.")
        return

    ventana_pacientes = tk.Toplevel()
    ventana_pacientes.title("Lista de Pacientes")
    ventana_pacientes.geometry("600x500")
    ventana_pacientes.configure(bg="#003366")

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

    btn_frame = tk.Frame(main_frame, bg="#004080")
    btn_frame.pack(pady=10)

    def seleccionar_paciente():
        seleccion = lista_pacientes.curselection()
        if seleccion:
            paciente = pacientes[seleccion[0]]
            mostrar_paciente(paciente, lista_pacientes, ventana_pacientes)

    ttk.Button(btn_frame, text="Seleccionar", command=seleccionar_paciente).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Cerrar", command=ventana_pacientes.destroy).grid(row=0, column=1, padx=10)



# In[19]:


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


# In[20]:


def main_window():
    root = tk.Tk()
    root.title("Detección de Fracturas")
    root.geometry("800x500")
    root.resizable(False, False) 

    canvas = Canvas(root, width=500, height=300, bg="#003366", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    canvas.create_text(
        400, 50,  
        text="Sistema de Detección de Fracturas", 
        font=("Arial", 24, "bold"),  
        fill="#fafbfd",
    )

    create_button(canvas, 300, 150, 240, 40, "Revisión Rápida", revision_rapida, "#87CEEB", "#FF7F50")
    create_button(canvas, 300, 250, 240, 40, "Agregar Paciente", agregar_paciente, "#87CEEB", "#B22222")
    create_button(canvas, 300, 350, 240, 40, "Ver Pacientes", ver_pacientes, "#87CEEB", "#6A5ACD")

    root.mainloop()

if __name__ == "__main__":
    main_window()


# In[ ]:





# In[ ]:





# In[ ]:




