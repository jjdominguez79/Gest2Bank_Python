import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd

from gestor_plantillas import GestorPlantillas
from generador_suenlace import apuntes_extracto
from utilidades import construir_nombre_salida

class UIGeneracionExtractos(ttk.Frame):
    def __init__(self, master, gestor: GestorPlantillas):
        super().__init__(master)
        self.gestor = gestor
        self.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(top, text="Código empresa:").pack(side=tk.LEFT)
        self.cod = tk.StringVar(value="00423"); ttk.Entry(top, textvariable=self.cod, width=12).pack(side=tk.LEFT, padx=6)
        ttk.Label(top, text="Banco:").pack(side=tk.LEFT)
        self.banco = tk.StringVar(value="Banco Demo"); ttk.Entry(top, textvariable=self.banco, width=18).pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Excel…", command=self._choose_excel).pack(side=tk.LEFT, padx=6)
        self.xl = tk.StringVar(); ttk.Entry(top, textvariable=self.xl).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        self.sheet = tk.StringVar()
        self.cb = ttk.Combobox(self, textvariable=self.sheet, state="readonly"); self.cb.pack(fill=tk.X, padx=8)

        self.tv = ttk.Treeview(self, show="headings", height=14); self.tv.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        bottom = ttk.Frame(self); bottom.pack(fill=tk.X, padx=8, pady=6)
        self.out = tk.StringVar()
        ttk.Button(bottom, text="Destino…", command=lambda: self.out.set(filedialog.asksaveasfilename(defaultextension=".dat", initialfile="salida.dat"))).pack(side=tk.RIGHT)
        ttk.Button(bottom, text="Generar", command=self._generar).pack(side=tk.RIGHT, padx=6)

    def _choose_excel(self):
        fp = filedialog.askopenfilename(title="Selecciona Excel", filetypes=[("Excel", ".xlsx .xls .xlsm"), ("Todos", "*.*")])
        if not fp: return
        self.xl.set(fp)
        try:
            xls = pd.ExcelFile(fp)
            self.cb["values"] = xls.sheet_names
            self.sheet.set("")
            self.tv.delete(*self.tv.get_children()); self.tv["columns"] = ()
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _load_df(self):
        df = pd.read_excel(self.xl.get(), sheet_name=self.sheet.get())
        return df

    def _preview(self):
        df = self._load_df()
        self.tv.delete(*self.tv.get_children())
        cols = list(df.columns)
        self.tv["columns"] = cols
        for c in cols:
            self.tv.heading(c, text=str(c)); self.tv.column(c, width=max(80, min(220, int(len(str(c))*10))))
        for _, row in df.head(200).iterrows():
            self.tv.insert("", tk.END, values=[row.get(c, "") for c in cols])

    def _generar(self):
        try:
            if not self.xl.get(): raise ValueError("Selecciona un Excel.")
            if not self.sheet.get(): raise ValueError("Selecciona una hoja.")
            if not self.out.get(): raise ValueError("Elige un destino.")
            codigo = self.cod.get().strip(); banco = self.banco.get().strip()
            p = self.gestor.buscar_extracto(codigo, banco)
            if not p: raise ValueError("No hay plantilla de extractos para ese código/banco.")
            ndig = int(p.get("digitos_plan", 8))

            df = self._load_df(); self._preview()

            # intentos de columnas
            cols_lower = {str(c).lower(): c for c in df.columns}
            col_fecha = next((cols_lower.get(k) for k in ["fecha","date","f. operación","fec"] if cols_lower.get(k)), None)
            col_conc  = next((cols_lower.get(k) for k in ["concepto","descripcion","descripción","detalle","concept"] if cols_lower.get(k)), None)
            col_imp   = next((cols_lower.get(k) for k in ["importe","amount","importe (€)","cargo/abono","importe final"] if cols_lower.get(k)), None)
            if not (col_fecha and col_conc and col_imp):
                raise ValueError("No se han encontrado columnas estándar de Fecha/Concepto/Importe en el Excel.")

            # mapeo de conceptos
            import fnmatch
            def subcuenta_para_concepto(concepto: str) -> str:
                cc = (concepto or "").lower()
                for cm in p.get("conceptos", []):
                    if fnmatch.fnmatch(cc, cm.get("patron","*").lower()):
                        return cm.get("subcuenta", p.get("subcuenta_por_defecto"))
                return p.get("subcuenta_por_defecto")

            out_lines = []
            for _, r in df.iterrows():
                if pd.isna(r[col_imp]) or pd.isna(r[col_fecha]): continue
                concepto = str(r[col_conc]) if not pd.isna(r[col_conc]) else ""
                subc = subcuenta_para_concepto(concepto)
                importe = float(r[col_imp])
                out_lines += apuntes_extracto(r[col_fecha], concepto, importe, p.get("subcuenta_banco"), subc, ndig)

            if not out_lines: raise ValueError("No hay apuntes válidos.")
            destino = construir_nombre_salida(self.out.get(), codigo)
            Path(destino).write_text("\n".join(out_lines)+"\n", encoding="utf-8")
            messagebox.showinfo("Gest2Bank", f"Fichero generado:\n{destino}")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))
