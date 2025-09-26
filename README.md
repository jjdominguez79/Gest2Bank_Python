# Gest2Bank – Flujo por Empresa

Flujo rediseñado:
1) Seleccionas la **empresa**.
2) Ves/editar **plantillas** de esa empresa (Bancos, Emitidas, Recibidas) en una sola pantalla.
3) Eliges **qué enlace** quieres generar (Bancos o Facturas) y la **plantilla** de esa empresa.
4) Importes en fichero **siempre positivos**; el D/H define el sentido.
5) El nombre del fichero generado es **`<codigo_empresa>.dat`**.

## Requisitos
```bash
pip install -r requirements.txt
```

## Ejecutar
```bash
python main.py
```

## Notas
- Plantillas en `plantillas/plantillas.json` con una sección `empresas` y tres listas: `bancos`, `facturas_emitidas`, `facturas_recibidas`.
- Edición de plantillas **integrada** en la UI (sin ventanas emergentes).
