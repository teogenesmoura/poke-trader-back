from flask import Flask, Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.auth.models import User

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.errorhandler(404)
def page_not_found(e):
    return "Could not find page"

@auth.route('/signin/', methods=['GET', 'POST'])
def signin():
    return '{"message": "login page"}'
