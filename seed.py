"""
Script para poblar la base de datos con datos iniciales.
Ejecutar una sola vez: python seed.py
"""
from app import create_app
from app.models import db, Rol, Usuario, Especialidad, Medico, Paciente, Medicamento
from datetime import date

app = create_app('development')

with app.app_context():
    db.create_all()

    # ─── Roles ───────────────────────────────────────
    roles_data = [
        ('admin',       'Administrador del sistema'),
        ('medico',      'Médico de la clínica'),
        ('recepcion',   'Personal de recepción'),
    ]
    roles = {}
    for nombre, desc in roles_data:
        r = Rol.query.filter_by(nombre=nombre).first()
        if not r:
            r = Rol(nombre=nombre, descripcion=desc)
            db.session.add(r)
            db.session.flush()
        roles[nombre] = r

    # ─── Usuarios ─────────────────────────────────────
    def crear_usuario(nombre, apellido, email, password, rol_nombre):
        if not Usuario.query.filter_by(email=email).first():
            u = Usuario(nombre=nombre, apellido=apellido,
                        email=email, rol_id=roles[rol_nombre].id)
            u.set_password(password)
            db.session.add(u)
            return u
        return Usuario.query.filter_by(email=email).first()

    admin_u  = crear_usuario('Carlos',  'Mamani',  'admin@clinica.com',      'admin123',   'admin')
    med1_u   = crear_usuario('María',   'Quispe',  'mquispe@clinica.com',    'medico123',  'medico')
    med2_u   = crear_usuario('Roberto', 'Flores',  'rflores@clinica.com',    'medico123',  'medico')
    recep_u  = crear_usuario('Ana',     'Torrez',  'atorrez@clinica.com',    'recep123',   'recepcion')
    db.session.flush()

    # ─── Especialidades ───────────────────────────────
    esps = [
        ('Medicina General',    'Atención primaria y consulta general'),
        ('Pediatría',           'Atención médica a niños y adolescentes'),
        ('Cardiología',         'Diagnóstico y tratamiento del corazón'),
        ('Ginecología',         'Salud reproductiva femenina'),
        ('Traumatología',       'Sistema musculoesquelético'),
    ]
    esp_objs = {}
    for nombre, desc in esps:
        e = Especialidad.query.filter_by(nombre=nombre).first()
        if not e:
            e = Especialidad(nombre=nombre, descripcion=desc)
            db.session.add(e)
            db.session.flush()
        esp_objs[nombre] = e

    # ─── Médicos ──────────────────────────────────────
    if med1_u and not med1_u.medico:
        m1 = Medico(matricula='MED-001', telefono='72345678',
                    consultorio='Consultorio 1',
                    usuario_id=med1_u.id,
                    especialidad_id=esp_objs['Medicina General'].id)
        db.session.add(m1)

    if med2_u and not med2_u.medico:
        m2 = Medico(matricula='MED-002', telefono='79876543',
                    consultorio='Consultorio 2',
                    usuario_id=med2_u.id,
                    especialidad_id=esp_objs['Pediatría'].id)
        db.session.add(m2)

    # ─── Pacientes ────────────────────────────────────
    pacientes_data = [
        ('Juan',    'Pérez',    '1234567',  date(1985, 3, 15), 'M', '71234567', 'A+'),
        ('Laura',   'Gómez',    '2345678',  date(1992, 7, 22), 'F', '72345678', 'O+'),
        ('Miguel',  'Salinas',  '3456789',  date(1978, 11, 5), 'M', '73456789', 'B-'),
        ('Sofia',   'Vargas',   '4567890',  date(2001, 4, 18), 'F', '74567890', 'AB+'),
    ]
    for nombre, apellido, ci, fnac, sexo, tel, sg in pacientes_data:
        if not Paciente.query.filter_by(ci=ci).first():
            p = Paciente(nombre=nombre, apellido=apellido, ci=ci,
                         fecha_nacimiento=fnac, sexo=sexo,
                         telefono=tel, grupo_sanguineo=sg)
            db.session.add(p)

    # ─── Medicamentos ─────────────────────────────────
    meds_data = [
        ('Paracetamol',  'Paracetamol',   'Tab 500mg'),
        ('Ibuprofeno',   'Ibuprofeno',    'Tab 400mg'),
        ('Amoxicilina',  'Amoxicilina',   'Cáps 500mg'),
        ('Loratadina',   'Loratadina',    'Tab 10mg'),
        ('Omeprazol',    'Omeprazol',     'Cáps 20mg'),
    ]
    for nombre, principio, presentacion in meds_data:
        if not Medicamento.query.filter_by(nombre=nombre).first():
            m = Medicamento(nombre=nombre, principio_activo=principio, presentacion=presentacion)
            db.session.add(m)

    db.session.commit()
    print("✅ Base de datos inicializada correctamente.")
    print("\nCuentas creadas:")
    print("  admin@clinica.com      → admin123   (Administrador)")
    print("  mquispe@clinica.com    → medico123  (Médico)")
    print("  rflores@clinica.com    → medico123  (Médico)")
    print("  atorrez@clinica.com    → recep123   (Recepción)")
