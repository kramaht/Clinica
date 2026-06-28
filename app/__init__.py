from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db, Usuario
from config import config

login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .pacientes import pacientes as pacientes_bp
    app.register_blueprint(pacientes_bp, url_prefix='/pacientes')

    from .medicos import medicos as medicos_bp
    app.register_blueprint(medicos_bp, url_prefix='/medicos')

    from .citas import citas as citas_bp
    app.register_blueprint(citas_bp, url_prefix='/citas')

    from .consultas import consultas as consultas_bp
    app.register_blueprint(consultas_bp, url_prefix='/consultas')

    return app
