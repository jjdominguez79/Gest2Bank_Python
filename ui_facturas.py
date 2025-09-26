import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
from utilidades import construir_nombre_salida
from facturas_common import render_tabular
from facturas_emitidas import generar_asiento_emitida
from facturas_recibidas import generar_asiento_recibida

def _normalize_df(df):
    # Try to map common column names to canonical
    cols = {str(c).strip().lower(): c for c in df.columns}
    def get(*names):
        for n in names:
            if n in cols: return cols[n]
        return None
    mapping = {
        "Fecha": get("fecha","date","f. operación","fec"),
        "Serie": get("serie"),
        "Número": get("numero","número","num","nº"),
        "NIF": get("nif","cif","dni"),
        "Nombre": get("nombre","cliente","proveedor"),
        "Base": get("base","base imponible","bi"),
        "IVA_pct": get("iva%","iva_pct","tipo iva","iva"),
        "CuotaIVA": get("cuotaiva","iva importe","iva€","cuota iva"),
        "Retencion_pct": get("ret%","retencion%","retención%"),
        "CuotaRetencion": get("cuota retencion","retencion importe","retención importe","retencion"),
        "Total": get("total","importe total","total factura","importe"),
        "Descripcion": get("descripcion","descripción","detalle","concepto"),
    }
    return df.rename(columns={v:k for k,v in mapping.items() if v})

class UIFacturas(ttk.Frame):
    def __init__(self, master, gestor, tipo: str):
        super().__init__(master)
        self.gestor = gestor
        self.tipo = tipo  # 'emitidas' or 'recibidas'
        self.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        ttk.Label(self, text=f"Facturas {self.tipo}").pack(anchor=tk.W, padx=8, pady=4)
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(top, text="Código empresa:").pack(side=tk.LEFT)
        self.cod = tk.StringVar(value="00423")
        ttk.Entry(top, textvariable=self.cod, width=12).pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Elegir Excel…", command=self._choose_excel).pack(side=tk.LEFT, padx=6)
        self.xl = tk.StringVar(); ttk.Entry(top, textvariable=self.xl).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        self.sheet = tk.StringVar()
        self.cb = ttk.Combobox(self, textvariable=self.sheet, state="readonly"); self.cb.pack(fill=tk.X, padx=8)

        self.tv = ttk.Treeview(self, show="headings", height=14); self.tv.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        bottom = ttk.Frame(self); bottom.pack(fill=tk.X, padx=8, pady=6)
        self.out = tk.StringVar()
        ttk.Button(bottom, text="Destino…", command=lambda: self.out.set(filedialog.asksaveasfilename(defaultextension=".dat", initialfile="salida.dat"))).pack(side=tk.RIGHT)
        ttk.Button(bottom, text="Generar", command=self._generar).pack(side=tk.RIGHT, padx=6)

    def _choose_excel(self):
        fp = filedialog.askopenfilename(title="Selecciona Excel", filetypes=[("Excel",".xlsx .xls .xlsm"),("Todos","*.*")])
        if not fp: return
        self.xl.set(fp)
        try:
            xls = pd.ExcelFile(fp)
            self.cb["values"] = xls.sheet_names
            self.sheet.set("")
            # clear preview
            self.tv.delete(*self.tv.get_children()); self.tv["columns"]=()
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _load_df(self):
        import pandas as pd
        df = pd.read_excel(self.xl.get(), sheet_name=self.sheet.get())
        return _normalize_df(df)

    def _preview(self):
        df = self._load_df()
        self.tv.delete(*self.tv.get_children())
        cols = list(df.columns)
        self.tv["columns"] = cols
        for c in cols:
            self.tv.heading(c, text=str(c)); self.tv.column(c, width=max(80, min(220, int(len(str(c))*10))))
        for _, row in df.head(200).iterrows():
            self.tv.insert("", tk.END, values=[row.get(c,"") for c in cols])

    def _generar(self):
        try:
            if not self.xl.get(): raise ValueError("Selecciona un Excel.")
            if not self.sheet.get(): raise ValueError("Selecciona una hoja.")
            if not self.out.get(): raise ValueError("Elige un destino.")

            df = self._load_df()
            self._preview()
            codigo = self.cod.get().strip()
            if self.tipo == "emitidas":
                conf = self._buscar_conf_emitidas(codigo)
                lineas = []
                for _, r in df.iterrows():
                    if pd.isna(r.get("Total")): continue
                    lns = generar_asiento_emitida(r, conf)
                    lineas.extend(lns)
                ndig = conf.get("digitos_plan", 8)
            else:
                conf = self._buscar_conf_recibidas(codigo)
                lineas = []
                for _, r in df.iterrows():
                    if pd.isna(r.get("Total")): continue
                    lns = generar_asiento_recibida(r, conf)
                    lineas.extend(lns)
                ndig = conf.get("digitos_plan", 8)

            from facturas_common import render_tabular
            txt = "\n".join(render_tabular(lineas, ndig)) + "\n"

            destino = construir_nombre_salida(self.out.get(), codigo)
            destino.write_text(txt, encoding="utf-8")
            messagebox.showinfo("Gest2Bank", f"Fichero generado:\n{destino}")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    # conf helpers
    def _buscar_conf_emitidas(self, codigo):
        for p in self.gestor.listar_emitidas():
            if p.get("codigo_empresa")==codigo:
                return p
        raise ValueError(f"No hay plantilla de facturas emitidas para {codigo}")

    def _buscar_conf_recibidas(self, codigo):
        for p in self.gestor.listar_recibidas():
            if p.get("codigo_empresa")==codigo:
                return p
        raise ValueError(f"No hay plantilla de facturas recibidas para {codigo}")
