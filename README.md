# Gest2Bank

**Gest2Bank** es una aplicación de escritorio en Python para generar ficheros `suenlace.dat` compatibles con A3ECO a partir de extractos bancarios en formato Excel.  
Permite gestionar múltiples plantillas de importación, configurar subcuentas por defecto, asociar conceptos a subcuentas específicas y seleccionar fácilmente la hoja y los datos a procesar.

---

## 🚀 Funcionalidades principales
- **Gestión de plantillas**:
  - Crear, modificar y eliminar plantillas de importación.
  - Definir subcuentas de banco y subcuentas por defecto.
  - Asignar conceptos predefinidos a subcuentas mediante comodines (`*texto*`).
  - Configurar número de dígitos del plan contable.

- **Generación de ficheros `suenlace.dat`**:
  - Seleccionar plantilla y archivo Excel.
  - Elegir la hoja del libro y vista previa de los datos.
  - Validación automática de subcuentas y formato de fecha `AAAAMMDD`.
  - Posibilidad de guardar el fichero en la ubicación deseada con el código de empresa en el nombre.

- **Diseño moderno** con barra lateral y pantallas integradas.

---

## 📦 Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/jjdominguez79/Gest2Bank_Python.git
   cd Gest2Bank_Python
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

---

## 🛠 Requisitos
- Python 3.9 o superior.
- Librerías Python:
  - `pandas`
  - `openpyxl`
  - `Pillow`
  - `ttkbootstrap`

Instalación rápida:
```bash
pip install pandas openpyxl Pillow ttkbootstrap
```

---

## 📂 Estructura del proyecto
```
Gest2Bank_Python/
│
├── main.py                # Entrada principal de la aplicación
├── ui_inicio.py           # Pantalla de inicio
├── ui_plantillas.py       # Gestión de plantillas
├── ui_generacion.py       # Generación del fichero suenlace.dat
├── gestor_plantillas.py   # Funciones para cargar y guardar plantillas
├── generador_suenlace.py  # Lógica de generación del fichero
├── resources/             # Carpeta de imágenes y logos
│   ├── logo.png
│   └── icon.ico
├── config.json            # Ruta actual de las plantillas
├── README.md
└── .gitignore
```

---

## 📌 Notas
- El archivo de plantillas puede estar en una carpeta compartida en red para uso multiusuario.
- Si no existe un archivo de plantillas al iniciar, la aplicación creará uno de ejemplo automáticamente.
- El icono del ejecutable y el logotipo de la app son personalizables.

---

## 📜 Licencia
Este proyecto es privado y su distribución está restringida a los usuarios autorizados por **Gestinem Fiscal**.
