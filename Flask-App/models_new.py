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
# TODO Merge Items table and Inventory table
"""
class Inventory(db.Model):
    __tablename__ = "inventory"

    item_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    item_type =  = db.Column(db.String)
    inventory_cost =  = db.Column(db.Float)
    expiration_date = db.Column(db.String) # TODO Modify for a date-specific format

    def __init__(self, product_id, inventory_cost):
        self.item_id = None # TODO Add logic to auto assign item_id
# TODO Decide if product_id or item_type should be input
        self.product_id = product_id
        self.item_type = None # TODO Get item_type from Products table
        self.inventory_cost = inventory_cost
        self.expiration_date = None # TODO Set to today + shelf_life from Products table

    def get_item(self, item_id)
        # TODO return all fields associated with item_id
        return []

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.item_id, self.product_id,self.item_type,
                                          self.inventory_cost, self.expiration_date)
"""


class Products(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer)
    inventory_count = db.Column(db.Integer)
    min_inventory = db.Column(db.Integer)
    shelf_life = db.Column(db.Integer)
    standard_price = db.Column(db.Float)
    sale_price = db.Column(db.Float)

    def __init__(self, supplier_id, inventory_count, min_inventory, shelf_life, standard_price):
        self.product_id = None  # TODO Add logic to auto assign product_id
        self.supplier_id = supplier_id
        self.inventory_count = inventory_count
        self.min_inventory = min_inventory
        self.shelf_life = shelf_life
        self.standard_price = standard_price
        self.sale_price = standard_price

    def get_price(self, product_id):
        # TODO get sale_price of this product
        return self.sale_price

    def __repr__(self):
        return '{} {} {} {} {} {} {}'.format(self.product_id, self.supplier_id, self.inventory_count,
                                             self.min_inventory, self.shelf_life, self.standard_price,
                                             self.sale_price)


class Sales(db.Model):
    __tablename__ = "sales"

    item_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    item_type = db.Column(db.String)
    price_sold = db.Column(db.Float)
    inventory_cost = db.Column(db.Float)
    transaction_id = db.Column(db.Float)

    def __init__(self, item_id, price_sold, transaction_id):
        self.item_id = item_id
        self.product_id = None  # TODO Get product_id from Inventory table
        self.item_type = None  # TODO Get item_type from Inventory table
        self.price_sold = price_sold
        self.inventory_cost = None  # TODO Get inventory_cost from Inventory table
        self.transaction_id = transaction_id

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.item_id, self.product_id, self.item_type,
                                          self.price_sold, self.inventory_cost, self.transaction_id)


class Suppliers(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, name, email):
        self.supplier_id = None  # TODO Add logic to auto assign supplier_id
        self.name = name
        self.email = email

    def __repr__(self):
        return '{} {} {}'.format(self.supplier_id, self.name, self.email)


class Transaction(db.Model):
    __tablename__ = "transactions"

    cust_name = db.Column(db.String)
    cust_contact = db.Column(db.String)
    payment_type = db.Column(db.Integer)
    date = db.Column(db.String)  # TODO Modify for a date-specific format
    transaction_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, cust_name, cust_contact, payment_type):
        self.cust_name = cust_name
        self.cust_contact = cust_contact
        self.payment_type = payment_type
        self.date = None  # TODO Auto-assign date
        self.transaction_id = None  # TODO Add logic to auto assign transaction_id

    def get_transaction(self, transaction_id):
        # TODO return all fields associated with transaction_id
        return []

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.cust_name, self.cust_contact, self.payment_type,
                                       self.date, self.transaction_id)


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
