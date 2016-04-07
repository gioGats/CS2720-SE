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


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String, nullable=False)
    inventory_cost = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.DATE, nullable=False)

    def __init__(self, product_id, inventory_cost):
# TODO Decide if product_id or item_type should be input
        self.product_id = product_id
        self.item_type = None # TODO Get item_type from Products table
        self.inventory_cost = inventory_cost
        self.expiration_date = None # TODO Set to today + shelf_life from Products table

    def get_item(self, item_id):
        # TODO return all fields associated with item_id
        return []

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.product_id,self.item_type,
                                       self.inventory_cost, self.expiration_date)


class Products(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, nullable=False)
    inventory_count = db.Column(db.Integer, nullable=False)
    min_inventory = db.Column(db.Integer, nullable=False)
    shelf_life = db.Column(db.Integer, nullable=False)
    standard_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)

    def __init__(self, supplier_id, inventory_count, min_inventory, shelf_life, standard_price):
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
        return '{} {} {} {} {} {} {}'.format(self.id, self.supplier_id, self.inventory_count,
                                             self.min_inventory, self.shelf_life, self.standard_price,
                                             self.sale_price)


class Sales(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String, nullable=False)
    price_sold = db.Column(db.Float, nullable=False)
    inventory_cost = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.Float, nullable=False)

    def __init__(self, item_id, price_sold, transaction_id):
        self.item_type = None  # TODO Get item_type from Inventory table
        self.price_sold = price_sold
        self.inventory_cost = None  # TODO Get inventory_cost from Inventory table
        self.transaction_id = transaction_id

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.id, self.product_id, self.item_type,
                                          self.price_sold, self.inventory_cost, self.transaction_id)


class Suppliers(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.name, self.email)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String, nullable=False)
    cust_contact = db.Column(db.String, nullable=False)
    payment_type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DATE, nullable=False)

    def __init__(self, cust_name, cust_contact, payment_type):
        self.cust_name = cust_name
        self.cust_contact = cust_contact
        self.payment_type = payment_type
        self.date = None  # TODO Auto-assign date

    def get_transaction(self, transaction_id):
        # TODO return all fields associated with transaction_id
        return []

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.cust_name, self.cust_contact, self.payment_type, self.date)


class Discounts(db.Model):
    __tablename__ = "discounts"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DATE, nullable=False)
    end_date = db.Column(db.DATE, nullable=False)
    discount = db.Column(db.Float, nullable=False) # TODO Is this a percentage or what?

    def __init__(self, product_id, start_date, end_date, discount):
        self.product_id = product_id
        self.start_date = start_date
        self.end_date = end_date
        self.discount = discount

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.product_id, self.start_date, self.end_date, self.discount)



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
