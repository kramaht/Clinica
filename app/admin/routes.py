from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from . import admin
from ..models import db, Usuario, Rol, Especialidad, Medicamento, Paciente, Medico, Cita, Consulta
from datetime import datetime, date

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.tiene_rol('admin'):
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated

# ── Dashboard ──────────────────────────────────────────
@admin.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'pacientes': Paciente.query.filter_by(activo=True).count(),
        'medicos': Medico.query.filter_by(activo=True).count(),
        'citas_hoy': Cita.query.filter(
            db.func.date(Cita.fecha_hora) == date.today()
        ).count(),
        'consultas_mes': Consulta.query.filter(
            db.func.extract('month', Consulta.fecha) == datetime.now().month,
            db.func.extract('year', Consulta.fecha) == datetime.now().year,
        ).count(),
    }
    citas_recientes = Cita.query.order_by(Cita.fecha_hora.desc()).limit(8).all()
    # Estadísticas por especialidad
    especialidades_stats = db.session.query(
        Especialidad.nombre,
        db.func.count(Medico.id).label('total')
    ).join(Medico, Medico.especialidad_id == Especialidad.id, isouter=True)\
     .filter(Especialidad.activa == True)\
     .group_by(Especialidad.id, Especialidad.nombre).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           citas_recientes=citas_recientes,
                           especialidades_stats=especialidades_stats)

# ── Usuarios ───────────────────────────────────────────
@admin.route('/usuarios')
@login_required
@admin_required
def usuarios():
    lista = Usuario.query.order_by(Usuario.nombre).all()
    roles = Rol.query.all()
    return render_template('admin/usuarios.html', usuarios=lista, roles=roles)

@admin.route('/usuarios/crear', methods=['POST'])
@login_required
@admin_required
def crear_usuario():
    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    rol_id = request.form.get('rol_id')

    if not all([nombre, apellido, email, password, rol_id]):
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('admin.usuarios'))
    if Usuario.query.filter_by(email=email).first():
        flash('Ya existe un usuario con ese correo.', 'error')
        return redirect(url_for('admin.usuarios'))

    u = Usuario(nombre=nombre, apellido=apellido, email=email, rol_id=int(rol_id))
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f'Usuario {u.nombre_completo} creado.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin.route('/usuarios/<int:id>/toggle')
@login_required
@admin_required
def toggle_usuario(id):
    u = Usuario.query.get_or_404(id)
    if u.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'error')
    else:
        u.activo = not u.activo
        db.session.commit()
        flash(f'Usuario {"activado" if u.activo else "desactivado"}.', 'success')
    return redirect(url_for('admin.usuarios'))

# ── Especialidades ─────────────────────────────────────
@admin.route('/especialidades')
@login_required
@admin_required
def especialidades():
    lista = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template('admin/especialidades.html', especialidades=lista)

@admin.route('/especialidades/crear', methods=['POST'])
@login_required
@admin_required
def crear_especialidad():
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return redirect(url_for('admin.especialidades'))
    if Especialidad.query.filter_by(nombre=nombre).first():
        flash('Ya existe esa especialidad.', 'error')
        return redirect(url_for('admin.especialidades'))
    e = Especialidad(nombre=nombre, descripcion=descripcion)
    db.session.add(e)
    db.session.commit()
    flash(f'Especialidad "{nombre}" creada.', 'success')
    return redirect(url_for('admin.especialidades'))

@admin.route('/especialidades/<int:id>/toggle')
@login_required
@admin_required
def toggle_especialidad(id):
    e = Especialidad.query.get_or_404(id)
    e.activa = not e.activa
    db.session.commit()
    flash(f'Especialidad {"activada" if e.activa else "desactivada"}.', 'success')
    return redirect(url_for('admin.especialidades'))

# ── Medicamentos ───────────────────────────────────────
@admin.route('/medicamentos')
@login_required
@admin_required
def medicamentos():
    lista = Medicamento.query.order_by(Medicamento.nombre).all()
    return render_template('admin/medicamentos.html', medicamentos=lista)

@admin.route('/medicamentos/crear', methods=['POST'])
@login_required
@admin_required
def crear_medicamento():
    nombre = request.form.get('nombre', '').strip()
    principio = request.form.get('principio_activo', '').strip()
    presentacion = request.form.get('presentacion', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return redirect(url_for('admin.medicamentos'))
    m = Medicamento(nombre=nombre, principio_activo=principio, presentacion=presentacion)
    db.session.add(m)
    db.session.commit()
    flash(f'Medicamento "{nombre}" creado.', 'success')
    return redirect(url_for('admin.medicamentos'))

@admin.route('/medicamentos/<int:id>/toggle')
@login_required
@admin_required
def toggle_medicamento(id):
    m = Medicamento.query.get_or_404(id)
    m.activo = not m.activo
    db.session.commit()
    flash(f'Medicamento {"activado" if m.activo else "desactivado"}.', 'success')
    return redirect(url_for('admin.medicamentos'))
