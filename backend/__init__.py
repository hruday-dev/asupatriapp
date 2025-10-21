from flask import Flask
from .config import Config
from .extensions import db, jwt, cors


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import auth_bp
    from .routes.hospitals import hospitals_bp
    from .routes.appointments import appointments_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(hospitals_bp, url_prefix="/api")
    app.register_blueprint(appointments_bp, url_prefix="/api")
    
    # Register hospital admin routes
    # from .routes.hospital_admin import hospital_admin_bp
    # app.register_blueprint(hospital_admin_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app