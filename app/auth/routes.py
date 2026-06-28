from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import db, Usuario, Rol

@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password) and usuario.activo:
            login_user(usuario, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Credenciales incorrectas o cuenta inactiva.', 'error')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
