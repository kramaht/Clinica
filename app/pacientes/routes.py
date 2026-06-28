from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import pacientes
from ..models import db, Paciente, Consulta, Cita
from datetime import datetime

@pacientes.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    query = Paciente.query.filter_by(activo=True)
    if q:
        query = query.filter(
            db.or_(
                Paciente.nombre.ilike(f'%{q}%'),
                Paciente.apellido.ilike(f'%{q}%'),
                Paciente.ci.ilike(f'%{q}%'),
            )
        )
    lista = query.order_by(Paciente.apellido).all()
    return render_template('pacientes/index.html', pacientes=lista, q=q)

@pacientes.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        ci = request.form.get('ci', '').strip()
        if Paciente.query.filter_by(ci=ci).first():
            flash('Ya existe un paciente con ese CI.', 'error')
            return redirect(url_for('pacientes.nuevo'))
        p = Paciente(
            nombre=request.form.get('nombre', '').strip(),
            apellido=request.form.get('apellido', '').strip(),
            ci=ci,
            fecha_nacimiento=datetime.strptime(request.form.get('fecha_nacimiento'), '%Y-%m-%d').date(),
            sexo=request.form.get('sexo'),
            telefono=request.form.get('telefono', '').strip(),
            email=request.form.get('email', '').strip().lower() or None,
            direccion=request.form.get('direccion', '').strip(),
            grupo_sanguineo=request.form.get('grupo_sanguineo', '').strip(),
            alergias=request.form.get('alergias', '').strip(),
        )
        db.session.add(p)
        db.session.commit()
        flash(f'Paciente {p.nombre_completo} registrado.', 'success')
        return redirect(url_for('pacientes.detalle', id=p.id))
    return render_template('pacientes/form.html', paciente=None)

@pacientes.route('/<int:id>')
@login_required
def detalle(id):
    p = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(paciente_id=id).order_by(Consulta.fecha.desc()).all()
    citas = Cita.query.filter_by(paciente_id=id).order_by(Cita.fecha_hora.desc()).limit(5).all()
    return render_template('pacientes/detalle.html', paciente=p, consultas=consultas, citas=citas)

@pacientes.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    p = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form.get('nombre', '').strip()
        p.apellido = request.form.get('apellido', '').strip()
        p.telefono = request.form.get('telefono', '').strip()
        p.email = request.form.get('email', '').strip().lower() or None
        p.direccion = request.form.get('direccion', '').strip()
        p.grupo_sanguineo = request.form.get('grupo_sanguineo', '').strip()
        p.alergias = request.form.get('alergias', '').strip()
        db.session.commit()
        flash('Datos del paciente actualizados.', 'success')
        return redirect(url_for('pacientes.detalle', id=p.id))
    return render_template('pacientes/form.html', paciente=p)

@pacientes.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    p = Paciente.query.get_or_404(id)
    p.activo = False
    db.session.commit()
    flash(f'Paciente {p.nombre_completo} dado de baja.', 'success')
    return redirect(url_for('pacientes.index'))
