import os
from flask import Flask
from app.auth.controllers import auth_blueprint as auth_module
from app.history.controllers import history_blueprint as history_module
from app.extensions import db
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.getenv('APP_SETTINGS'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app

def register_extensions(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return None

def register_errorhandlers(app):
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)
    return None

def register_blueprints(app):
    app.register_blueprint(auth_module)
    app.register_blueprint(history_module)
    return None
