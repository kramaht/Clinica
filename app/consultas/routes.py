from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import consultas
from ..models import db, Consulta, Paciente, Medico, Cita, Receta, Medicamento
from datetime import datetime

@consultas.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    query = Consulta.query.join(Paciente)
    if q:
        query = query.filter(
            db.or_(
                Paciente.nombre.ilike(f'%{q}%'),
                Paciente.apellido.ilike(f'%{q}%'),
            )
        )
    lista = query.order_by(Consulta.fecha.desc()).all()
    return render_template('consultas/index.html', consultas=lista, q=q)

@consultas.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    pacientes = Paciente.query.filter_by(activo=True).order_by(Paciente.apellido).all()
    medicos = Medico.query.filter_by(activo=True).all()
    medicamentos = Medicamento.query.filter_by(activo=True).order_by(Medicamento.nombre).all()
    citas_pendientes = Cita.query.filter_by(estado='confirmada').order_by(Cita.fecha_hora).all()

    if request.method == 'POST':
        cita_id = request.form.get('cita_id') or None
        c = Consulta(
            paciente_id=int(request.form.get('paciente_id')),
            medico_id=int(request.form.get('medico_id')),
            cita_id=int(cita_id) if cita_id else None,
            motivo_consulta=request.form.get('motivo_consulta', '').strip(),
            sintomas=request.form.get('sintomas', '').strip(),
            diagnostico=request.form.get('diagnostico', '').strip(),
            tratamiento=request.form.get('tratamiento', '').strip(),
            peso=request.form.get('peso') or None,
            talla=request.form.get('talla') or None,
            presion_arterial=request.form.get('presion_arterial', '').strip() or None,
            temperatura=request.form.get('temperatura') or None,
            frecuencia_cardiaca=request.form.get('frecuencia_cardiaca') or None,
            observaciones=request.form.get('observaciones', '').strip(),
        )
        db.session.add(c)
        db.session.flush()  # para obtener c.id antes del commit

        # Si venía de cita, marcarla como completada
        if cita_id:
            cita = Cita.query.get(int(cita_id))
            if cita:
                cita.estado = 'completada'

        # Procesar recetas
        med_ids = request.form.getlist('medicamento_id[]')
        dosis_list = request.form.getlist('dosis[]')
        freq_list = request.form.getlist('frecuencia[]')
        dur_list = request.form.getlist('duracion[]')
        ind_list = request.form.getlist('indicaciones[]')

        for i, mid in enumerate(med_ids):
            if mid:
                r = Receta(
                    consulta_id=c.id,
                    medicamento_id=int(mid),
                    dosis=dosis_list[i] if i < len(dosis_list) else '',
                    frecuencia=freq_list[i] if i < len(freq_list) else '',
                    duracion=dur_list[i] if i < len(dur_list) else '',
                    indicaciones=ind_list[i] if i < len(ind_list) else '',
                )
                db.session.add(r)

        db.session.commit()
        flash('Consulta registrada correctamente.', 'success')
        return redirect(url_for('consultas.detalle', id=c.id))

    return render_template('consultas/form.html',
                           pacientes=pacientes, medicos=medicos,
                           medicamentos=medicamentos,
                           citas_pendientes=citas_pendientes)

@consultas.route('/<int:id>')
@login_required
def detalle(id):
    c = Consulta.query.get_or_404(id)
    recetas = Receta.query.filter_by(consulta_id=id).all()
    return render_template('consultas/detalle.html', consulta=c, recetas=recetas)
