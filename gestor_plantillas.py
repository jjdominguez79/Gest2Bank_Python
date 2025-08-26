
import os, json
from tkinter import filedialog

CONFIG_FILE = "config.json"

def obtener_configuracion():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("ruta_plantillas", "")
        except:
            return ""
    return ""

def establecer_configuracion():
    ruta = filedialog.askopenfilename(title="Seleccionar archivo de plantillas",
                                      filetypes=[("Archivos JSON", "*.json")])
    if ruta:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"ruta_plantillas": ruta}, f, indent=2, ensure_ascii=False)
        return ruta
    return None

def cargar_plantillas(ruta_json):
    if not ruta_json or not os.path.exists(ruta_json):
        return []
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Asegurar formato lista
        if isinstance(data, dict):
            return data.get("plantillas", [])
        return data

def guardar_plantillas(ruta_json, plantillas):
    # Permitimos guardar como lista simple
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(plantillas, f, indent=2, ensure_ascii=False)
