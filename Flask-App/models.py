from app import db
from app import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime
# TODO Adjust so that foreign keys auto-assign


class Items(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    inventory_cost = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.DATE, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, product_id, inventory_cost):
        self.product_id = product_id
        self.inventory_cost = inventory_cost
        shelf_life = 1  # TODO get shelflife from products table
        self.expiration_date = datetime.date.today() + datetime.timedelta(days=shelf_life)
        # TODO Increment inventory count in products table

    def __repr__(self):
        return '{} {} {} {}'.format(self.id, self.product_id, self.inventory_cost, self.expiration_date)


class Users(db.Model):
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


class Products(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    supplier_id = db.Column(db.Integer, ForeignKey('suppliers.id'))
    inventory_count = db.Column(db.Integer, nullable=False)
    min_inventory = db.Column(db.Integer, nullable=False)
    shelf_life = db.Column(db.Integer, nullable=False)
    standard_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)

    def __init__(self, name, supplier_id, min_inventory, shelf_life, standard_price):
        self.name = name
        self.supplier_id = supplier_id
        self.inventory_count = 0
        self.min_inventory = min_inventory
        self.shelf_life = shelf_life
        self.standard_price = standard_price
        self.sale_price = standard_price

    def get_price(self, product_id):
        # TODO get sale_price of this product
        return self.sale_price

    def __repr__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.id, self. name, self.supplier_id, self.inventory_count,
                                             self.min_inventory, self.shelf_life, self.standard_price, self.sale_price)


class ItemsSold(db.Model):
    __tablename__ = "items_sold"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('items.id'))
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    price_sold = db.Column(db.Float, nullable=False)
    inventory_cost = db.Column(db.Float, ForeignKey('items.inventory_cost'))
    transaction_id = db.Column(db.Float, nullable=False)

    def __init__(self, item_id, price_sold, transaction_id):
        self.item_id = item_id
        self.price_sold = price_sold
        self.inventory_cost = None  # TODO Get inventory_cost from Inventory table
        self.transaction_id = transaction_id

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.id, self.item_id, self.product_id, self.price_sold,
                                          self.inventory_cost, self.transaction_id)


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


class Transactions(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(20), nullable=False)
    cust_contact = db.Column(db.String(40), nullable=False)
    payment_type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DATE, nullable=False)

    def __init__(self, cust_name, cust_contact, payment_type):
        self.cust_name = cust_name
        self.cust_contact = cust_contact
        self.payment_type = payment_type
        self.date = datetime.date.today()

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.cust_name, self.cust_contact, self.payment_type, self.date)


class Discounts(db.Model):
    __tablename__ = "discounts"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DATE, nullable=False)
    end_date = db.Column(db.DATE, nullable=False)
    discount = db.Column(db.Float, nullable=False)

    def __init__(self, product_id, start_date, end_date, discount):
        self.product_id = product_id
        self.start_date = start_date
        self.end_date = end_date
        self.discount = discount

    # TODO Find the appropriate place for this function:
    """
    def update_prices():
        for row in discounts:
            get corresponding row in products table where discounts.product_id = products.id
            if (datetime.date.today() >= start_date) and (datetime.date.today() <= end_date):
                set this row's products.sale_price to products.standard_price * discounts.discount
            else:
                set this row's products.sale_price to products.standard_price
    """

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.product_id, self.start_date, self.end_date, self.discount)
