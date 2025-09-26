# Gest2Bank (Extendido)

Generación de `suenlace.dat` para **extractos bancarios** y **facturas (emitidas/recibidas)**.

## Novedades
- Importes en salida **siempre positivos**; el sentido contable lo marca `D/H`.
- Nombre de fichero de salida = **`<codigo_empresa>.dat`**.
- Nuevas pantallas: Facturas → Emitidas / Recibidas.
- Plantillas ampliadas: `facturas_emitidas` y `facturas_recibidas` en `plantillas/plantillas.json`.

## Requisitos
```
pip install pandas openpyxl Pillow
```

## Ejecutar
```
python main.py
```

## Excel esperado
Columnas: `Fecha, Serie, Número, NIF, Nombre, Base, IVA_pct, CuotaIVA, Retencion_pct, CuotaRetencion, Total, Descripcion` (los nombres pueden variar; se normalizan).

## Salida
- Extractos: pares `I/U` por movimiento.
- Facturas: formato tabular `T` (una línea por cuenta). Puedes adaptar el render si necesitas `I/U`.
