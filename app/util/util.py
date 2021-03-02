from email.utils import parseaddr
from app.auth.models import User, BlacklistToken
import jwt
import datetime
import os

def is_email_valid(address):
    return '@' in parseaddr(address)[1]

def build_response_object(status, message, auth_token):
    response = {}
    if status:
        response['status'] = status
    if message:
        response['message'] = message
    if auth_token:
        response['auth_token'] = auth_token
    return response

def get_user_from_token(auth_header):
    user = False
    auth_token = auth_header.split(" ")[1] if auth_header else ''
    if auth_token:
        user_id = decode_auth_token(auth_token)
        user = User.query.filter_by(id=user_id).first()
    if not user:
        resp = build_response_object('fail', USER_NOT_EXIST, "")
        return make_response(jsonify(resp)), 406
    return user, user_id

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithms='HS256')
        is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
