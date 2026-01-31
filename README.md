# 🏦 Cajero Automático Pro1 - Terminal Edition

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=for-the-badge&logo=sqlite)

Un sistema de cajero automático robusto con interfaz estética de terminal retro. Este proyecto aplica conceptos avanzados de **Programación Orientada a Objetos (POO)**, persistencia de datos segura y una arquitectura cliente-servidor moderna.



## 🚀 Características

- **Seguridad Bancaria:** Hashing de PINs con `werkzeug.security` (nunca guardamos texto plano).
- **Gestión de Sesiones:** Uso de `flask.session` para mantener la identidad del usuario.
- **Operaciones Atómicas:** Transferencias entre cuentas con validación de fondos y rollback en caso de error.
- **Interfaz "Matrix":** Diseño retro responsivo con animaciones CSS y actualizaciones dinámicas vía Fetch API (AJAX).
- **Historial Detallado:** Registro automático de cada movimiento (Retiros, Depósitos, Transferencias).

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3 + Flask.
* **Base de Datos:** SQLite3 con diseño relacional.
* **Frontend:** HTML5, CSS3 (Estilo Custom Terminal), JavaScript Vanilla.
* **Seguridad:** PBKDF2 con Salt para contraseñas.

## 📦 Estructura del Proyecto

```text
├── app.py              # Rutas de Flask y control de sesiones
├── database.py         # Configuración de SQLite y gestión de datos
├── models.py           # Clases POO (Cuenta, CuentaAhorros, CuentaCorriente)
├── static/
│   ├── css/style.css   # Estilo Matrix / Terminal Retro
│   └── js/main.js      # Lógica del cliente y Fetch API
├── templates/
│   └── index.html      # Estructura principal
└── cajero.db           # Base de Datos (se genera al iniciar)



## ⚙️ Instalación y Configuración

Sigue estos pasos para ejecutar el entorno localmente:

### 1. Clonar el repositorio
```bash
git clone https://github.com/Andersonquin/CajeroPro1.git
cd CajeroPro1

2. Configurar el entorno virtual (Recomendado)
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

3. Instalar dependencias
pip install flask werkzeug

4. Inicializar la Base de Datos 🛠️
Este paso es crucial. Ejecuta el script para crear las tablas y generar los hashes de seguridad iniciales:

python database.py


5. Ejecutar la aplicación

python3 app.py


