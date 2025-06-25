from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Instâncias globais
db = SQLAlchemy()


def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Criar diretório de uploads
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Registrar blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.finances import finances_bp
    from routes.uploads import uploads_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(finances_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp, url_prefix='/api')
    
    # Criar tabelas do banco
    with app.app_context():
        db.create_all()
    
    return app
