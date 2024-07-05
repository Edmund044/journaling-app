from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from .config import Config

db = SQLAlchemy()
# migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    # migrate.init_app(app, db)
    jwt.init_app(app)
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [{"Bearer": []}]
    }
    Swagger(app, config=swagger_config)

    from .auth import auth_bp
    from .journal import journal_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(journal_bp, url_prefix='/journal')

    return app
