import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import fnmatch

from utilidades import construir_nombre_salida
from generador_suenlace import apuntes_extracto
from facturas_common import render_tabular
from facturas_emitidas import generar_asiento_emitida
from facturas_recibidas import generar_asiento_recibida

class UIProcesos(ttk.Frame):
    def __init__(self, master, gestor, empresa_codigo):
        super().__init__(master)
        self.gestor = gestor
        self.codigo = empresa_codigo
        self.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(top, text=f"Empresa: {self.codigo}", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        self.tipo = tk.StringVar(value="bancos")
        ttk.Radiobutton(top, text="Bancos", variable=self.tipo, value="bancos", command=self._reload_plantillas).pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(top, text="Facturas emitidas", variable=self.tipo, value="emitidas", command=self._reload_plantillas).pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(top, text="Facturas recibidas", variable=self.tipo, value="recibidas", command=self._reload_plantillas).pack(side=tk.LEFT, padx=8)

        mid = ttk.Frame(self); mid.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(mid, text="Plantilla:").pack(side=tk.LEFT)
        self.cbo = ttk.Combobox(mid, state="readonly"); self.cbo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        filebar = ttk.Frame(self); filebar.pack(fill=tk.X, padx=8, pady=4)
        self.xl = tk.StringVar(); self.sheet = tk.StringVar(); self.out = tk.StringVar()
        ttk.Button(filebar, text="Excel…", command=self._choose_excel).pack(side=tk.LEFT)
        ttk.Entry(filebar, textvariable=self.xl).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.cb_sheets = ttk.Combobox(filebar, textvariable=self.sheet, state="readonly"); self.cb_sheets.pack(side=tk.LEFT, padx=6)
        ttk.Button(filebar, text="Destino…", command=lambda: self.out.set(filedialog.asksaveasfilename(defaultextension=".dat", initialfile="salida.dat"))).pack(side=tk.LEFT)

        self.tv = ttk.Treeview(self, show="headings", height=14); self.tv.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        bottom = ttk.Frame(self); bottom.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(bottom, text="Generar", command=self._generar).pack(side=tk.RIGHT)

        self._reload_plantillas()

    def _reload_plantillas(self):
        t = self.tipo.get()
        if t=="bancos":
            vals = [p.get("banco") for p in self.gestor.listar_bancos(self.codigo)]
        elif t=="emitidas":
            vals = [p.get("nombre") for p in self.gestor.listar_emitidas(self.codigo)]
        else:
            vals = [p.get("nombre") for p in self.gestor.listar_recibidas(self.codigo)]
        self.cbo["values"] = vals
        self.cbo.set(vals[0] if vals else "")

    def _choose_excel(self):
        fp = filedialog.askopenfilename(title="Selecciona Excel", filetypes=[("Excel",".xlsx .xls .xlsm"),("Todos","*.*")])
        if not fp: return
        self.xl.set(fp)
        try:
            xls = pd.ExcelFile(fp)
            self.cb_sheets["values"] = xls.sheet_names
            self.sheet.set("")
            self.tv.delete(*self.tv.get_children()); self.tv["columns"]=()
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _load_df(self):
        df = pd.read_excel(self.xl.get(), sheet_name=self.sheet.get())
        cols = {str(c).strip().lower(): c for c in df.columns}
        def get(*names):
            for n in names:
                if n in cols: return cols[n]
            return None
        mapping = {
            "Fecha": get("fecha","date","f. operación","fec"),
            "Concepto": get("concepto","descripcion","descripción","detalle"),
            "Importe": get("importe","amount","importe (€)","cargo/abono","importe final")
        }
        mapping_f = {
            "Fecha": get("fecha","date"),
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
        if self.tipo.get()=="bancos":
            return df.rename(columns={v:k for k,v in mapping.items() if v})
        else:
            return df.rename(columns={v:k for k,v in mapping_f.items() if v})

    def _preview(self, df):
        self.tv.delete(*self.tv.get_children())
        cols = list(df.columns)
        self.tv["columns"] = cols
        for c in cols:
            self.tv.heading(c, text=str(c)); self.tv.column(c, width=max(80, min(220, int(len(str(c))*10))))
        for _, row in df.head(200).iterrows():
            self.tv.insert("", tk.END, values=[row.get(c,"") for c in cols])

    def _generar(self):
    try:
        if not self.cbo.get(): raise ValueError("Selecciona una plantilla.")
        if not self.xl.get(): raise ValueError("Selecciona un Excel.")
        if not self.sheet.get(): raise ValueError("Selecciona una hoja.")
        if not self.out.get(): raise ValueError("Elige un destino.")

        # Preview using the existing lightweight loader
        df = self._load_df(); self._preview(df)

        from pathlib import Path
        destino = construir_nombre_salida(self.out.get(), self.codigo)

        # Effective mapping: empresa-level (template-level override podría añadirse)
        empresas = [e for e in self.gestor.listar_empresas() if e.get("codigo")==self.codigo]
        map_emp = (empresas[0].get("excel") if empresas else {}) or {}

        if self.tipo.get()=="bancos":
            p = next((x for x in self.gestor.listar_bancos(self.codigo) if x.get("banco")==self.cbo.get()), None)
            if not p: raise ValueError("Plantilla no encontrada.")
            ndig = int(p.get("digitos_plan", 8))

            rows = extract_by_mapping(self.xl.get(), self.sheet.get(), map_emp)

            import fnmatch
            def subcuenta_para_concepto(concepto: str) -> str:
                cc = (concepto or "").lower()
                for cm in p.get("conceptos", []):
                    if fnmatch.fnmatch(cc, cm.get("patron","*").lower()):
                        return cm.get("subcuenta", p.get("subcuenta_por_defecto"))
                return p.get("subcuenta_por_defecto")

            out = []
            for rec in rows:
                fecha = rec.get("Fecha Asiento")
                concepto = rec.get("Descripcion Factura") or rec.get("Concepto")
                importe = rec.get("Importe")
                if fecha in (None, "") or importe in (None, ""):
                    continue
                try:
                    impf = float(str(importe).replace(",", "."))
                except Exception:
                    continue
                subc = subcuenta_para_concepto(str(concepto or ""))
                out += apuntes_extracto(fecha, str(concepto or ""), impf, p["subcuenta_banco"], subc, ndig)
            if not out: raise ValueError("No hay movimientos válidos.")
            Path(destino).write_text("
".join(out) + "
", encoding="utf-8")
        else:
            if self.tipo.get()=="emitidas":
                conf = next((x for x in self.gestor.listar_emitidas(self.codigo) if x.get("nombre")==self.cbo.get()), None)
                gen_fun = generar_asiento_emitida
            else:
                conf = next((x for x in self.gestor.listar_recibidas(self.codigo) if x.get("nombre")==self.cbo.get()), None)
                gen_fun = generar_asiento_recibida
            if not conf: raise ValueError("Plantilla no encontrada.")
            ndig = int(conf.get("digitos_plan", 8))

            rows = extract_by_mapping(self.xl.get(), self.sheet.get(), map_emp)

            lineas = []
            for rec in rows:
                row = {
                    "Fecha": rec.get("Fecha Asiento"),
                    "Descripcion": rec.get("Descripcion Factura"),
                    "Base": rec.get("Base"),
                    "IVA_pct": rec.get("Porcentaje IVA"),
                    "CuotaIVA": rec.get("Cuota IVA"),
                    "CuotaRetencion": rec.get("Cuota Retencion IRPF"),
                    "Total": rec.get("Total") if rec.get("Total") is not None else None,
                    "NIF": rec.get("NIF Cliente Proveedor"),
                    "Nombre": rec.get("Nombre Cliente Proveedor"),
                    "CuentaClienteProveedor": rec.get("Cuenta Cliente Proveedor"),
                    "CuentaComprasVentas": rec.get("Cuenta Compras Ventas"),
                    "CuentaIVA": rec.get("Cuenta IVA"),
                }
                if not row["Fecha"] or (row["Base"] is None and row["Total"] is None):
                    continue
                def to_num(x):
                    if x is None or x == "": return None
                    try:
                        return float(str(x).replace(",", "."))
                    except Exception:
                        return None
                for k in ("Base","IVA_pct","CuotaIVA","CuotaRetencion","Total"):
                    row[k] = to_num(row[k])
                row["_usar_cuenta_generica"] = bool(rec.get("_usar_cuenta_generica"))
                row["_cuenta_tercero_override"] = rec.get("Cuenta Cliente Proveedor")
                row["_cuenta_py_gv_override"] = rec.get("Cuenta Compras Ventas")
                row["_cuenta_iva_override"] = rec.get("Cuenta IVA")
                lineas.extend(gen_fun(row, conf))

            txt = "
".join(render_tabular(lineas, ndig)) + "
"
            Path(destino).write_text(txt, encoding="utf-8")

        messagebox.showinfo("Gest2Bank", f"Fichero generado:
{destino}")
    except Exception as e:
        messagebox.showerror("Gest2Bank", str(e))

            df = self._load_df(); self._preview(df)
            destino = construir_nombre_salida(self.out.get(), self.codigo)

            if self.tipo.get()=="bancos":
                p = next((x for x in self.gestor.listar_bancos(self.codigo) if x.get("banco")==self.cbo.get()), None)
                if not p: raise ValueError("Plantilla no encontrada.")
                ndig = int(p.get("digitos_plan", 8))

                # Mapeo de conceptos
                import fnmatch
                def subcuenta_para_concepto(concepto: str) -> str:
                    cc = (concepto or "").lower()
                    for cm in p.get("conceptos", []):
                        if fnmatch.fnmatch(cc, cm.get("patron","*").lower()):
                            return cm.get("subcuenta", p.get("subcuenta_por_defecto"))
                    return p.get("subcuenta_por_defecto")

                out = []
                for _, r in df.iterrows():
                    if pd.isna(r.get("Importe")) or pd.isna(r.get("Fecha")): continue
                    subc = subcuenta_para_concepto(str(r.get("Concepto","")))
                    out += apuntes_extracto(r["Fecha"], str(r.get("Concepto","")), float(r["Importe"]), p["subcuenta_banco"], subc, ndig)
                if not out: raise ValueError("No hay movimientos válidos.")
                Path(destino).write_text("\n".join(out) + "\n", encoding="utf-8")
            else:
                if self.tipo.get()=="emitidas":
                    conf = next((x for x in self.gestor.listar_emitidas(self.codigo) if x.get("nombre")==self.cbo.get()), None)
                    gen_fun = generar_asiento_emitida
                else:
                    conf = next((x for x in self.gestor.listar_recibidas(self.codigo) if x.get("nombre")==self.cbo.get()), None)
                    gen_fun = generar_asiento_recibida
                if not conf: raise ValueError("Plantilla no encontrada.")
                ndig = int(conf.get("digitos_plan", 8))

                lineas = []
                for _, r in df.iterrows():
                    if pd.isna(r.get("Total")) or pd.isna(r.get("Fecha")): continue
                    lineas.extend(gen_fun(r, conf))

                txt = "\n".join(render_tabular(lineas, ndig)) + "\n"
                Path(destino).write_text(txt, encoding="utf-8")

            messagebox.showinfo("Gest2Bank", f"Fichero generado:\n{destino}")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

def _parse_condition(cond: str):
    cond = (cond or "").strip()
    if "=" not in cond: return None, None
    col, val = cond.split("=", 1)
    return col.strip().upper(), val

def extract_by_mapping(xlsx_path: str, sheet: str, mapping: dict):
    import pandas as pd
    from utilidades import col_letter_to_index
    raw = pd.read_excel(xlsx_path, sheet_name=sheet, header=None, dtype=object)
    def col(letter):
        i = col_letter_to_index(letter)
        return None if i < 0 else i
    first = int(mapping.get("primera_fila_procesar", 2))
    start_idx = max(0, first - 1)
    cols_map = mapping.get("columnas", {})
    ign_col_letter, ign_val = _parse_condition(mapping.get("ignorar_filas",""))
    gen_col_letter, gen_val = _parse_condition(mapping.get("condicion_cuenta_generica",""))

    rows = []
    for r in range(start_idx, len(raw)):
        row = raw.iloc[r]
        if ign_col_letter is not None:
            ci = col(ign_col_letter)
            if ci is not None:
                cell = row.iloc[ci]
                if str(cell).strip() == str(ign_val):
                    continue
        rec = {}
        for k, letter in cols_map.items():
            if not letter:
                rec[k] = None; continue
            ci = col(letter)
            rec[k] = None if ci is None else row.iloc[ci]
        rec["_usar_cuenta_generica"] = False
        if gen_col_letter is not None:
            ci = col(gen_col_letter)
            if ci is not None and str(row.iloc[ci]).strip() == str(gen_val):
                rec["_usar_cuenta_generica"] = True
        rows.append(rec)
    return rows
