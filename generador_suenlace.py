from fnmatch import fnmatch
from utilidades import columna_a_indice, normaliza_fecha, limpia_texto, pad_subcuenta

def _valor(row, col_spec):
    idx = columna_a_indice(col_spec)
    if idx is not None:
        try:
            return row.iloc[idx]
        except:
            return ""
    return row.get(col_spec, "")

def _subcuenta_por_concepto(conceptos, texto):
    txt = str(texto).lower()
    for c in conceptos or []:
        filtro = str(c.get("filtro","")).lower()
        if not filtro:
            continue
        # soporta * comodín y también % como comodín
        patron = filtro.replace("%", "*")
        if fnmatch(txt, patron) or filtro.strip("*") in txt:
            return c.get("subcuenta","").strip()
    return None

def _formatea_importe(valor):
    # +0000001000.00 (signo + 10 enteros + . + 2 decimales)
    try:
        v = float(str(valor).replace(",", "."))
    except:
        v = 0.0
    sign = "+" if v >= 0 else "-"
    v = abs(v)
    entero = int(v)
    dec = int(round((v - entero) * 100))
    return f"{sign}{entero:010d}.{dec:02d}"

def _record_tipo0(
    codigo_empresa, fecha_yyyymmdd, cuenta, desc_cuenta,
    tipo_importe, ref_doc, linea_IMU, desc_apunte, importe_txt,
    moneda="E", analitico=" ", generado="N"
):
    """
    Construye un registro TIPO 0 (Alta de apuntes sin IVA) EXACTO de 256 bytes.
    Posiciones (1-based):
      1:  '4'
      2-6:  código empresa (5)
      7-14: fecha (8) AAAAMMDD
     15:  '0'
     16-27: cuenta (12) (nivel 6 a 12)  -> contenido + espacios a la derecha
     28-57: desc cuenta (30)
     58:   tipo importe ('D'/'H')
     59-68: referencia doc (10)
     69:   línea (I/M/U)
     70-99: desc apunte (30)
    100-113: importe (14) +0000000000.00
    114-251: relleno espacios (138)
    252:     analítico ('S' o espacio)
    253:     moneda ('E'/'P')
    254:     generado ('N')
    255-256: CRLF
    """
    def fit(s, n):
        return (s or "")[:n].ljust(n, " ")

    # Construcción por secciones
    partes = []
    partes.append("4")                                             # 1
    partes.append(fit(codigo_empresa, 5))                         # 2-6
    partes.append(fit(fecha_yyyymmdd, 8))                         # 7-14
    partes.append("0")                                            # 15
    partes.append(fit(cuenta, 12))                                # 16-27
    partes.append(fit(desc_cuenta, 30))                           # 28-57
    partes.append(tipo_importe if tipo_importe in ("D","H") else "D")  # 58
    partes.append(fit(ref_doc, 10))                               # 59-68
    partes.append(linea_IMU if linea_IMU in ("I","M","U") else "I")    # 69
    partes.append(fit(desc_apunte, 30))                           # 70-99
    partes.append(fit(importe_txt, 14))                           # 100-113
    partes.append(" " * 138)                                      # 114-251
    partes.append(analitico if analitico in ("S"," ") else " ")   # 252
    partes.append(moneda if moneda in ("E","P") else "E")         # 253
    partes.append(generado if generado else "N")                  # 254

    linea = "".join(partes)
    # Asegurar longitud 254 antes de CRLF
    if len(linea) != 254:
        # recorta o rellena por si acaso
        linea = (linea[:254]).ljust(254, " ")
    return linea + "\r\n"  # 255-256 CRLF

def generar_suenlace(plantilla, df, ruta_salida):
    # Campos de la plantilla
    col_f = plantilla.get("columna_fecha","")
    col_i = plantilla.get("columna_importe","")
    col_c = plantilla.get("columna_concepto","")
    fila_ini = int(plantilla.get("fila_inicio","1") or "1")
    dig = int(plantilla.get("digitos_subcuenta","10") or "10")

    empresa = str(plantilla.get("codigo_empresa","")).zfill(5)
    sub_banco = pad_subcuenta(plantilla.get("subcuenta_banco",""), dig)
    sub_default = pad_subcuenta(plantilla.get("subcuenta_default",""), dig)
    desc_cuenta_banco = (plantilla.get("nombre_banco") or "BANCO")[:30]
    conceptos = plantilla.get("conceptos", [])

    lineas = []

    for _, row in df.iloc[fila_ini-1:].iterrows():
        fecha_raw = _valor(row, col_f)
        fecha = normaliza_fecha(fecha_raw)  # AAAAMMDD
        importe_raw = _valor(row, col_i)
        concepto_raw = _valor(row, col_c)
        concepto = limpia_texto(concepto_raw)[:30]

        if not fecha or str(importe_raw).strip() == "":
            continue

        # Importe y signo para decidir D/H
        try:
            imp_float = float(str(importe_raw).replace(",", "."))
        except:
            imp_float = 0.0

        # Subcuenta contrapartida por concepto o por defecto
        sub_contra = _subcuenta_por_concepto(conceptos, concepto_raw) or sub_default
        sub_contra = pad_subcuenta(sub_contra, dig)

        importe_txt = _formatea_importe(imp_float)

        # D/H: si el importe es positivo, banco al DEBE y contrapartida al HABER (y viceversa)
        tipo_banco = "D" if imp_float >= 0 else "H"
        tipo_contra = "H" if tipo_banco == "D" else "D"

        # Referencia doc (vacía o pon aquí algo como fecha o secuencia si quieres)
        ref_doc = ""

        # Registro 1: línea I (Banco)
        linea1 = _record_tipo0(
            codigo_empresa=empresa,
            fecha_yyyymmdd=fecha,
            cuenta=sub_banco,
            desc_cuenta=desc_cuenta_banco,
            tipo_importe=tipo_banco,
            ref_doc=ref_doc,
            linea_IMU="I",
            desc_apunte=concepto,
            importe_txt=importe_txt,
            moneda="E",
            analitico=" ",
            generado="N",
        )

        # Registro 2: línea U (Contrapartida)
        linea2 = _record_tipo0(
            codigo_empresa=empresa,
            fecha_yyyymmdd=fecha,
            cuenta=sub_contra,
            desc_cuenta="CONTRAPARTIDA",
            tipo_importe=tipo_contra,
            ref_doc=ref_doc,
            linea_IMU="U",
            desc_apunte=concepto,
            importe_txt=importe_txt,
            moneda="E",
            analitico=" ",
            generado="N",
        )

        lineas.append(linea1)
        lineas.append(linea2)

    # Escribir con CRLF, sin BOM
    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        for l in lineas:
            f.write(l)
