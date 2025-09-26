from datetime import datetime
from decimal import Decimal
from facturas_common import Linea, d2, cuenta_por_porcentaje, formar_tercero

def generar_asiento_recibida(row, conf) -> list[Linea]:
    fecha = row["Fecha"]
    desc = str(row.get("Descripcion",""))
    base = d2(row.get("Base", 0))
    iva_pct = float(row.get("IVA_pct", 21))
    cuota_iva = d2(row.get("CuotaIVA", base * Decimal(iva_pct/100)))
    ret = d2(row.get("CuotaRetencion", 0))
    total = d2(row.get("Total", base + cuota_iva - ret))

    c_prov = formar_tercero(conf.get("cuenta_proveedor_prefijo","400"), row.get(conf.get("col_proveedor_codigo","NIF"), ""), conf.get("digitos_plan",8)) if conf.get("proveedor_por_columna") else "40000000"
    c_gasto = conf.get("cuenta_gasto_por_defecto","62900000")
    c_iva = cuenta_por_porcentaje(conf.get("tipos_iva", []), iva_pct, conf.get("cuenta_iva_soportado_defecto","47200000"))
    c_ret = conf.get("cuenta_retenciones_irpf","47510000")

    lineas = []
    # Gasto (Debe): Base
    if base != d2(0):
        lineas.append(Linea(fecha, c_gasto, "D", base, desc))
    # IVA soportado (Debe): cuota
    if cuota_iva != d2(0):
        lineas.append(Linea(fecha, c_iva, "D", cuota_iva, desc))
    # Proveedor (Haber): Total - Retención
    lineas.append(Linea(fecha, c_prov, "H", total - ret, desc))
    # Retención (Haber)
    if ret != d2(0) and conf.get("soporta_retencion", True):
        lineas.append(Linea(fecha, c_ret, "H", ret, desc))
    return lineas
