import json
from pathlib import Path

class GestorPlantillas:
    def __init__(self, path_json: Path):
        self.path = Path(path_json)
        self.data = {}
        self._load()

    def _load(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text('{"extractos":[],"facturas_emitidas":[],"facturas_recibidas":[]}', encoding="utf-8")
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def listar_extractos(self):
        return self.data.get("extractos", [])

    def listar_emitidas(self):
        return self.data.get("facturas_emitidas", [])

    def listar_recibidas(self):
        return self.data.get("facturas_recibidas", [])

    def buscar_extracto(self, codigo, banco):
        for p in self.listar_extractos():
            if p.get("codigo_empresa")==codigo and p.get("banco")==banco:
                return p
        return None

    def buscar_emitidas(self, codigo):
        for p in self.listar_emitidas():
            if p.get("codigo_empresa")==codigo:
                return p
        return None

    def buscar_recibidas(self, codigo):
        for p in self.listar_recibidas():
            if p.get("codigo_empresa")==codigo:
                return p
        return None
