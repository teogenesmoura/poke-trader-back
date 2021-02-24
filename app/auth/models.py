from app import db
from sqlalchemy.dialects.postgresql import JSON

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class User(Base):
    __tablename__ = 'auth_user'
    name = db.Column(db.String(128),  nullable=False)
    email    = db.Column(db.String(128),  nullable=False,
                                            unique=True)
    password = db.Column(db.String(192),  nullable=False)
    role = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False)
    collections = db.relationship('History', backref='owner', lazy='dynamic')

    def __init__(self, name, email, password):
        self.name     = name
        self.email    = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)

class History(Base):
    __tablename__ = 'collection'
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(128), nullable=False)
    entries = db.relationship('Entry', backref='owner', lazy='dynamic')

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return '<Collection %r>' % (self.name)

class Entry(Base):
    __tablename__ = 'entry'
    host = db.Column(JSON, nullable=False)
    opponent = db.Column(JSON, nullable=False)

    def __init__(self, host, opponent):
        self.host = host
        self.opponent = opponent

    def __repr__(self):
        return '<Entry %r>' % (self.id)
