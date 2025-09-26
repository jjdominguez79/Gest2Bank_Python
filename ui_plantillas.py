import tkinter as tk
from tkinter import ttk, messagebox
import json

def _mk_labeled_entry(parent, label, var, width=18):
    fr = ttk.Frame(parent); fr.pack(fill=tk.X, pady=2)
    ttk.Label(fr, text=label, width=22).pack(side=tk.LEFT)
    e = ttk.Entry(fr, textvariable=var, width=width); e.pack(side=tk.LEFT, fill=tk.X, expand=True)
    return e

class UIPlantillasEmpresa(ttk.Frame):
    def __init__(self, master, gestor, empresa_codigo, empresa_nombre):
        super().__init__(master)
        self.gestor = gestor
        self.codigo = empresa_codigo
        self.nombre = empresa_nombre
        self.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        ttk.Label(self, text=f"Plantillas de {self.nombre} ({self.codigo})", font=("Segoe UI", 12, "bold")).pack(pady=6, anchor=tk.W, padx=10)
        nb = ttk.Notebook(self); nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        fr_ban = ttk.Frame(nb); nb.add(fr_ban, text="Bancos"); self._build_bancos(fr_ban)
        fr_em = ttk.Frame(nb); nb.add(fr_em, text="Facturas emitidas"); self._build_emitidas(fr_em)
        fr_re = ttk.Frame(nb); nb.add(fr_re, text="Facturas recibidas"); self._build_recibidas(fr_re)

    # ---- Bancos
    def _build_bancos(self, frame):
        left = ttk.Frame(frame); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,3), pady=6)
        right = ttk.Frame(frame); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3,6), pady=6)

        cols = ("banco","subcuenta_banco","subcuenta_por_defecto")
        self.tv_ban = ttk.Treeview(left, columns=cols, show="headings", height=12)
        for c,t in zip(cols, ["Banco","Subcta banco","Subcta por defecto"]):
            self.tv_ban.heading(c, text=t); self.tv_ban.column(c, width=160)
        self.tv_ban.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(left); btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Nuevo", command=self._ban_nuevo).pack(side=tk.LEFT)
        ttk.Button(btns, text="Guardar", command=self._ban_guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Eliminar", command=self._ban_eliminar).pack(side=tk.LEFT)
        self._ban_refresh()

        self.b_banco = tk.StringVar(); self.b_sb = tk.StringVar(); self.b_sdef = tk.StringVar()
        self.b_dig = tk.StringVar(value="8"); self.b_eje = tk.StringVar(value="2025")
        ttk.Label(right, text="Editor de plantilla (Bancos)", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        _mk_labeled_entry(right, "Banco", self.b_banco)
        _mk_labeled_entry(right, "Subcuenta banco", self.b_sb)
        _mk_labeled_entry(right, "Subcuenta por defecto", self.b_sdef)
        _mk_labeled_entry(right, "Dígitos plan", self.b_dig)
        _mk_labeled_entry(right, "Ejercicio", self.b_eje)
        ttk.Label(right, text="Conceptos → Subcuentas (JSON)").pack(anchor=tk.W, pady=(6,0))
        self.b_json = tk.Text(right, height=8); self.b_json.pack(fill=tk.BOTH, expand=True)
        ttk.Label(right, text='Ejemplo: [{"patron":"*comi*","subcuenta":"62600000"}]').pack(anchor=tk.W)
        self.tv_ban.bind("<<TreeviewSelect>>", self._ban_load_selected)

    def _ban_refresh(self):
        self.tv_ban.delete(*self.tv_ban.get_children())
        for p in self.gestor.listar_bancos(self.codigo):
            self.tv_ban.insert("", tk.END, values=(p.get("banco"), p.get("subcuenta_banco"), p.get("subcuenta_por_defecto")))

    def _ban_load_selected(self, *_):
        sel = self.tv_ban.selection()
        if not sel: return
        banco, sb, sdef = self.tv_ban.item(sel[0], "values")
        p = next((x for x in self.gestor.listar_bancos(self.codigo) if x.get("banco")==banco), None)
        if not p: return
        self.b_banco.set(p.get("banco","")); self.b_sb.set(p.get("subcuenta_banco","")); self.b_sdef.set(p.get("subcuenta_por_defecto",""))
        self.b_dig.set(str(p.get("digitos_plan",8))); self.b_eje.set(str(p.get("ejercicio",2025)))
        import json; self.b_json.delete("1.0", tk.END); self.b_json.insert(tk.END, json.dumps(p.get("conceptos", []), ensure_ascii=False))
        self.b_override.set(bool(p.get("excel_override", False)))
        self.b_excel.delete("1.0", tk.END); self.b_excel.insert(tk.END, json.dumps((p.get("excel") or {}).get("columnas", {}), ensure_ascii=False, indent=2))

    def _ban_nuevo(self):
        self.b_banco.set(""); self.b_sb.set(""); self.b_sdef.set(""); self.b_dig.set("8"); self.b_eje.set("2025"); self.b_json.delete("1.0", tk.END)

    def _ban_guardar(self):
        import json
        try:
            plantilla = {
                "codigo_empresa": self.codigo,
                "banco": self.b_banco.get().strip(),
                "subcuenta_banco": self.b_sb.get().strip(),
                "subcuenta_por_defecto": self.b_sdef.get().strip(),
                "digitos_plan": int(self.b_dig.get().strip() or "8"),
                "ejercicio": int(self.b_eje.get().strip() or "2025"),
                "conceptos": json.loads(self.b_json.get("1.0", tk.END) or "[]")
            }
            
            if self.b_override.get():
                plantilla["excel_override"] = True
                plantilla["excel"] = plantilla.get("excel", {"{}":{}});
                import json as _json
                plantilla["excel"]["columnas"] = _json.loads(self.b_excel.get("1.0", tk.END) or "{}")
            else:
                plantilla["excel_override"] = False
            self.gestor.upsert_banco(plantilla); self._ban_refresh()
            messagebox.showinfo("Gest2Bank", "Plantilla guardada.")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _ban_eliminar(self):
        sel = self.tv_ban.selection()
        if not sel: return
        banco, *_ = self.tv_ban.item(sel[0], "values")
        self.gestor.eliminar_banco(self.codigo, banco); self._ban_refresh()

    # ---- Emitidas
    def _build_emitidas(self, frame):
        left = ttk.Frame(frame); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,3), pady=6)
        right = ttk.Frame(frame); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3,6), pady=6)

        cols = ("nombre","cliente_prefijo","iva_defecto")
        self.tv_em = ttk.Treeview(left, columns=cols, show="headings", height=12)
        self.tv_em.heading("nombre", text="Nombre"); self.tv_em.heading("cliente_prefijo", text="Prefijo 430"); self.tv_em.heading("iva_defecto", text="477 defecto")
        self.tv_em.column("nombre", width=180); self.tv_em.column("cliente_prefijo", width=120); self.tv_em.column("iva_defecto", width=120)
        self.tv_em.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(left); btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Nuevo", command=self._em_nuevo).pack(side=tk.LEFT)
        ttk.Button(btns, text="Guardar", command=self._em_guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Eliminar", command=self._em_eliminar).pack(side=tk.LEFT)
        self._em_refresh()

        self.em_nombre = tk.StringVar(); self.em_dig = tk.StringVar(value="8")
        self.em_cli_col = tk.BooleanVar(value=True); self.em_cli_codcol = tk.StringVar(value="NIF"); self.em_cli_pref = tk.StringVar(value="430")
        self.em_ing_def = tk.StringVar(value="70000000"); self.em_iva_def = tk.StringVar(value="47700000"); self.em_ret = tk.StringVar(value="47510000")

        ttk.Label(right, text="Editor (Emitidas)", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
self.em_override = tk.BooleanVar(value=False)

ttk.Checkbutton(right, text="Usar mapeo Excel propio (override)", variable=self.em_override).pack(anchor=tk.W, pady=(6,0))
ttk.Label(right, text="Mapeo Excel (JSON) — Clave→Letra").pack(anchor=tk.W)
self.em_excel = tk.Text(right, height=8); self.em_excel.pack(fill=tk.BOTH, expand=True)
        _mk_labeled_entry(right, "Nombre", self.em_nombre, 24)
        _mk_labeled_entry(right, "Dígitos plan", self.em_dig)
        ttk.Checkbutton(right, text="Cliente por columna", variable=self.em_cli_col).pack(anchor=tk.W)
        _mk_labeled_entry(right, "Columna código cliente", self.em_cli_codcol)
        _mk_labeled_entry(right, "Prefijo cuenta cliente (430)", self.em_cli_pref)
        _mk_labeled_entry(right, "Ingreso por defecto (700)", self.em_ing_def)
        _mk_labeled_entry(right, "IVA repercutido defecto (477)", self.em_iva_def)
        _mk_labeled_entry(right, "Retenciones IRPF (4751)", self.em_ret)

        ttk.Checkbutton(right, text="Usar mapeo Excel propio (override)", variable=tk.BooleanVar(value=False), command=lambda: None).pack(anchor=tk.W, pady=(6,0))
        ttk.Label(right, text="Tipos IVA (JSON)").pack(anchor=tk.W, pady=(6,0))
        self.em_tipos = tk.Text(right, height=5); self.em_tipos.pack(fill=tk.BOTH, expand=True)
        self.em_tipos.insert(tk.END, '[{"porcentaje":21,"cuenta_iva":"47700000"}]')

        self.tv_em.bind("<<TreeviewSelect>>", self._em_load_selected)

    def _em_refresh(self):
        self.tv_em.delete(*self.tv_em.get_children())
        for p in self.gestor.listar_emitidas(self.codigo):
            self.tv_em.insert("", tk.END, values=(p.get("nombre"), p.get("cuenta_cliente_prefijo","430"), p.get("cuenta_iva_repercutido_defecto","47700000")))

    def _em_load_selected(self, *_):
        sel = self.tv_em.selection()
        if not sel: return
        nombre, *_ = self.tv_em.item(sel[0], "values")
        p = next((x for x in self.gestor.listar_emitidas(self.codigo) if x.get("nombre")==nombre), None)
        if not p: return
        self.em_nombre.set(p.get("nombre",""))
        self.em_dig.set(str(p.get("digitos_plan",8)))
        self.em_cli_col.set(bool(p.get("cliente_por_columna", True)))
        self.em_cli_codcol.set(p.get("col_cliente_codigo","NIF"))
        self.em_cli_pref.set(p.get("cuenta_cliente_prefijo","430"))
        self.em_ing_def.set(p.get("cuenta_ingreso_por_defecto","70000000"))
        self.em_iva_def.set(p.get("cuenta_iva_repercutido_defecto","47700000"))
        self.em_ret.set(p.get("cuenta_retenciones_irpf","47510000"))
        self.em_tipos.delete("1.0", tk.END); self.em_tipos.insert(tk.END, json.dumps(p.get("tipos_iva", []), ensure_ascii=False))
        self.em_override.set(bool(p.get("excel_override", False)))
        self.em_excel.delete("1.0", tk.END); self.em_excel.insert(tk.END, json.dumps((p.get("excel") or {}).get("columnas", {}), ensure_ascii=False, indent=2))

    def _em_nuevo(self):
        self.em_nombre.set(""); self.em_dig.set("8"); self.em_cli_col.set(True); self.em_cli_codcol.set("NIF"); self.em_cli_pref.set("430"); self.em_ing_def.set("70000000"); self.em_iva_def.set("47700000"); self.em_ret.set("47510000"); self.em_tipos.delete("1.0", tk.END); self.em_tipos.insert(tk.END, "[]")

    def _em_guardar(self):
        try:
            plantilla = {
                "codigo_empresa": self.codigo,
                "nombre": self.em_nombre.get().strip(),
                "digitos_plan": int(self.em_dig.get().strip() or "8"),
                "cliente_por_columna": bool(self.em_cli_col.get()),
                "col_cliente_codigo": self.em_cli_codcol.get().strip(),
                "cuenta_cliente_prefijo": self.em_cli_pref.get().strip(),
                "cuenta_ingreso_por_defecto": self.em_ing_def.get().strip(),
                "cuenta_iva_repercutido_defecto": self.em_iva_def.get().strip(),
                "cuenta_retenciones_irpf": self.em_ret.get().strip(),
                "tipos_iva": json.loads(self.em_tipos.get("1.0", tk.END) or "[]"),
                "soporta_retencion": True
            }
            
            if self.em_override.get():
                plantilla["excel_override"] = True
                plantilla["excel"] = plantilla.get("excel", {"{}":{}});
                import json as _json
                plantilla["excel"]["columnas"] = _json.loads(self.em_excel.get("1.0", tk.END) or "{}")
            else:
                plantilla["excel_override"] = False
            self.gestor.upsert_emitida(plantilla); self._em_refresh()
            messagebox.showinfo("Gest2Bank", "Plantilla guardada.")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _em_eliminar(self):
        sel = self.tv_em.selection()
        if not sel: return
        nombre, *_ = self.tv_em.item(sel[0], "values")
        self.gestor.eliminar_emitida(self.codigo, nombre); self._em_refresh()

    # ---- Recibidas
    def _build_recibidas(self, frame):
        left = ttk.Frame(frame); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,3), pady=6)
        right = ttk.Frame(frame); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3,6), pady=6)

        cols = ("nombre","proveedor_prefijo","iva_defecto")
        self.tv_re = ttk.Treeview(left, columns=cols, show="headings", height=12)
        self.tv_re.heading("nombre", text="Nombre"); self.tv_re.heading("proveedor_prefijo", text="Prefijo 400"); self.tv_re.heading("iva_defecto", text="472 defecto")
        self.tv_re.column("nombre", width=180); self.tv_re.column("proveedor_prefijo", width=120); self.tv_re.column("iva_defecto", width=120)
        self.tv_re.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(left); btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Nuevo", command=self._re_nuevo).pack(side=tk.LEFT)
        ttk.Button(btns, text="Guardar", command=self._re_guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Eliminar", command=self._re_eliminar).pack(side=tk.LEFT)
        self._re_refresh()

        self.re_nombre = tk.StringVar(); self.re_dig = tk.StringVar(value="8")
        self.re_prov_col = tk.BooleanVar(value=True); self.re_prov_codcol = tk.StringVar(value="NIF"); self.re_prov_pref = tk.StringVar(value="400")
        self.re_gasto_def = tk.StringVar(value="62900000"); self.re_iva_def = tk.StringVar(value="47200000"); self.re_ret = tk.StringVar(value="47510000")

        ttk.Label(right, text="Editor (Recibidas)", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
self.re_override = tk.BooleanVar(value=False)

ttk.Checkbutton(right, text="Usar mapeo Excel propio (override)", variable=self.re_override).pack(anchor=tk.W, pady=(6,0))
ttk.Label(right, text="Mapeo Excel (JSON) — Clave→Letra").pack(anchor=tk.W)
self.re_excel = tk.Text(right, height=8); self.re_excel.pack(fill=tk.BOTH, expand=True)
        _mk_labeled_entry(right, "Nombre", self.re_nombre, 24)
        _mk_labeled_entry(right, "Dígitos plan", self.re_dig)
        ttk.Checkbutton(right, text="Proveedor por columna", variable=self.re_prov_col).pack(anchor=tk.W)
        _mk_labeled_entry(right, "Columna código proveedor", self.re_prov_codcol)
        _mk_labeled_entry(right, "Prefijo cuenta proveedor (400)", self.re_prov_pref)
        _mk_labeled_entry(right, "Gasto por defecto (6xx)", self.re_gasto_def)
        _mk_labeled_entry(right, "IVA soportado defecto (472)", self.re_iva_def)
        _mk_labeled_entry(right, "Retenciones IRPF (4751)", self.re_ret)

        ttk.Checkbutton(right, text="Usar mapeo Excel propio (override)", variable=tk.BooleanVar(value=False), command=lambda: None).pack(anchor=tk.W, pady=(6,0))
        ttk.Label(right, text="Tipos IVA (JSON)").pack(anchor=tk.W, pady=(6,0))
        self.re_tipos = tk.Text(right, height=5); self.re_tipos.pack(fill=tk.BOTH, expand=True)
        self.re_tipos.insert(tk.END, '[{"porcentaje":21,"cuenta_iva":"47200000"}]')

        self.tv_re.bind("<<TreeviewSelect>>", self._re_load_selected)

    def _re_refresh(self):
        self.tv_re.delete(*self.tv_re.get_children())
        for p in self.gestor.listar_recibidas(self.codigo):
            self.tv_re.insert("", tk.END, values=(p.get("nombre"), p.get("cuenta_proveedor_prefijo","400"), p.get("cuenta_iva_soportado_defecto","47200000")))

    def _re_load_selected(self, *_):
        sel = self.tv_re.selection()
        if not sel: return
        nombre, *_ = self.tv_re.item(sel[0], "values")
        p = next((x for x in self.gestor.listar_recibidas(self.codigo) if x.get("nombre")==nombre), None)
        if not p: return
        self.re_nombre.set(p.get("nombre",""))
        self.re_dig.set(str(p.get("digitos_plan",8)))
        self.re_prov_col.set(bool(p.get("proveedor_por_columna", True)))
        self.re_prov_codcol.set(p.get("col_proveedor_codigo","NIF"))
        self.re_prov_pref.set(p.get("cuenta_proveedor_prefijo","400"))
        self.re_gasto_def.set(p.get("cuenta_gasto_por_defecto","62900000"))
        self.re_iva_def.set(p.get("cuenta_iva_soportado_defecto","47200000"))
        self.re_ret.set(p.get("cuenta_retenciones_irpf","47510000"))
        self.re_tipos.delete("1.0", tk.END); self.re_tipos.insert(tk.END, json.dumps(p.get("tipos_iva", []), ensure_ascii=False))
        self.re_override.set(bool(p.get("excel_override", False)))
        self.re_excel.delete("1.0", tk.END); self.re_excel.insert(tk.END, json.dumps((p.get("excel") or {}).get("columnas", {}), ensure_ascii=False, indent=2))

    def _re_nuevo(self):
        self.re_nombre.set(""); self.re_dig.set("8"); self.re_prov_col.set(True); self.re_prov_codcol.set("NIF"); self.re_prov_pref.set("400"); self.re_gasto_def.set("62900000"); self.re_iva_def.set("47200000"); self.re_ret.set("47510000"); self.re_tipos.delete("1.0", tk.END); self.re_tipos.insert(tk.END, "[]")

    def _re_guardar(self):
        try:
            import json
            plantilla = {
                "codigo_empresa": self.codigo,
                "nombre": self.re_nombre.get().strip(),
                "digitos_plan": int(self.re_dig.get().strip() or "8"),
                "proveedor_por_columna": bool(self.re_prov_col.get()),
                "col_proveedor_codigo": self.re_prov_codcol.get().strip(),
                "cuenta_proveedor_prefijo": self.re_prov_pref.get().strip(),
                "cuenta_gasto_por_defecto": self.re_gasto_def.get().strip(),
                "cuenta_iva_soportado_defecto": self.re_iva_def.get().strip(),
                "cuenta_retenciones_irpf": self.re_ret.get().strip(),
                "tipos_iva": json.loads(self.re_tipos.get("1.0", tk.END) or "[]"),
                "soporta_retencion": True
            }
            
            if self.re_override.get():
                plantilla["excel_override"] = True
                plantilla["excel"] = plantilla.get("excel", {"{}":{}});
                import json as _json
                plantilla["excel"]["columnas"] = _json.loads(self.re_excel.get("1.0", tk.END) or "{}")
            else:
                plantilla["excel_override"] = False
            self.gestor.upsert_recibida(plantilla); self._re_refresh()
            messagebox.showinfo("Gest2Bank", "Plantilla guardada.")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))

    def _re_eliminar(self):
        sel = self.tv_re.selection()
        if not sel: return
        nombre, *_ = self.tv_re.item(sel[0], "values")
        self.gestor.eliminar_recibida(self.codigo, nombre); self._re_refresh()

