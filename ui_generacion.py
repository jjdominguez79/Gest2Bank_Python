
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd
from gestor_plantillas import cargar_plantillas
from utilidades import columna_a_indice, normaliza_fecha, limpia_texto, pad_subcuenta
from generador_suenlace import generar_suenlace

def mostrar_pantalla_generacion(parent, ruta_plantillas, on_status=lambda m: None):
    for w in parent.winfo_children():
        w.destroy()

    cont = tb.Frame(parent, padding=10)
    cont.pack(fill="both", expand=True)

    tb.Label(cont, text="Generar fichero", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,8))

    lf_p = tb.Labelframe(cont, text="Plantilla"); lf_p.pack(fill="x", pady=6)

    plantillas = cargar_plantillas(ruta_plantillas)
    plantilla_map = {}
    combo = tb.Combobox(lf_p, state="readonly", width=70)
    for p in plantillas:
        key = f"{(p.get('nombre_empresa',''))} - {p.get('nombre_banco','')}"
        plantilla_map[key] = p
    combo["values"] = list(plantilla_map.keys())
    combo.pack(fill="x", padx=8, pady=6)

    resumen = tb.Label(lf_p, text="", anchor="w");
    resumen.pack(fill="x", padx=8, pady=(0,8))

    def on_sel(*_):
        p = plantilla_map.get(combo.get())
        if not p:
            resumen.config(text=""); return
        txt = (f"Empresa: {p.get('nombre_empresa','')} | Ejercicio: {p.get('ejercicio','')}\n"
               f"Subcuenta banco: {p.get('subcuenta_banco','')} | Contrapartida: {p.get('subcuenta_default','')}\n"
               f"Col Fecha: {p.get('columna_fecha','')}\n"
               f"Col Importe: {p.get('columna_importe','')}\n"
               f"Col Concepto: {p.get('columna_concepto','')}\n"
               f"Fila inicio: {p.get('fila_inicio','')}")
        resumen.config(text=txt)
    combo.bind("<<ComboboxSelected>>", on_sel)

    lf_x = tb.Labelframe(cont, text="Excel"); lf_x.pack(fill="x", pady=6)
    ruta_excel = tb.Entry(lf_x); ruta_excel.pack(side="left", fill="x", expand=True, padx=8, pady=6)

    def buscar_excel():
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if f:
            ruta_excel.delete(0, "end"); ruta_excel.insert(0, f); cargar_hojas()
    tb.Button(lf_x, text="Seleccionar", bootstyle="secondary", command=buscar_excel).pack(side="right", padx=8, pady=6)

    lf_h = tb.Labelframe(cont, text="Hoja"); lf_h.pack(fill="x", pady=6)
    combo_hoja = tb.Combobox(lf_h, state="readonly"); combo_hoja.pack(fill="x", padx=8, pady=6)

    lf_prev = tb.Labelframe(cont, text="Vista previa"); lf_prev.pack(fill="both", expand=True, pady=6)
    tree = tb.Treeview(lf_prev, show="headings", height=12)
    vsb = tb.Scrollbar(lf_prev, orient="vertical", command=tree.yview)
    hsb = tb.Scrollbar(lf_prev, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew"); vsb.grid(row=0, column=1, sticky="ns"); hsb.grid(row=1, column=0, sticky="ew")
    lf_prev.rowconfigure(0, weight=1); lf_prev.columnconfigure(0, weight=1)

    df_cache = {"df": None}

    def cargar_hojas():
        excel = ruta_excel.get().strip()
        if not excel: return
        try:
            xls = pd.ExcelFile(excel)
            combo_hoja["values"] = xls.sheet_names; combo_hoja.set("")
            df_cache["xls"] = xls
            on_status(f"Hojas detectadas: {', '.join(xls.sheet_names)}")
        except Exception as e:
            messagebox.showerror("Gest2Bank", f"No se pudo leer el Excel: {e}")

    def on_sel_hoja(*_):
        xls = df_cache.get("xls"); hoja = combo_hoja.get().strip()
        if not xls or not hoja: return
        try:
            df = pd.read_excel(xls, sheet_name=hoja, dtype=str).fillna("")
            df_cache["df"] = df
            tree.delete(*tree.get_children())
            tree["columns"] = list(df.columns)
            for c in df.columns:
                tree.heading(c, text=c); tree.column(c, width=120, anchor="w")
            for _, row in df.head(200).iterrows():
                tree.insert("", "end", values=list(row))
            on_status(f"Hoja '{hoja}' cargada ({len(df)} filas)")
        except Exception as e:
            messagebox.showerror("Gest2Bank", f"No se pudo cargar la hoja: {e}")

    combo_hoja.bind("<<ComboboxSelected>>", on_sel_hoja)

    bottom = tb.Frame(cont); bottom.pack(fill="x", pady=10)
    tb.Button(bottom, text="Generar suenlace.dat", bootstyle="success", command=lambda: generar()).pack(side="right", padx=8)

    def generar():
        p = plantilla_map.get(combo.get()); df = df_cache.get("df")
        if not p or df is None:
            messagebox.showerror("Gest2Bank", "Selecciona plantilla, Excel y hoja."); return
        dest = filedialog.asksaveasfilename(defaultextension=".dat",
                                            initialfile=f"suenlace_{str(p.get('codigo_empresa','')).zfill(5)}")
        if not dest: return
        try:
            generar_suenlace(p, df, dest)
            on_status(f"Generado: {dest}")
            messagebox.showinfo("Gest2Bank", f"Fichero generado:\n{dest}")
        except Exception as e:
            messagebox.showerror("Gest2Bank", f"Error al generar: {e}")
