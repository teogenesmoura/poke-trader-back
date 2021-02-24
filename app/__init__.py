import os
from flask import Flask
from app.auth.controllers import auth as auth_module
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
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

def register_blueprints(app):
    app.register_blueprint(auth_module)
    return None
