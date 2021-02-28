import os
import jwt
import datetime
from app.extensions import db, bcrypt
from sqlalchemy.dialects.postgresql import JSON
from dotenv import load_dotenv
load_dotenv()

class Base(db.Model):
    __abstract__  = True
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class User(Base):
    __tablename__ = 'auth_user'
    username = db.Column(db.String(80), unique=True,  nullable=False)
    email    = db.Column(db.String(80),  unique=True, nullable= False)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    password = db.Column(db.LargeBinary(128),  nullable=True)
    histories = db.relationship('History', backref='auth_user', lazy='dynamic')

    def __init__(self, username, email, password=None, **kwargs):
        super().__init__(username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self):
        return bcrypt.check_password_hash(self.password, value)

    def encode_auth_token(self, user_id):
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

    @staticmethod
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

    @property
    def full_name(self):
        return f"{self.fist_name} {self.last_name}"

    def __repr__(self):
        return f"<User({self.username!r})>"

class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class History(Base):
    __tablename__ = 'history'
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    user = db.relationship('User')
    entries = db.relationship('Entry', backref='parent_history', lazy='dynamic')

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return '<Collection %r>' % (self.name)

class Entry(Base):
    __tablename__ = 'entry'
    host = db.Column(JSON, nullable=False)
    opponent = db.Column(JSON, nullable=False)
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    history = db.relationship('History')

    def __init__(self, host, opponent):
        self.host = host
        self.opponent = opponent

    def __repr__(self):
        return '<Entry %r>' % (self.id)
