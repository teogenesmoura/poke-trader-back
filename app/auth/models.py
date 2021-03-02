import os
import datetime
from dataclasses import dataclass
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

@dataclass
class Entry(Base):
    host: JSON
    opponent: JSON
    history_id: int

    __tablename__ = 'entry'
    host = db.Column(JSON, nullable=False)
    opponent = db.Column(JSON, nullable=False)
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    history = db.relationship('History')

    def __init__(self, history_id, host, opponent):
        self.host = host
        self.opponent = opponent
        self.history_id = history_id

    def __repr__(self):
        return '<Entry %r>' % (self.id)

@dataclass
class History(Base):
    name: str
    type: str
    user_id: int

    __tablename__ = 'history'
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    user = db.relationship('User')
    entries = db.relationship('Entry', backref='parent_history', lazy='dynamic')

    def __init__(self, name, type, user_id):
        self.name = name
        self.type = type
        self.user_id = user_id

    def __repr__(self):
        return '<Collection %r>' % (self.name)
