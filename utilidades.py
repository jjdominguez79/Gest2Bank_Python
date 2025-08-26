
import string
from datetime import datetime

def columna_a_indice(col):
    # Soporta A, B, C ... y nombres de columna
    if not col:
        return None
    c = col.strip().upper()
    if c.isalpha():
        # A -> índice 0, B -> 1, etc.
        idx = 0
        for i, ch in enumerate(reversed(c)):
            idx += (string.ascii_uppercase.index(ch) + 1) * (26 ** i)
        return idx - 1
    return None  # indica que no es letra, sino nombre de columna

def normaliza_fecha(valor):
    """ Devuelve YYYYMMDD robusto. Acepta:
        - pandas.Timestamp
        - 'dd/mm/aaaa', 'd/m/aa'
        - 'aaaa-mm-dd'
        - 'yyyymmdd'
        - otros: intenta parsear con heurística
    """
    if valor is None:
        return ""
    s = str(valor).strip()
    # pandas Timestamp -> strftime
    try:
        if hasattr(valor, "strftime"):
            return valor.strftime("%Y%m%d")
    except:
        pass

    # yyyymmdd directo
    if s.isdigit() and len(s) == 8 and s.startswith(("19","20")):
        return s

    # dd/mm/aaaa o dd/mm/aa
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 3:
            d, m, y = parts
            d = d.zfill(2)
            m = m.zfill(2)
            if len(y) == 2:
                y = "20" + y  # heurística siglo 2000+
            return f"{y}{m}{d}"

    # aaaa-mm-dd
    if "-" in s and len(s.split("-")) == 3:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
            return dt.strftime("%Y%m%d")
        except:
            pass

    # último intento
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(s[:10], fmt).strftime("%Y%m%d")
        except:
            continue
    return s  # peor caso

def limpia_texto(t):
    return str(t).replace("\n"," ").replace("\r"," ").strip()

def pad_subcuenta(sc, digitos):
    sc = str(sc).strip()
    if len(sc) < digitos:
        sc = sc.zfill(digitos)
    return sc[:digitos]
