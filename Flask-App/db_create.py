"""
Author: Jacob Campbell; Ryan Giarusso
Created: 3/1/2016
Purpose: Test database creation file.  Generates sample entries in all database tables.
"""
from app import db
from models import *
import datetime

# Create the database and the db tables #
db.create_all()

#######################################################################################################################
#  INSERT ITEMS INTO TABLES!																																									#
#######################################################################################################################

users_init = [
    # username, password, permissions
    ["admin", "admin", 1],
    ["cashier", "admin", 2],
    ["stocker", "admin", 3]
]

suppliers_init = [
    # name, email
    ["Ethan", "myEmail@email.com"],
    ["BopBoop", "3195551234"]
]

products_init = [
    # name, supplier_id, min_inventory, shelf_life, standard_price
    ["poop", 1, 10, 10, 1.50],
    ["banana", 1, 20, 5, 1.00],
    ["matches", 2, 15, 100, 1.25]
]

items_init = [
    # product_id, inventory_cost
    [1, 0.75],
    [1, 1.50],
    [1, 1.60],
    [2, 0.25],
    [2, 0.50],
    [2, 0.75],
    [3, 0.20],
    [3, 0.25],
    [3, 0.30],
    [1, 0.75],
    [1, 1.50],
    [1, 1.60],
    [2, 0.25],
    [2, 0.50],
    [2, 0.75],
    [3, 0.20],
    [3, 0.25],
    [3, 0.30],
]

for i in range(1, 4):
    for j in range(0, 100):
        for k in range(1, 5):
            items_init.append([i, 2-(1/k)])

itemsSold_init = [
    # item_id, price_sold, transaction_id
    [1, 1.50, 1],
    [2, 1.50, 1],
    [3, 1.50, 1],
    [4, 0.50, 1],
    [5, 0.50, 2],
    [6, 0.50, 2],
    [7, 0.25, 2],
    [8, 0.25, 2],
    [9, 0.25, 2],
]

discounts_init = [
    # product_id, start_date, end_date, discount
    [1, datetime.date.today() - datetime.timedelta(days=1), datetime.date.today() + datetime.timedelta(days=1), 0.10],
    [2, datetime.date.today() - datetime.timedelta(days=2), datetime.date.today() + datetime.timedelta(days=2), 0.20]
]

transactions_init = [
    # cust_name, cust_contact, payment_type
    ["Bob", "never!", 1],
    ["Tom", "Gah!", 2]
]

# Probably useless, but doesn't hurt to have them all right?
all_inits = [users_init, suppliers_init, products_init, items_init, itemsSold_init, discounts_init, transactions_init]

for i in transactions_init:
    db.session.add(Transaction(i[0], i[1], i[2]))
    # db.session.commit()

for i in suppliers_init:
    db.session.add(Supplier(i[0], i[1]))
    # db.session.commit()

for i in products_init:
    db.session.add(Product(i[0], i[1], i[2], i[3], i[4]))
    # db.session.commit()

for i in users_init:
    db.session.add(User(i[0], i[1], i[2]))
    # db.session.commit()

for i in items_init:
    db.session.add(Item(i[0], i[1]))
    # db.session.commit()

for i in itemsSold_init:
    db.session.add(ItemSold(i[0], i[1], i[2]))
    # db.session.commit()

for i in discounts_init:
    db.session.add(Discount(i[0], i[1], i[2], i[3]))
#    db.session.commit()

# Commit changes
db.session.commit()
