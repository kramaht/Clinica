# 🏥 ClinicaMed — Sistema de Gestión de Clínica Médica

**TEM-742 · Tecnologías Emergentes II · Proyecto I-2026**

Aplicación web desarrollada con **Python + Flask** aplicando el patrón **Application Factory**.

---

## 📋 Estructura del proyecto

```
clinica/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── models.py            # 10 modelos / tablas
│   ├── auth/                # Autenticación (login/logout)
│   ├── admin/               # Dashboard, usuarios, especialidades, medicamentos
│   ├── pacientes/           # CRUD pacientes + historial
│   ├── medicos/             # CRUD médicos + horarios
│   ├── citas/               # CRUD citas + gestión de estados
│   ├── consultas/           # CRUD consultas + recetas
│   └── templates/
│       ├── layouts/base.html
│       ├── auth/
│       ├── admin/
│       ├── pacientes/
│       ├── medicos/
│       ├── citas/
│       └── consultas/
├── config.py
├── run.py
├── seed.py
└── requirements.txt
```

---

## 🗃️ Modelo de base de datos (10 tablas)

| # | Tabla | Descripción |
|---|-------|-------------|
| 1 | `roles` | Roles del sistema (admin, médico, recepción) |
| 2 | `usuarios` | Cuentas de acceso con autenticación |
| 3 | `especialidades` | Especialidades médicas disponibles |
| 4 | `medicos` | Perfil médico vinculado a un usuario |
| 5 | `pacientes` | Registro de pacientes |
| 6 | `horarios_medico` | Horarios de atención por médico |
| 7 | `citas` | Agenda de citas médicas |
| 8 | `consultas` | Historial clínico / consultas realizadas |
| 9 | `medicamentos` | Catálogo de medicamentos |
| 10 | `recetas` | Recetas emitidas por consulta |

---

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd clinica
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

### 5. Crear la base de datos
```sql
-- En psql:
CREATE DATABASE clinica_db;
```

### 6. Inicializar tablas y datos de prueba
```bash
python seed.py
```

### 7. Ejecutar la aplicación
```bash
python run.py
```
Abrir: http://localhost:5000

---

## 👤 Cuentas de acceso iniciales

| Correo | Contraseña | Rol |
|--------|-----------|-----|
| admin@clinica.com | admin123 | Administrador |
| mquispe@clinica.com | medico123 | Médico |
| rflores@clinica.com | medico123 | Médico |
| atorrez@clinica.com | recep123 | Recepción |

---

## 🚀 Despliegue en Render

1. Crear un servicio Web en [render.com](https://render.com)
2. Configurar variables de entorno: `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`
3. Build Command: `pip install -r requirements.txt && python seed.py`
4. Start Command: `gunicorn run:app`

> Agregar `gunicorn` a `requirements.txt` para producción.

---

## 🛠️ Tecnologías

- **Backend:** Python 3.11+, Flask 3.1, Flask-Login, Flask-SQLAlchemy, Flask-Migrate
- **Base de datos:** PostgreSQL
- **Frontend:** Bootstrap 5.3, Bootstrap Icons
- **Autenticación:** Flask-Login + Werkzeug (hash bcrypt)
- **Patrón:** Application Factory con Blueprints
