from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, jwt
from .core.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Deferred imports to prevent circular dependency
    from . import models
    from .routes.auth import auth_bp
    from .routes.ingestion import ingestion_bp
    from .routes.timetable import timetable_bp
    from .routes.preferences import preferences_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ingestion_bp, url_prefix='/api/ingestion')
    app.register_blueprint(timetable_bp, url_prefix='/api/timetable')
    app.register_blueprint(preferences_bp, url_prefix='/api/preferences')

    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200

    return app
