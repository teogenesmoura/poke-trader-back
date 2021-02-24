from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

from app.auth.models import User

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/signin/', methods=['GET', 'POST'])
def signin():
    return '{"message": "login page"}'
