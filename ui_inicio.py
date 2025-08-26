
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os

def mostrar_pantalla_inicio(parent):
    for w in parent.winfo_children():
        w.destroy()

    frame = tb.Frame(parent, padding=20)
    frame.pack(fill="both", expand=True)

    # Logo (el usuario debe poner su propio logo.png junto a main.py)
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((420, 140))
            ph = ImageTk.PhotoImage(img)
            lbl = tb.Label(frame, image=ph)
            lbl.image = ph
            lbl.pack(pady=20)
        except:
            tb.Label(frame, text="[No se pudo cargar el logotipo]").pack(pady=20)

    instrucciones = (
        "1) Revisa/edita o crea una plantilla en la sección 'Plantillas'.\n"
        "2) Ve a 'Generar fichero' y selecciona plantilla, Excel y hoja.\n"
        "3) Previsualiza los datos.\n"
        "4) Genera 'suenlace_XXXXX.dat' para importar en A3ECO."
    )
    tb.Label(frame, text=instrucciones, justify="center", font=("Segoe UI", 14)).pack(pady=8)
