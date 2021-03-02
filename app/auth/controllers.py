import json
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.extensions import bcrypt,db
from app.auth.models import User, BlacklistToken
from app.util.util import is_email_valid, build_response_object
from app.messages import INVALID_EMAIL, REGISTRATION_SUCCESS, GENERIC_ERROR, \
                         USER_NOT_EXIST, ALREADY_REGISTERED, LOGIN_SUCCESS, LOGOUT_SUCCESS, EMAIL_PASS_MISMATCH, INVALID_TOKEN
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.before_request
def check_valid_email_before_route():
    data = request.get_json()
    if data:
        if "email" in data:
            if not is_email_valid(data["email"]):
                resp = build_response_object('fail', INVALID_EMAIL, "")
                return make_response(jsonify(resp)), 401

class RegisterAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    username=post_data.get('username'),
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                db.session.add(user)
                db.session.flush()
            except Exception as e:
                response = build_response_object('fail',GENERIC_ERROR,"")
                return make_response(jsonify(response)), 500
            #return successful
            user_id = user.id
            auth_token = user.encode_auth_token(user_id)
            response = build_response_object('success',REGISTRATION_SUCCESS,auth_token)
            return make_response(jsonify(response)), 201
        else:
            response = build_response_object('fail',ALREADY_REGISTERED,"")
            return make_response(jsonify(response)), 500

class LoginAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        try:
            user = User.query.filter_by(
                username=post_data.get('username')
            ).first()
            #No user under the given username is found
            if(not(isinstance(user, User))):
                response = build_response_object('fail',USER_NOT_EXIST,"")
                return make_response(jsonify(response)), 404
            #Checks username against the given password
            if user and bcrypt.check_password_hash(
                user.password, post_data.get('password')):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response = build_response_object('success',LOGIN_SUCCESS,auth_token)
                    return make_response(jsonify(response)), 200
            else:
                response = build_response_object('fail', EMAIL_PASS_MISMATCH, "")
                return make_response(jsonify(response)), 400
        except Exception as e:
            response = build_response_object('fail',GENERIC_ERROR, "")
            return make_response(jsonify(response)), 500

class TokenStatusAPI(MethodView):
    def get(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                user_info = {
                    'user_id': user.id,
                    'email': user.email,
                    'date_created': user.date_created
                }
                response = build_response_object('success', user_info, "")
                return make_response(jsonify(response)), 200
            response = build_response_object('fail', resp, "")
            return make_response(jsonify(response)), 401
        else:
            response = build_response_object('fail', INVALID_TOKEN, "")
            return make_response(jsonify(response)), 401

class LogoutAPI(MethodView):
    def post(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    db.session.add(blacklist_token)
                    db.session.commit()
                    response = build_response_object('success', LOGOUT_SUCCESS, "")
                    return make_response(jsonify(response)), 200
                except Exception as e:
                    response = build_response_object('fail', e, "")
                    return make_response(jsonify(response)), 200
            else:
                response = build_response_object('fail', resp, "")
                return make_response(jsonify(response)), 401
        else:
            response = build_response_object('fail', INVALID_TOKEN, "")
            return make_response(jsonify(response)), 403

#API Resources
registration_controller = RegisterAPI.as_view('register_api')
login_controller = LoginAPI.as_view('login_api')
token_status_controller = TokenStatusAPI.as_view('user_api')
logout_controller = LogoutAPI.as_view('logout_api')

#rules for API endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_controller,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_controller,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=token_status_controller,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_controller,
    methods=['POST']
)
