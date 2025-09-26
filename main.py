import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json

from ui_inicio import build_home
from ui_generacion import UIGeneracionExtractos
from ui_facturas import UIFacturas
from ui_plantillas import UIPlantillas
from gestor_plantillas import GestorPlantillas

APP_NAME = "Gest2Bank"

def main():
    cfg_path = Path("config.json")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {"default_templates_path":"plantillas/plantillas.json"}
    tpl_path = Path(cfg.get("default_templates_path", "plantillas/plantillas.json")).resolve()
    gestor = GestorPlantillas(tpl_path)

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("1150x760")

    container = ttk.Frame(root); container.pack(fill=tk.BOTH, expand=True)
    current = {"frame": None}

    def show(widget_factory):
        if current["frame"] is not None:
            current["frame"].destroy()
        current["frame"] = widget_factory()

    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label="Inicio", command=lambda: show(lambda: build_home(container, Path("logo.png"))))
    menubar.add_command(label="Plantillas", command=lambda: show(lambda: UIPlantillas(container, tpl_path)))
    menubar.add_command(label="Extractos", command=lambda: show(lambda: UIGeneracionExtractos(container, gestor)))
    # Submenú Facturas
    m_fact = tk.Menu(menubar, tearoff=0)
    m_fact.add_command(label="Emitidas", command=lambda: show(lambda: UIFacturas(container, gestor, "emitidas")))
    m_fact.add_command(label="Recibidas", command=lambda: show(lambda: UIFacturas(container, gestor, "recibidas")))
    menubar.add_cascade(label="Facturas", menu=m_fact)

    show(lambda: build_home(container, Path("logo.png")))
    root.mainloop()

if __name__ == "__main__":
    main()
