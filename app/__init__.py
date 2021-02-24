import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

print(os.environ['APP_SETTINGS'])
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return "page not found"

from app.auth.controllers import auth as auth_module

app.register_blueprint(auth_module)

db.create_all()
