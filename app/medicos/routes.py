from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import medicos
from ..models import db, Medico, Usuario, Rol, Especialidad, HorarioMedico
from datetime import time

@medicos.route('/')
@login_required
def index():
    lista = Medico.query.filter_by(activo=True).join(Usuario).order_by(Usuario.apellido).all()
    return render_template('medicos/index.html', medicos=lista)

@medicos.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not current_user.tiene_rol('admin'):
        flash('Solo administradores pueden crear médicos.', 'error')
        return redirect(url_for('medicos.index'))
    especialidades = Especialidad.query.filter_by(activa=True).order_by(Especialidad.nombre).all()
    # Usuarios con rol médico sin perfil de médico aún
    rol_medico = Rol.query.filter_by(nombre='medico').first()
    usuarios_disponibles = []
    if rol_medico:
        usuarios_disponibles = Usuario.query.filter_by(rol_id=rol_medico.id, activo=True)\
            .filter(~Usuario.medico.has()).all()

    if request.method == 'POST':
        matricula = request.form.get('matricula', '').strip()
        if Medico.query.filter_by(matricula=matricula).first():
            flash('La matrícula ya está registrada.', 'error')
            return redirect(url_for('medicos.nuevo'))
        m = Medico(
            matricula=matricula,
            telefono=request.form.get('telefono', '').strip(),
            consultorio=request.form.get('consultorio', '').strip(),
            usuario_id=int(request.form.get('usuario_id')),
            especialidad_id=int(request.form.get('especialidad_id')),
        )
        db.session.add(m)
        db.session.commit()
        flash(f'Médico {m.nombre_completo} registrado.', 'success')
        return redirect(url_for('medicos.detalle', id=m.id))
    return render_template('medicos/form.html', medico=None,
                           especialidades=especialidades,
                           usuarios_disponibles=usuarios_disponibles)

@medicos.route('/<int:id>')
@login_required
def detalle(id):
    m = Medico.query.get_or_404(id)
    horarios = HorarioMedico.query.filter_by(medico_id=id, activo=True)\
                .order_by(HorarioMedico.dia_semana).all()
    citas_recientes = m.citas.order_by(None).order_by(db.desc('fecha_hora')).limit(10).all()
    return render_template('medicos/detalle.html', medico=m,
                           horarios=horarios, citas=citas_recientes)

@medicos.route('/<int:id>/horario', methods=['POST'])
@login_required
def agregar_horario(id):
    m = Medico.query.get_or_404(id)
    dia = int(request.form.get('dia_semana'))
    h_inicio = time(*map(int, request.form.get('hora_inicio').split(':')))
    h_fin = time(*map(int, request.form.get('hora_fin').split(':')))
    h = HorarioMedico(medico_id=m.id, dia_semana=dia, hora_inicio=h_inicio, hora_fin=h_fin)
    db.session.add(h)
    db.session.commit()
    flash('Horario agregado.', 'success')
    return redirect(url_for('medicos.detalle', id=id))

@medicos.route('/<int:id>/horario/<int:hid>/eliminar', methods=['POST'])
@login_required
def eliminar_horario(id, hid):
    h = HorarioMedico.query.get_or_404(hid)
    h.activo = False
    db.session.commit()
    flash('Horario eliminado.', 'success')
    return redirect(url_for('medicos.detalle', id=id))
