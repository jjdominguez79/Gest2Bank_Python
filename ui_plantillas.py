import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json

class UIPlantillas(ttk.Frame):
    def __init__(self, master, path_json: Path):
        super().__init__(master)
        self.path_json = Path(path_json)
        self.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(top, text="Fichero plantillas:").pack(side=tk.LEFT)
        self.path = tk.StringVar(value=str(self.path_json)); ttk.Entry(top, textvariable=self.path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(top, text="Cambiar…", command=self._choose).pack(side=tk.LEFT)

        self.text = tk.Text(self, height=28); self.text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        ttk.Button(self, text="Guardar", command=self._save).pack(pady=6)
        self._load()

    def _choose(self):
        fp = filedialog.askopenfilename(title="Selecciona JSON", filetypes=[("JSON",".json"),("Todos","*.*")])
        if fp:
            self.path.set(fp); self._load()

    def _load(self):
        p = Path(self.path.get())
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            txt = "{\n  \"extractos\": [],\n  \"facturas_emitidas\": [],\n  \"facturas_recibidas\": []\n}\n"
        self.text.delete("1.0", tk.END); self.text.insert(tk.END, txt)

    def _save(self):
        p = Path(self.path.get())
        try:
            data = json.loads(self.text.get("1.0", tk.END))
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            messagebox.showinfo("Gest2Bank", "Plantillas guardadas.")
        except Exception as e:
            messagebox.showerror("Gest2Bank", str(e))