def _build_excel_empresa(self, frame):
    import json
    left = ttk.Frame(frame); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
    right = ttk.Frame(frame); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    ttk.Label(left, text="Primera Fila Procesar (1=primera fila)", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
    self.emp_primera = tk.StringVar(value="2")
    e1 = ttk.Entry(left, textvariable=self.emp_primera, width=8); e1.pack(anchor=tk.W, pady=4)

    ttk.Label(left, text="Ignorar Filas (ej. Q=NOPROCESARFACTURA)").pack(anchor=tk.W)
    self.emp_ignorar = tk.StringVar()
    ttk.Entry(left, textvariable=self.emp_ignorar, width=40).pack(anchor=tk.W, pady=4)

    ttk.Label(left, text="Condición cuenta genérica (ej. D=PARTICULAR)").pack(anchor=tk.W)
    self.emp_generica = tk.StringVar()
    ttk.Entry(left, textvariable=self.emp_generica, width=40).pack(anchor=tk.W, pady=4)

    ttk.Label(right, text="Tabla mapeo columnas (Clave → Letra)").pack(anchor=tk.W)
    self.emp_map = tk.Text(right, height=18)
    self.emp_map.pack(fill=tk.BOTH, expand=True)

    # Load from gestor
    empresas = [e for e in self.gestor.listar_empresas() if e.get("codigo")==self.codigo]
    conf = (empresas[0].get("excel") if empresas else {}) or {}
    self.emp_primera.set(str(conf.get("primera_fila_procesar", 2)))
    self.emp_ignorar.set(conf.get("ignorar_filas",""))
    self.emp_generica.set(conf.get("condicion_cuenta_generica",""))
    self.emp_map.insert(tk.END, json.dumps(conf.get("columnas", {}), ensure_ascii=False, indent=2))

    ttk.Button(frame, text="Guardar configuración de empresa", command=lambda: self._excel_empresa_save()).pack(side=tk.BOTTOM, pady=6)

def _excel_empresa_save(self):
    import json
    empresas = [e for e in self.gestor.listar_empresas() if e.get("codigo")==self.codigo]
    if not empresas:
        from tkinter import messagebox
        messagebox.showerror("Gest2Bank","Empresa no encontrada"); return
    emp = empresas[0]
    emp["excel"] = {
        "primera_fila_procesar": int(self.emp_primera.get() or "2"),
        "ignorar_filas": self.emp_ignorar.get().strip(),
        "condicion_cuenta_generica": self.emp_generica.get().strip(),
        "columnas": json.loads(self.emp_map.get("1.0", tk.END) or "{}")
    }
    self.gestor.save()
    from tkinter import messagebox
    messagebox.showinfo("Gest2Bank","Configuración Excel de empresa guardada.")
