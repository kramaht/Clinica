from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import citas
from ..models import db, Cita, Paciente, Medico
from datetime import datetime

ESTADOS_VALIDOS = ['pendiente', 'confirmada', 'completada', 'cancelada']

@citas.route('/')
@login_required
def index():
    estado = request.args.get('estado', '')
    q = request.args.get('q', '').strip()
    query = Cita.query.join(Paciente).join(Medico)
    if estado and estado in ESTADOS_VALIDOS:
        query = query.filter(Cita.estado == estado)
    if q:
        query = query.filter(
            db.or_(
                Paciente.nombre.ilike(f'%{q}%'),
                Paciente.apellido.ilike(f'%{q}%'),
            )
        )
    lista = query.order_by(Cita.fecha_hora.desc()).all()
    return render_template('citas/index.html', citas=lista, estado=estado, q=q,
                           estados=ESTADOS_VALIDOS)

@citas.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    pacientes = Paciente.query.filter_by(activo=True).order_by(Paciente.apellido).all()
    medicos = Medico.query.filter_by(activo=True).all()
    paciente_id = request.args.get('paciente_id', type=int)

    if request.method == 'POST':
        fecha_hora = datetime.strptime(request.form.get('fecha_hora'), '%Y-%m-%dT%H:%M')
        c = Cita(
            paciente_id=int(request.form.get('paciente_id')),
            medico_id=int(request.form.get('medico_id')),
            fecha_hora=fecha_hora,
            motivo=request.form.get('motivo', '').strip(),
            notas=request.form.get('notas', '').strip(),
        )
        db.session.add(c)
        db.session.commit()
        flash('Cita agendada correctamente.', 'success')
        return redirect(url_for('citas.index'))
    return render_template('citas/form.html', pacientes=pacientes,
                           medicos=medicos, paciente_id=paciente_id)

@citas.route('/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado(id):
    c = Cita.query.get_or_404(id)
    nuevo = request.form.get('estado')
    if nuevo in ESTADOS_VALIDOS:
        c.estado = nuevo
        db.session.commit()
        flash(f'Estado de cita actualizado a "{nuevo}".', 'success')
    return redirect(url_for('citas.index'))

@citas.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    c = Cita.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Cita eliminada.', 'success')
    return redirect(url_for('citas.index'))
