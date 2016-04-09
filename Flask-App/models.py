from app import db
from app import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Item(db.Model):
	__tablename__ = "items"

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(30), nullable=False)
	price = db.Column(db.Float, nullable=False)
	product_id = db.Column(db.Integer, ForeignKey("products.id"), nullable=False)
	exp_date = db.Column(db.Date, nullable=False)

	author_id = db.Column(db.Integer, ForeignKey('users.id'))

	def __init__(self, type, price, product_id, exp_date, author_id):
		self.type = type
		self.price = price
		self.product_id = product_id
		self.exp_date = exp_date
		self.author_id = author_id

	def __repr__(self):
		return '{} {}'.format(self.type, self.price)

class Product(db.Model):
	__tablename__ = "products"

	id = db.Column(db.Integer, primary_key=True)
	supplier_id = db.Column(db.Integer, ForeignKey("suppliers.id"), nullable=False)
	inventory_count = db.Column(db.Integer, nullable=False)
	min_count = db.Column(db.Integer)
	shelf_life = db.Column(db.Integer, nullable=False)
	standard_price = db.Column(db.Float, nullable=False)
	sale_price = db.Column(db.Float)

	def __init__(self, supplier_id, inventory_count, shelf_life, standard_price):
		self.supplier_id = supplier_id
		self.inventory_count = inventory_count
		self.shelf_life = shelf_life
		self.standard_price = standard_price

	def __repr__(self):
		return "{} {} {} {}".format(self.supplier_id, self.inventory_count, self.shelf_life, self.standard_price)

class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False)
	password = db.Column(db.String(400), nullable=False)
	permissions = db.Column(db.Integer, nullable=False)
	posts = relationship("Item", backref="author")

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

class Supplier(db.Model):
	__tablename__ = "suppliers"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String(20))

	def __init__(self, name, email):
		self.name = name
		self.email = email

	def __repr__(self):
		return "{} {} {}".format(self.id, self.name, self.email)

