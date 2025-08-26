
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox

from ui_inicio import mostrar_pantalla_inicio
from ui_plantillas import mostrar_pantallas_plantillas
from ui_generacion import mostrar_pantalla_generacion
from gestor_plantillas import obtener_configuracion, establecer_configuracion

class Gest2BankApp:
    def __init__(self):
        self.root = tb.Window(themename="flatly")
        self.root.title("Gest2Bank")
        self.root.geometry("1400x900")

        # Layout principal: sidebar + contenido
        self.container = tb.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.sidebar = tb.Frame(self.container, width=230, bootstyle="secondary")
        self.sidebar.pack(side="left", fill="y")

        self.content = tb.Frame(self.container)
        self.content.pack(side="right", fill="both", expand=True)

        # Estado
        self.status = tb.Label(self.root, text="Listo", anchor="w", bootstyle="secondary")
        self.status.pack(side="bottom", fill="x")

        # Config: ruta de plantillas
        self.ruta_plantillas = obtener_configuracion()
        if not self.ruta_plantillas:
            ruta = establecer_configuracion()
            if not ruta:
                messagebox.showerror("Gest2Bank", "No se seleccionó fichero de plantillas. La aplicación se cerrará.")
                self.root.destroy()
                return
            self.ruta_plantillas = ruta

        # Sidebar botones
        tb.Label(self.sidebar, text="Gest2Bank", font=("Segoe UI", 16, "bold")).pack(pady=(16, 8))
        tb.Button(self.sidebar, text="Inicio", bootstyle="link", command=self._go_inicio).pack(fill="x", padx=12, pady=6)
        tb.Button(self.sidebar, text="Plantillas", bootstyle="link", command=self._go_plantillas).pack(fill="x", padx=12, pady=6)
        tb.Button(self.sidebar, text="Generar fichero", bootstyle="link", command=self._go_generar).pack(fill="x", padx=12, pady=6)
        tb.Button(self.sidebar, text="Cambiar fichero de plantillas", bootstyle="link", command=self._cambiar_plantillas).pack(fill="x", padx=12, pady=20)
        tb.Button(self.sidebar, text="Salir", bootstyle="danger", command=self.root.destroy).pack(fill="x", padx=12, pady=6)

        self._go_inicio()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _go_inicio(self):
        self._clear_content()
        mostrar_pantalla_inicio(self.content)

    def _go_plantillas(self):
        self._clear_content()
        mostrar_pantallas_plantillas(self.content, self.ruta_plantillas, on_status=self._set_status)

    def _go_generar(self):
        self._clear_content()
        mostrar_pantalla_generacion(self.content, self.ruta_plantillas, on_status=self._set_status)

    def _cambiar_plantillas(self):
        nueva = establecer_configuracion()
        if nueva:
            self.ruta_plantillas = nueva
            self._set_status(f"Fichero de plantillas: {self.ruta_plantillas}")
            self._go_plantillas()

    def _set_status(self, msg):
        self.status.config(text=msg)

def main():
    app = Gest2BankApp()
    if hasattr(app, "root"):
        app.root.mainloop()

if __name__ == "__main__":
    main()
