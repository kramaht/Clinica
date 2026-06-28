from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ─────────────────────────────────────────────
# TABLA 1: Roles
# ─────────────────────────────────────────────
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    # Relaciones
    usuarios = db.relationship('Usuario', back_populates='rol', lazy='dynamic')

    def __repr__(self):
        return f'<Rol {self.nombre}>'

# ─────────────────────────────────────────────
# TABLA 2: Usuarios
# ─────────────────────────────────────────────
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    # Relaciones
    rol = db.relationship('Rol', back_populates='usuarios')
    medico = db.relationship('Medico', back_populates='usuario', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def tiene_rol(self, nombre_rol):
        return self.rol.nombre == nombre_rol

    def __repr__(self):
        return f'<Usuario {self.email}>'

# ─────────────────────────────────────────────
# TABLA 3: Especialidades
# ─────────────────────────────────────────────
class Especialidad(db.Model):
    __tablename__ = 'especialidades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    # Relaciones
    medicos = db.relationship('Medico', back_populates='especialidad', lazy='dynamic')

    def __repr__(self):
        return f'<Especialidad {self.nombre}>'

# ─────────────────────────────────────────────
# TABLA 4: Médicos
# ─────────────────────────────────────────────
class Medico(db.Model):
    __tablename__ = 'medicos'
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    consultorio = db.Column(db.String(50))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='medico')
    especialidad = db.relationship('Especialidad', back_populates='medicos')
    citas = db.relationship('Cita', back_populates='medico', lazy='dynamic')
    consultas = db.relationship('Consulta', back_populates='medico', lazy='dynamic')
    horarios = db.relationship('HorarioMedico', back_populates='medico', lazy='dynamic')

    @property
    def nombre_completo(self):
        return self.usuario.nombre_completo

    def __repr__(self):
        return f'<Medico {self.matricula}>'

# ─────────────────────────────────────────────
# TABLA 5: Pacientes
# ─────────────────────────────────────────────
class Paciente(db.Model):
    __tablename__ = 'pacientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)  # M / F
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(150))
    direccion = db.Column(db.Text)
    grupo_sanguineo = db.Column(db.String(5))
    alergias = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    # Relaciones
    citas = db.relationship('Cita', back_populates='paciente', lazy='dynamic')
    consultas = db.relationship('Consulta', back_populates='paciente', lazy='dynamic')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def edad(self):
        hoy = datetime.today().date()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __repr__(self):
        return f'<Paciente {self.ci}>'

# ─────────────────────────────────────────────
# TABLA 6: HorariosMedico
# ─────────────────────────────────────────────
class HorarioMedico(db.Model):
    __tablename__ = 'horarios_medico'
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lun … 6=Dom
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    # Relaciones
    medico = db.relationship('Medico', back_populates='horarios')

    DIAS = {0:'Lunes',1:'Martes',2:'Miércoles',3:'Jueves',4:'Viernes',5:'Sábado',6:'Domingo'}

    @property
    def dia_nombre(self):
        return self.DIAS.get(self.dia_semana, '')

    def __repr__(self):
        return f'<Horario médico {self.medico_id} día {self.dia_semana}>'

# ─────────────────────────────────────────────
# TABLA 7: Citas
# ─────────────────────────────────────────────
class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    # pendiente | confirmada | completada | cancelada
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    # Relaciones
    paciente = db.relationship('Paciente', back_populates='citas')
    medico = db.relationship('Medico', back_populates='citas')
    consulta = db.relationship('Consulta', back_populates='cita', uselist=False)

    ESTADOS_BADGE = {
        'pendiente': 'warning',
        'confirmada': 'primary',
        'completada': 'success',
        'cancelada': 'danger',
    }

    @property
    def badge_color(self):
        return self.ESTADOS_BADGE.get(self.estado, 'secondary')

    def __repr__(self):
        return f'<Cita {self.id} {self.fecha_hora}>'

# ─────────────────────────────────────────────
# TABLA 8: Consultas (historial clínico)
# ─────────────────────────────────────────────
class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo_consulta = db.Column(db.Text, nullable=False)
    sintomas = db.Column(db.Text)
    diagnostico = db.Column(db.Text, nullable=False)
    tratamiento = db.Column(db.Text)
    peso = db.Column(db.Float)
    talla = db.Column(db.Float)
    presion_arterial = db.Column(db.String(20))
    temperatura = db.Column(db.Float)
    frecuencia_cardiaca = db.Column(db.Integer)
    observaciones = db.Column(db.Text)
    # Relaciones
    paciente = db.relationship('Paciente', back_populates='consultas')
    medico = db.relationship('Medico', back_populates='consultas')
    cita = db.relationship('Cita', back_populates='consulta')
    recetas = db.relationship('Receta', back_populates='consulta', lazy='dynamic')

    def __repr__(self):
        return f'<Consulta {self.id}>'

# ─────────────────────────────────────────────
# TABLA 9: Medicamentos
# ─────────────────────────────────────────────
class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    principio_activo = db.Column(db.String(200))
    presentacion = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    # Relaciones
    recetas = db.relationship('Receta', back_populates='medicamento', lazy='dynamic')

    def __repr__(self):
        return f'<Medicamento {self.nombre}>'

# ─────────────────────────────────────────────
# TABLA 10: Recetas
# ─────────────────────────────────────────────
class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    dosis = db.Column(db.String(100), nullable=False)
    frecuencia = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.String(100))
    indicaciones = db.Column(db.Text)
    # Relaciones
    consulta = db.relationship('Consulta', back_populates='recetas')
    medicamento = db.relationship('Medicamento', back_populates='recetas')

    def __repr__(self):
        return f'<Receta {self.id}>'
