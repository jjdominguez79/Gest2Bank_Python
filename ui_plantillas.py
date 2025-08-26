
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from ui_conceptos import abrir_editor_conceptos
from gestor_plantillas import cargar_plantillas, guardar_plantillas
from utilidades import pad_subcuenta

def mostrar_pantallas_plantillas(parent, ruta_plantillas, on_status=lambda m: None):
    for w in parent.winfo_children():
        w.destroy()

    cont = tb.Frame(parent, padding=10)
    cont.pack(fill="both", expand=True)

    style = tb.Style()

    tb.Label(cont, text="Plantillas", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,8))

    frame_tabla = tb.Labelframe(cont, text="Listado de plantillas")
    frame_tabla.pack(fill="both", expand=True)

    cols = ("Ejercicio","Código","Empresa","Banco","Subcuenta banco","Contrapartida")
    tree = tb.Treeview(frame_tabla, columns=cols, show="headings", height=14)
    vsb = tb.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    hsb = tb.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame_tabla.rowconfigure(0, weight=1)
    frame_tabla.columnconfigure(0, weight=1)

    for c in cols:
        tree.heading(c, text=c, command=lambda cc=c: _sort_by(tree, cc, False))
        tree.column(c, width=180 if c in ("Empresa","Banco") else 140, anchor="w")

    plantillas = cargar_plantillas(ruta_plantillas)

    def refrescar():
        tree.delete(*tree.get_children())
        for i, p in enumerate(plantillas):
            vals = (
                str(p.get("ejercicio","")),
                str(p.get("codigo_empresa","")).zfill(5),
                p.get("nombre_empresa",""),
                p.get("nombre_banco",""),
                p.get("subcuenta_banco",""),
                p.get("subcuenta_default",""),
            )
            tag = "odd" if i%2 else "even"
            tree.insert("", "end", values=vals, tags=(tag,))
        tree.tag_configure("odd", background=style.colors.light)

    def _sort_by(tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]))
        except:
            data.sort(key=lambda t: t[0])
        if reverse:
            data.reverse()
        for i, (_, k) in enumerate(data):
            tree.move(k, "", i)
        tree.heading(col, command=lambda: _sort_by(tree, col, not reverse))

    btns = tb.Frame(cont); btns.pack(fill="x", pady=8)
    tb.Button(btns, text="Crear nueva", bootstyle="primary", command=lambda: editar(None)).pack(side="left", padx=4)
    tb.Button(btns, text="Modificar", bootstyle="secondary", command=lambda: editar(_sel())).pack(side="left", padx=4)
    tb.Button(btns, text="Eliminar", bootstyle="danger", command=lambda: eliminar(_sel())).pack(side="left", padx=4)
    tb.Button(btns, text="Editar conceptos", bootstyle="info", command=lambda: conceptos(_sel())).pack(side="left", padx=12)

    def _sel():
        sel = tree.selection()
        if not sel:
            return None
        vals = tree.item(sel[0])["values"]
        codigo = str(vals[1]).zfill(5)
        for p in plantillas:
            if str(p.get("codigo_empresa","")).zfill(5) == codigo:
                return p
        return None

    def editar(plantilla):
        win = tb.Toplevel(parent)
        win.title("Plantilla")
        win.geometry("900x900")
        win.grab_set()

        campos = [
            ("Código empresa", "codigo_empresa"),
            ("Nombre empresa", "nombre_empresa"),
            ("Nombre banco", "nombre_banco"),
            ("Subcuenta banco", "subcuenta_banco"),
            ("Contrapartida por defecto", "subcuenta_default"),
            ("Dígitos subcuenta", "digitos_subcuenta"),
            ("Columna Fecha", "columna_fecha"),
            ("Columna Importe", "columna_importe"),
            ("Columna Concepto", "columna_concepto"),
            ("Primera fila a procesar", "fila_inicio"),
            ("Ejercicio", "ejercicio"),
        ]

        entries = {}
        for i, (lbl, key) in enumerate(campos):
            tb.Label(win, text=lbl).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            e = tb.Entry(win)
            e.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[key] = e
        win.columnconfigure(1, weight=1)

        if plantilla:
            for k, e in entries.items():
                e.insert(0, str(plantilla.get(k,"")))

        def guardar():
            datos = {k: entries[k].get().strip() for _, k in campos}
            datos["codigo_empresa"] = str(datos.get("codigo_empresa","")).zfill(5)
            dig = int(datos.get("digitos_subcuenta","10") or "10")
            datos["subcuenta_banco"] = pad_subcuenta(datos.get("subcuenta_banco",""), dig)
            datos["subcuenta_default"] = pad_subcuenta(datos.get("subcuenta_default",""), dig)
            if not datos["codigo_empresa"] or not datos["subcuenta_banco"]:
                messagebox.showerror("Gest2Bank","Código empresa y Subcuenta banco son obligatorios.")
                return
            if plantilla and plantilla in plantillas:
                plantillas.remove(plantilla)
            plantillas.append(datos)
            guardar_plantillas(ruta_plantillas, plantillas)
            on_status("Plantilla guardada.")
            win.destroy()
            refrescar()

        tb.Button(win, text="Guardar", bootstyle="success", command=guardar).grid(row=len(campos), column=0, columnspan=2, pady=14)

    def eliminar(plantilla):
        if not plantilla: return
        plantillas.remove(plantilla)
        guardar_plantillas(ruta_plantillas, plantillas)
        on_status("Plantilla eliminada.")
        refrescar()

    def conceptos(plantilla):
        if not plantilla: return
        def _save_concepts(new_list):
            plantilla["conceptos"] = new_list
            guardar_plantillas(ruta_plantillas, plantillas)
            on_status("Conceptos actualizados.")
        abrir_editor_conceptos(parent, plantilla, _save_concepts)

    refrescar()
