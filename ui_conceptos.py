
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

def abrir_editor_conceptos(parent, plantilla, on_save):
    # Ventana modal para editar conceptos de una plantilla
    win = tb.Toplevel(parent)
    win.title(f"Conceptos - {plantilla.get('codigo_empresa','')} ({plantilla.get('nombre_banco','')})")
    win.geometry("800x600")
    win.grab_set()

    style = tb.Style()

    tb.Label(win, text="Filtros de concepto (usa *comodines*) y subcuentas:", font=("Segoe UI", 10, "bold")).pack(pady=(10,6))

    frame = tb.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    cols = ("filtro","subcuenta")
    tree = tb.Treeview(frame, columns=cols, show="headings", height=12)
    vsb = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = tb.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    for c in cols:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=250 if c=="filtro" else 180, anchor="w")

    conceptos = plantilla.get("conceptos", [])
    if isinstance(conceptos, dict):  # compatibilidad
        conceptos = [{"filtro": k, "subcuenta": v} for k, v in conceptos.items()]

    def refrescar():
        tree.delete(*tree.get_children())
        for i, c in enumerate(conceptos):
            tag = "odd" if i%2 else "even"
            tree.insert("", "end", values=(c.get("filtro",""), c.get("subcuenta","")), tags=(tag,))
        tree.tag_configure("odd", background=style.colors.light)

    def add_concepto():
        top = tb.Toplevel(win)
        top.title("Añadir concepto")
        top.geometry("400x180")
        top.transient(win)       # <— modal amigable
        top.grab_set()           # <— captura de foco

        tb.Label(top, text="Filtro (ej: *comi*):").pack(anchor="w", padx=10, pady=(10,2))
        ent_f = tb.Entry(top)
        ent_f.pack(fill="x", padx=10)
        tb.Label(top, text="Subcuenta:").pack(anchor="w", padx=10, pady=(8,2))
        ent_s = tb.Entry(top)
        ent_s.pack(fill="x", padx=10)

        def guardar():
            f = ent_f.get().strip()
            s = ent_s.get().strip()
            if not f or not s:
                from tkinter import messagebox
                messagebox.showerror("Error", "Filtro y subcuenta son obligatorios.")
                return
            conceptos.append({"filtro": f, "subcuenta": s})
            refrescar()
            top.destroy()

        # Atajos y foco
        ent_f.focus_set()
        top.bind("<Return>", lambda e: guardar())

        tb.Button(top, text="Guardar", bootstyle="success", command=guardar).pack(pady=10)


    def edit_concepto():
        sel = tree.selection()
        if not sel:
            return
        idx = tree.index(sel[0])
        c = conceptos[idx]

        top = tb.Toplevel(win)
        top.title("Modificar concepto")
        top.geometry("400x180")
        top.transient(win)
        top.grab_set()

        tb.Label(top, text="Filtro (ej: *comi*):").pack(anchor="w", padx=10, pady=(10,2))
        ent_f = tb.Entry(top)
        ent_f.insert(0, c.get("filtro",""))
        ent_f.pack(fill="x", padx=10)

        tb.Label(top, text="Subcuenta:").pack(anchor="w", padx=10, pady=(8,2))
        ent_s = tb.Entry(top)
        ent_s.insert(0, c.get("subcuenta",""))
        ent_s.pack(fill="x", padx=10)

        def guardar():
            c["filtro"] = ent_f.get().strip()
            c["subcuenta"] = ent_s.get().strip()
            refrescar()
            top.destroy()

        ent_f.focus_set()
        top.bind("<Return>", lambda e: guardar())

        tb.Button(top, text="Guardar", bootstyle="primary", command=guardar).pack(pady=10)


    def del_concepto():
        sel = tree.selection()
        if not sel: return
        idx = tree.index(sel[0]); del conceptos[idx]; refrescar()

    btns = tb.Frame(win); btns.pack(fill="x", padx=10, pady=(0,10))
    tb.Button(btns, text="Añadir", bootstyle="primary", command=add_concepto).pack(side="left", padx=6)
    tb.Button(btns, text="Modificar", bootstyle="secondary", command=edit_concepto).pack(side="left", padx=6)
    tb.Button(btns, text="Eliminar", bootstyle="danger", command=del_concepto).pack(side="left", padx=6)
    tb.Button(btns, text="Cerrar y guardar", bootstyle="success", command=lambda: (on_save(conceptos), win.destroy())).pack(side="right", padx=6)

    refrescar()
