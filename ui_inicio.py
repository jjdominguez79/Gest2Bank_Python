import tkinter as tk
from tkinter import ttk
from pathlib import Path

def build_home(root, logo_path: Path | None):
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    if logo_path and Path(logo_path).exists():
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((200,200))
            photo = ImageTk.PhotoImage(img)
            lbl = ttk.Label(frame, image=photo); lbl.image = photo; lbl.pack(pady=8)
        except Exception:
            ttk.Label(frame, text=f"(Logo no disponible: {logo_path})").pack()

    ttk.Label(frame, text="Gest2Bank", font=("Segoe UI", 20, "bold")).pack(pady=6)
    instrucciones = (
        "1) Verifica/edita tus plantillas en JSON.\n"
        "2) Usa 'Extractos' para generar suenlace de movimientos bancarios.\n"
        "3) Usa 'Facturas' para emitidas/recibidas.\n"
    )
    ttk.Label(frame, text=instrucciones, justify=tk.LEFT).pack(pady=6)

    return frame
