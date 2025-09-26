from datetime import datetime
from decimal import Decimal
from facturas_common import Linea, d2, cuenta_por_porcentaje, formar_tercero

def generar_asiento_emitida(row, conf) -> list[Linea]:
    fecha = row["Fecha"]
    desc = str(row.get("Descripcion",""))
    base = d2(row.get("Base", 0))
    iva_pct = float(row.get("IVA_pct", 21))
    cuota_iva = d2(row.get("CuotaIVA", base * Decimal(iva_pct/100)))
    ret = d2(row.get("CuotaRetencion", 0))
    total = d2(row.get("Total", base + cuota_iva - ret))

    c_cliente = formar_tercero(conf.get("cuenta_cliente_prefijo","430"), row.get(conf.get("col_cliente_codigo","NIF"), ""), conf.get("digitos_plan",8)) if conf.get("cliente_por_columna") else "43000000"
    # ingreso por comodín omitido aquí; usamos por defecto
    c_ingreso = conf.get("cuenta_ingreso_por_defecto","70000000")
    c_iva = cuenta_por_porcentaje(conf.get("tipos_iva", []), iva_pct, conf.get("cuenta_iva_repercutido_defecto","47700000"))
    c_ret = conf.get("cuenta_retenciones_irpf","47510000")

    lineas = []
    # Cliente (Debe): Total - Retención
    lineas.append(Linea(fecha, c_cliente, "D", total - ret, desc))
    # Ingreso (Haber): Base
    if base != d2(0):
        lineas.append(Linea(fecha, c_ingreso, "H", base, desc))
    # IVA (Haber): Cuota IVA
    if cuota_iva != d2(0):
        lineas.append(Linea(fecha, c_iva, "H", cuota_iva, desc))
    # Retención (Haber)
    if ret != d2(0) and conf.get("soporta_retencion", True):
        lineas.append(Linea(fecha, c_ret, "H", ret, desc))
    return lineas
