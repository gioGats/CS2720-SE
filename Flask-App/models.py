"""
Author: Jacob Campbell; Ryan Giarusso
Created: 3/10/2016
Purpose: All the databases!
"""

from app import db
from app import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy.exc import SQLAlchemyError


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    inventory_cost = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.DATE, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, product_id, inventory_cost):
        """
        Database table stores individual items in store inventory.
        :param product_id: int
        :param inventory_cost: float
        :return: None
        """
        self.product_id = product_id
        self.inventory_cost = inventory_cost
        shelf_life = self.get_product(product_id).shelf_life
        self.expiration_date = datetime.date.today() + datetime.timedelta(days=shelf_life)
        self.get_product(product_id).inventory_count += 1

    @staticmethod
    def get_product(product_id):
        """
        Gets the entry with the input product_id from products table.
        :param product_id: int
        :return: Product entry from products table
        """
        try:
            return Product.query.filter_by(id=product_id).first()
        except SQLAlchemyError:
            raise Exception("get_product failed.  You suck.")

    def __repr__(self):
        return '{} {} {} {}'.format(self.id, self.product_id, self.inventory_cost, self.expiration_date)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(400), nullable=False)
    permissions = db.Column(db.Integer, nullable=False)
    posts = relationship("Item", backref="author")

    def __init__(self, name, password, permissions):
        """
        Database table stores individual users.
        :param name: str
        :param password: str
        :param permissions: int
        :return: None
        """
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


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    supplier_id = db.Column(db.Integer, ForeignKey('suppliers.id'))
    inventory_count = db.Column(db.Integer, nullable=False)
    min_inventory = db.Column(db.Integer, nullable=False)
    shelf_life = db.Column(db.Integer, nullable=False)
    standard_price = db.Column(db.Float, nullable=False)

    def __init__(self, name, supplier_id, min_inventory, shelf_life, standard_price):
        """
        Database table stores products (types of items) in store inventory.
        :param name: str
        :param supplier_id: int
        :param min_inventory: int
        :param shelf_life: int (days)
        :param standard_price: float
        :return: None
        """
        self.name = name
        self.supplier_id = supplier_id
        self.inventory_count = 0
        self.min_inventory = min_inventory
        self.shelf_life = shelf_life
        self.standard_price = standard_price

    def __repr__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.id, self. name, self.supplier_id, self.inventory_count,
                                             self.min_inventory, self.shelf_life, self.standard_price, self.sale_price)


class ItemSold(db.Model):
    __tablename__ = "items_sold"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    price_sold = db.Column(db.Float, nullable=False)
    inventory_cost = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.Float, nullable=False)

    def __init__(self, item_id, price_sold, transaction_id):
        """
        Database table stores records of individual items sold.
        :param item_id: int
        :param price_sold: float
        :param transaction_id: int
        :return: None
        """
        self.item_id = item_id
        self.product_id = self.get_product_id(item_id)
        self.price_sold = price_sold
        self.inventory_cost = self.get_cost(item_id)
        self.transaction_id = transaction_id

    @staticmethod
    def get_product_id(item_id):
        """
        Given an item_id, returns the product_id associated with that item.
        Raises SQLAlchemyError if the query fails for any reason.
        :param item_id: int
        :return: product_id (int)
        """
        try:
            item = Item.query.filter_by(id=item_id).first()
            return item.product_id
        except SQLAlchemyError:
            raise SQLAlchemyError("get_product_id failed. You suck.")

    @staticmethod
    def get_cost(item_id):
        """
        Given an item_id, returns the inventory cost associated with that item.
        Raises SQLAlchemyError if the query fails for any reason.
        :param item_id:
        :return:
        """
        try:
            item = Item.query.filter_by(id=item_id).first()
            return item.inventory_cost
        except SQLAlchemyError:
            raise SQLAlchemyError("get_cost failed.  You suck.")

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.id, self.item_id, self.product_id, self.price_sold,
                                          self.inventory_cost, self.transaction_id)


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __init__(self, name, email):
        """
        Database table stores suppliers and their contact information.
        :param name: str
        :param email: str
        :return: None
        """
        self.name = name
        self.email = email

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.name, self.email)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(20), nullable=False)
    cust_contact = db.Column(db.String(40), nullable=False)
    payment_type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DATE, nullable=False)

    def __init__(self, cust_name, cust_contact, payment_type, date=datetime.date.today()):
        """
        Database table stores records of transactions.
        :param cust_name: str
        :param cust_contact: str
        :param payment_type: int
        :param date: datetime.date (defaults to today)
        :return: None
        """
        self.cust_name = cust_name
        self.cust_contact = cust_contact
        self.payment_type = payment_type
        self.date = date

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.cust_name, self.cust_contact, self.payment_type, self.date)


class Discount(db.Model):
    __tablename__ = "discounts"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    start_date = db.Column(db.DATE, nullable=False)
    end_date = db.Column(db.DATE, nullable=False)
    discount = db.Column(db.Float, nullable=False)

    def __init__(self, product_id, start_date, end_date, discount):
        """
        Database table stores discounts for product types past, present, and future.
        :param product_id: int
        :param start_date: datetime.date
        :param end_date: datetime.date
        :param discount: float
        :return: None
        """
        self.product_id = product_id
        self.start_date = start_date
        self.end_date = end_date
        self.discount = discount

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.product_id, self.start_date, self.end_date, self.discount)
