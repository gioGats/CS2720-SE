from app import db
from app import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Items(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, type, price):
        self.type = type
        self.price = price

    def __repr__(self):
        return '{} {}'.format(self.type, self.price)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(400), nullable=False)
    permissions = db.Column(db.Integer, nullable=False)
    posts = relationship("Items", backref="author")

    def __init__(self, name, password, permissions):
        self.name = name
        self.password = bcrypt.generate_password_hash(password)
        self.permissions = permissions

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


    def __repr__(self):
        return '<name {}'.format(self.name)
