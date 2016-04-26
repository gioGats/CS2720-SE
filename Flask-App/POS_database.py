"""
File: models.py
Author: Ethan Morisette; Braden Menke
Created: 03/09/2016 (Last Modified: 4/24/2016)
Purpose: Contains all database interaction functions for passing data between the user interface and databases.
"""
########################################################################################################################
# IMPORTS																											   #
########################################################################################################################

# from flask_sqlalchemy import *
import csv
import datetime as dt
import re
# from datetime import datetime
from io import StringIO

from flask import make_response
from sqlalchemy import func

from models import *


# from app import app

########################################################################################################################
# WRAPPER FUNCTION      																					           #
########################################################################################################################
def commitDB_Errorcatch(func):
    """
    Decorator to wrap a function in errorchecking
    :param func: decorates a function
    :return: the decorated function
    """
    def wrapperFunction(db, *args, **kwargs):
        """
        Wrapper function to error-check
        :param db: database pointer
        :param args: Whatever the wrapped function needs
        :param kwargs: Whatever the wrapped function needs
        :return: 0 if no issues, -1 if failure
        """
        try:
            func(db, *args, **kwargs)
            return 0
        except SQLAlchemyError as e:
            db.session.rollback()
            return -1  # !!

    # Hand back the function for future usage.
    return wrapperFunction

def getfromDB_Error(func):
    """
    Decorator to wrap a function in error-checking
    :param func: decorates a function
    :return: the decorated function
    """
    def wrapperFunction(db, *args, **kwargs):
        """
        Wrapper function to error-check
        :param db: database pointer
        :param args: As needed by the function
        :param kwargs: As needed by the function
        :return: the function's return value, or -1 if the operation fails.
        """
        try:
            v = func(db, *args, **kwargs)
            return v
        except SQLAlchemyError as e:
            return -1
    return wrapperFunction


# Defined: Products      (FULL)
#          Transaction   (FULL)
#          Items/Sold    (FULL)
#          Supplier      (FULL)
#          Discounts     (FULL)
#          Users         (FULL)
#
#
# Product access: getProduct{}(db, productID)
#                   Viable {}'s: Name, Price, Type, ShelfLife, MinInventory, InventoryCount, SupplierID
# Products also have: destroyProduct(db, id),
#                     addProduct(db, supplier_id, inventory_count, min_inventory, shelf_life, standard_price) (creative)
#
# Transaction Access: add,
#                     get(tuple, consisting of customer_name, customer_contact, payment_type, date-of-transaction),
#                     destroy
#
# Supplier Access: get(tuple of name, email),
#                  getID,
#                  add,
#                  destroy
#
# Others follow a similar vein


########################################################################################################################
# FUNCTION DEFINITIONS																								   #
########################################################################################################################


#########################################################################
# Product database Access                                               #
#########################################################################
@getfromDB_Error
def getProductName(db, productID):
    """
    Gives the product's name
    :param db: database pointer
    :param productID: int
    :return: str (name)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    return result.name



@getfromDB_Error
def getProductPrice(db, productID):
    """
    gets the price for a given ID
    :param db: database pointer
    :param productID: int
    :return: float (discounted price)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    price = result.standard_price
    # get the product from the discounts db
    discount = getDiscountFor(db, productID)
    # Get the total price!
    newPrice = price * (1 - discount)
    return newPrice  # PRICE (FLOAT)


@getfromDB_Error
def getProductShelfLife(db, productID):
    """
    get the shelf life for a given product (in days)
    :param db: database pointer
    :param productID: int
    :return: int (days)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    return result.shelf_life  # product's shelf life (INT)



@getfromDB_Error
def getProductMinInventory(db, productID):
    """
    Gives back the minimum inventory for a given product
    :param db: database pointer
    :param productID: int
    :return: int
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    return result.min_inventory  # product's min inventory (INT)


@getfromDB_Error
def getProductInventoryCount(db, productID):
    """
    Get the actual current inventory cost
    :param db: database pointer
    :param productID: int
    :return: int (current inventory)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    return result.inventory_count  # product's current inventory count


@getfromDB_Error
def getProductSupplierID(db, productID):
    """
    get the supplier from a product
    :param db: database pointer
    :param productID: int
    :return: int (supplier ID)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    return result.supplier_id  # product's supplier's ID


@commitDB_Errorcatch
def destroyProduct(db, productID):
    """
    Destroys a productID from the database
    :param db: database pointer
    :param productID: int
    :return: -
    """
    # Kill it!
    db.session.query(Product).filter(Product.id == productID).delete()
    # Commit
    db.session.commit()


@commitDB_Errorcatch
def addProduct(db, name, supplier_id, min_inventory, shelf_life, standard_price):
    """
    Builds and creates a product given all the info about it.
    :param db: database pointer
    :param supplier_id: int
    :param min_inventory: int
    :param shelf_life: integer
    :param standard_price: float
    :return: -
    """
    # Build one
    db.session.add(Product(name, supplier_id, min_inventory, shelf_life, standard_price))
    # commit our addition!
    db.session.commit()


@commitDB_Errorcatch
def incProduct(db, productID):
    """
    Adds one to the product's inventory_count
    :param db: database pointer
    :param productID: int
    :return: -
    """
    # Get our row
    result = db.session.query(Product).filter(Product.id == productID).first()
    # Increment the row
    result.inventory_count += 1
    # Needs to be committed outside of here


@commitDB_Errorcatch
def decProduct(db, productID):
    """
    Adds one to the product's inventory_count
    :param db: database pointer
    :param productID: int
    :return: -
    """
    # Get our row
    result = db.session.query(Product).filter(Product.id == productID).first()
    # Increment the row
    result.inventory_count -= 1
    # Needs to be committed outside of here

@getfromDB_Error
def getMaxProductID(db):
    """
    Gets the max product id in the products table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(Product.id)).first()
    return result[0]


#########################################################################
# Items/ItemSold database Access                                        #
#########################################################################
# Notes:	this is intended to take all of the rows we add locally and commit them together to the DB;
#			"Update Stock" and "Finish Transaction" buttons will use this procedure
@commitDB_Errorcatch
def updateItemTable(db, rowsList):
    """
    Update the table given a list of rows
    :param db: database pointer
    :param rowsList: list of rows
    :return: -
    """
    for row in rowsList:
        for x in range(0, row.quantity):
            db.session.add(Item(row.product_id, row.inventory_cost))
            incProduct(db, row.product_id)
    db.session.commit()

def updateCashierTable(db, rowsList, customerName, customerContact, paymentType):
    """
    update the items_sold, items, and transaction tables given a list of rows
    :param db: database pointer
    :param rowsList: list of row objects
    :param customerName: String
    :param customerContact: String
    :param paymentType: Int
    :return:
    """

    transactionID = addTransaction(db, customerName, customerContact, paymentType)
    for row in rowsList:
        popItemToItemSold(db, row.item_id, row.price, transactionID)


@commitDB_Errorcatch
def popItemToItemSold(db, itemID, priceSoldAt, transactionID):
    """
    Given an item, price, and a transactionID, moves an item from Items to ItemSold
    :param db: database pointer
    :param itemID: int
    :param priceSoldAt: float
    :param transactionID: int
    :return: -
    """
    # Decrement the product count for this item
    decProduct(db, getItemProduct(db, itemID))
    # Add the new thing into the ItemSold portion
    db.session.add(ItemSold(itemID, priceSoldAt, transactionID))
    # Get and destroy the old Item out of the database
    db.session.query(Item).filter(Item.id == itemID).delete()
    # Finalize the changes.
    db.session.commit()


@commitDB_Errorcatch
def addItem(db, product_id, inventory_cost):
    """
    Add a singular item to the items database
    :param db: database pointer
    :param product_id: int
    :param inventory_cost: float
    :return: -
    """
    # Build one
    db.session.add(Item(product_id, inventory_cost))
    incProduct(db, product_id)
    # Commit it
    db.session.commit()


@commitDB_Errorcatch
def destroyItem(db, itemID):
    """
    Destroys an item out of the pointed database
    :param db: database pointer
    :param itemID: int
    :return: -
    """
    # Decrement the product
    decProduct(db, getItemProduct(db, itemID))
    # Find and destroy the thingie
    db.session.query(Item).filter(Item.id == itemID).delete()
    # Commit the changes
    db.session.commit()

@getfromDB_Error
def getItemProduct(db, itemID):
    """
    Get an item's linked product id
    :param db: database pointer
    :param itemID: int
    :return: int
    """
    # Get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing off
    return item.product_id


@getfromDB_Error
def getItemCost(db, itemID):
    """
    Get an item's cost
    :param db: database pointer
    :param itemID: int
    :return: float (cost)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.inventory_cost


@getfromDB_Error
def getItemExpirationDate(db, itemID):
    """
    Get an item's expiration date
    :param db: database pointer
    :param itemID: int
    :return: datetime object (of expiration)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.expiration_date


@getfromDB_Error
def getItemAuthor(db, itemID):
    """
    Get the author of an item (?)
    :param db: database pointer
    :param itemID: int
    :return: int (the author's id)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.author_id


@getfromDB_Error
def getItemData(db, itemID):
    """
    Function to get all the data from the db about an item.
    :param db: database pointer
    :param itemID: int
    :return: Tuple, containing: product_id, inventory_cost, expiration_date, author_id
    """
    # Get ALL THE DATA
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # construct a tuple
    itemTup = tuple([item.product_id,
                     item.inventory_cost,
                     item.expiration_date,
                     item.author_id])
    return itemTup

@getfromDB_Error
def getMaxItemID(db):
    """
    Gets the max item id in the item table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(Item.id)).first()
    return result[0]

@getfromDB_Error
def getMaxItemSoldID(db):
    """
    Gets the max item id in the item table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(ItemSold.id)).first()
    return result[0]


#########################################################################
# Supplier database Access                                              #
#########################################################################
@getfromDB_Error
def getSupplier(db, supplierID):
    """
    Get the supplier's information
    :param db: database pointer
    :param supplierID: int
    :return: tuple containing name, email
    """
    # Grab the whole Supplier
    result = db.session.query(Supplier).filter(Supplier.id == supplierID).first()
    # filter the ID since we already have that.
    retTuple = tuple([result.name, result.email])
    return retTuple


@getfromDB_Error
def getSupplierName(db, supplierID):
    """
    Get supplier's name
    :param db: database pointer
    :param supplierID: int
    :return: str (name)
    """
    return getSupplier(db, supplierID)[0]


@getfromDB_Error
def getSupplierEmail(db, supplierID):
    """
    Get supplier's name
    :param db: database pointer
    :param supplierID: int
    :return: str (email)
    """
    return getSupplier(db, supplierID)[1]


@getfromDB_Error
def getSupplierID(db, supplierString):
    """
    Get the supplier's ID based on their name
    :param db: database pointer
    :param supplierString: string, composed of supplier's name
    :return: int : supplier's ID
    """
    # Get the supplier
    result = db.session.query(Supplier).filter(Supplier.name == supplierString).first()
    # just hand back the ID
    return result.id


@commitDB_Errorcatch
def addSupplier(db, supplierName, supplierEmail):
    """
    add a supplier to the database.
    :param db: database pointer
    :param supplierName: str
    :param supplierEmail: str
    :return: int (supplier's generated ID)
    """
    # Add and construct the supplier
    db.session.add(Supplier(supplierName, supplierEmail))
    # Extract the ID from the database (since it gens on-the-spot)
    retID = getSupplierID(db, supplierName)
    # Return
    return retID


@commitDB_Errorcatch
def destroySupplier(db, supplierID):
    """
    Destroys a supplier from the db
    :param db: database pointer
    :param supplierID: int
    :return: -
    """
    # Kill it!
    db.session.query(Supplier).filter(Supplier.id == supplierID).delete()
    # Commit our changes
    db.session.commit()

@getfromDB_Error
def getMaxSupplierID(db):
    """
    Gets the max supplier id in the suppliers table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(Supplier.id)).first()
    return result[0]

#########################################################################
# Discount database Access                                              #
#########################################################################
@getfromDB_Error
def getDiscountFor(db, productID):
    """
    Get any discounts for the product ID
    :param db: database pointer
    :param productID: int
    :return: float (between 0.0-1.0; a percentage)
    """
    # Get the discount tuple if it satisfies conditionals                   ::Correct product, correct date.
    # Get the discount tuple if it satisfies conditionals
    currentDiscount = db.session.query(Discount).filter(Discount.product_id == productID)\
                                                .filter(Discount.start_date <= datetime.date.today())\
                                                .filter(Discount.end_date >= datetime.date.today())\
                                                        .first()  # Pick the first one.
    # Filter the price out; or 0 for no matches
    if currentDiscount is None:
        return 0
    else:
        return currentDiscount.discount


@commitDB_Errorcatch
def addDiscount(db, productID, discPercent, startDate, endDate):
    """
    Add a discount to the table
    :param db: database pointer
    :param productID: int
    :param discPercent: float (0.0-1.0, a percentage)
    :param startDate: datetime object
    :param endDate: datetime object
    :return: -
    """
    # Create the discount portion
    db.session.add(Discount(productID, startDate, endDate, discPercent))
    # Save it to the database
    db.session.commit()


@commitDB_Errorcatch
def destroyDiscount(db, discountID):
    """
    Destroy a discount out of the db
    :param db: database pointer
    :param discountID: int
    :return: -
    """
    # Kill it!
    db.session.query(Discount).filter(Discount.id == discountID).delete()
    # Commit our changes
    db.session.commit()

@getfromDB_Error
def getMaxDiscountID(db):
    """
    Gets the max discount id in the discounts table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(Discount.id)).first()
    return result[0]

#########################################################################
# Transaction database Access                                           #
#########################################################################
@getfromDB_Error
def getTransaction(db, transactionID):
    """
    Get all the stuff about a transaction given the ID
    :param db: database pointer
    :param transactionID: int
    :return: tuple, consisting of customer_name, customer_contact, payment_type, date-of-transaction
    """
    # Get the transaction
    transaction = db.session.query(Transaction).filter(Transaction.id == transactionID).first()
    # Structure it into a tuple
    retT = tuple([transaction.cust_name, transaction.cust_contact,
                  transaction.payment_type, transaction.date])
    # Return that.
    return retT


@commitDB_Errorcatch
def destroyTransaction(db, transactionID):
    """
    Destroy a transaction given the ID
    :param db: database pointer
    :param transactionID: int
    :return: -
    """
    # Kill it!
    db.session.query(Transaction).filter(Transaction.id == transactionID).delete()
    # Commit this obliteration
    db.session.commit()


@getfromDB_Error
def addTransaction(db, cust_name, cust_contact, payment_type):
    """
    Add a transaction
    :param db: database pointer
    :param cust_name: str
    :param cust_contact: str
    :param payment_type: int
    :return: -
    """
    # Create the transaction
    db.session.add(Transaction(cust_name, cust_contact, payment_type))
    # get the transaction ID of the transaction added
    result = db.session.query(func.max(Transaction.id)).first()
    # Commit that
    db.session.commit()
    # return the transaction ID of most recent transaction add
    return result[0]

@getfromDB_Error
def getMaxTransactionID(db):
    """
    Gets the max transaction id in the transactions table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(Transaction.id)).first()
    return result[0]

#########################################################################
# User database Access                                                  #
#########################################################################
@getfromDB_Error
def getUser(db, id):
    """
    Gets a user's info
    :param db: database pointer
    :param id: int
    :return:
    """
    #Find our user!
    userInfo = db.session.query(User).filter(User.id == id).first()
    #Build a tuple
    retTup = tuple([userInfo.name,
                    userInfo.password,
                    userInfo.permissions])
    return retTup


@getfromDB_Error
def getUserName(db, id):
    """
    Gets the user's name
    :param db: database pointer
    :param id: int
    :return: str (user's name)
    """
    return getUser(db, id)[0]


@getfromDB_Error
def getUserPassword(db, id):
    """
    Get the user's password (HASHED)
    :param db: database pointer
    :param id: int
    :return: str (hashed password)
    """
    return getUser(db, id)[1]


@getfromDB_Error
def getUserPermissions(db, id):
    """
    Get the user's permissions
    :param db: database pointer
    :param id: int
    :return: int (user's permission level)
    """
    return getUser(db, id)[2]


@commitDB_Errorcatch
def addUser(db, name, password, permissions):
    """
    Creates and adds to a database a user
    :param db: database pointer
    :param name: str
    :param password: str (unhashed!)
    :param permissions: int (1-3)
    :return: -
    """
    # Create the thing!
    db.session.add(User(name, password, permissions))
    # Commit our change!
    db.session.commit()


@commitDB_Errorcatch
def destroyUser(db, id):
    """
    destructify a user and all their data!!!
    :param db: database pointer
    :param id: int
    :return: -
    """
    # Kill it!
    db.session.query(User).filter(User.id == id).delete()
    # Commit the change!
    db.session.commit()

@getfromDB_Error
def getMaxUserID(db):
    """
    Gets the max user id in the users table
    :param db: database pointer
    :return: integer
    """

    result = db.session.query(func.max(User.id)).first()
    return result[0]


#########################################################################
#########################################################################
# Editing Databases                                                     #
#########################################################################
#########################################################################
@commitDB_Errorcatch
def editProduct(db, productID, name, supplier_id, inv_count,
                min_inventory, shelf_life, standard_price):
    """
    Give me all the things, I'll edit the ones you change.
        IF any of the fields are empty, don't change them!
    :param db: database pointer
    :param productID: int
    :param name: str (new name)
    :param supplier_id: int (new)
    :param inv_count: int (new)
    :param min_inventory: int (new)
    :param shelf_life: int (new)
    :param standard_price: float (new)
    :return: -
    """
    result = db.session.query(Product).filter(Product.id == productID).first()
    if name != '':
        result.name = name
    if supplier_id != '':
        result.supplier_id = int(supplier_id)
    if inv_count != '':
        result.inventory_count = int(inv_count)
    if min_inventory != '':
        result.min_inventory = int(inv_count)
    if shelf_life != '':
        result.shelf_life = int(shelf_life)
    if standard_price != '':
        result.standard_price = float(standard_price)
    db.session.commit()


@commitDB_Errorcatch
def editSupplier(db, id, name, email):
    """
    Give me the things, I'll edit the changed thigns.
        Any empty fields will be unchanged
    :param db: database pointer
    :param id: int
    :param name: str (name)
    :param email: str (email)
    :return: -
    """
    result = db.session.query(Supplier).filter(Supplier.id == id).first()
    if name != '':
        result.name = name
    if email != '':
        result.email = email
    db.session.commit()


@commitDB_Errorcatch
def editUser(db, id, name, password, permissions):
    """
    Give me all the things, I'll edit changed things
    :param db: database pointer
    :param id: int
    :param name: str (username)
    :param password: str (unhashed password)
    :param permissions: int
    :return: -
    """
    result = db.session.query(User).filter(User.id == id).first()
    if name != '':
        result.name = name
    if password != '':
        result.password = bcrypt.generate_password_hash(password)
    if permissions != '':
        result.permissions = int(permissions)
    db.session.commit()


@commitDB_Errorcatch
def editDiscount(db, id, product_id, start_date, end_date, percent):
    """
    Give it all the things, it'll edit the non-empty ones
    :param db: database pointer
    :param id: int
    :param start_date: datetime
    :param end_date: datetime
    :param percent: float (0.0-1.0)
    :return: -
    """
    result = db.session.query(Discount).filter(Discount.id == id).first()
    if product_id != '':
        result.product_id = int(product_id)
    if start_date != '':
        match = re.match(r'''(?P<month>\d\d?).(?P<day>\d\d?).(?P<year>\d\d\d\d)''', str(start_date))
        result.start_date = dt.datetime(match.groups('year'), match.groups('month'), match.groups('day'))
    if end_date != '':
        match = re.match(r'''(?P<month>\d\d?).(?P<day>\d\d?).(?P<year>\d\d\d\d)''', str(end_date))
        result.end_date = dt.datetime(match.groups('year'), match.groups('month'), match.groups('day'))
    if percent != '':
        result.discount = float(percent)
    db.session.commit()


@commitDB_Errorcatch
def editItem(db, id, product_id, inventory_cost):
    """
    Give it all the things, it'll fix them up real good.
    :param db: database pointer
    :param id: int
    :param product_id: int
    :param inventory_cost: float
    :return: -
    """
    result = db.session.query(Item).filter(Item.id == id).first()
    if product_id != '':
        result.product_id = int(product_id)
    if inventory_cost != '':
        result.inventory_cost = float(inventory_cost)
    db.session.commit()


@commitDB_Errorcatch
def editItemSold(db, id, item_id, sold_at, transaction_id):
    """
    Give it all the things, it'll fix them up real good.
    :param db: database pointer
    :param id: int
    :param item_id: int
    :param sold_at: float
    :param transaction_id: int
    :return: -
    """
    result = db.session.query(ItemSold).filter(ItemSold.id == id).first()
    if item_id != '':
        try:
            result.item_id = int(item_id)
        except ValueError:
            raise
    if sold_at != '':
        try:
            result.price_sold = float(sold_at)
        except ValueError:
            raise
    if transaction_id:
        try:
            result.transaction_id = int(transaction_id)
        except ValueError:
            raise
    db.session.commit()

@commitDB_Errorcatch
def editTransaction(db, transactionID, cust_name, cust_contact, payment_type):
    """
    Give this all the things, and it'll edit the database to match
    :param db: database pointer
    :param transactionID: int
    :param cust_name: string
    :param cust_contact: string
    :param payment_type: int
    :return: -
    """
    result = db.session.query(Transaction).filter(Transaction.id == transactionID).first()
    if cust_name != '':
        result.cust_name = cust_name
    if cust_contact != '':
        result.cust_contact = cust_contact
    if payment_type != '':
        try:
            result.payment_type = int(payment_type)
        except ValueError:
            raise
    db.session.commit()

#########################################################################
# Reporting Databases                                                   #
#########################################################################
#@app.route('/download')
@getfromDB_Error
def toCSV(db, theRedPill, dateTup = None): # Should ask for a string and properly give back the right database's setup
    # TODO Joined tables : items_sold + transactions
    """
    Brings in a string of the type, gives ya' a .csv for that.
    :param db: database pointer
    :param theRedPill: str (the string of the type)
    :return: response to a flask app that instantiates a download
    """
    DATED_TABLES = ["discounts", # Discount.start_date / .end_date
                    "transactions", # Transaction.date
                    "items_sold"] # getTransaction(db, typeType.transactionID)[3]
    if theRedPill == 'Users':
        typeStr  = 'users'
        typeType =  User
    elif theRedPill == 'Discounts':
        typeStr  = 'discounts'
        typeType =  Discount
    elif theRedPill == 'Items Sold':
        typeStr  = 'items_sold'
        typeType =  ItemSold
    elif theRedPill == 'Items in Inventory':
        typeStr  = 'inventory'
        typeType =  Item
    elif theRedPill == 'Suppliers':
        typeStr  = 'supplier'
        typeType =  Supplier
    elif theRedPill == 'Transactions':
        typeStr  = 'transactions'
        typeType =  Transaction
    elif theRedPill == 'Products':
        typeStr  = 'products'
        typeType =  Product
    else:
        typeStr  = 'inventory'
        typeType =  Item

    records = []
    # Get dated stuff if we're given a date range
    if dateTup is not None\
            and typeStr in DATED_TABLES:
        start = dateTup[0]
        end   = dateTup[1]
        if typeStr == "items_sold":
            # get only items sold during the date range.
            records = db.session.query(typeType).filter(getTransaction(db, typeType.transaction_id)[3] > start)\
                                                .filter(getTransaction(db, typeType.transaction_id)[3] < end).all()
        elif typeStr == "transactions":
            records = db.session.query(typeType).filter(typeType.date > start)\
                                                .filter(typeType.date < end).all()
                                                # Transactions that occur between dates.
        else:
            records = db.session.query(typeType).filter(typeType.start_date > start)\
                                                .filter(typeType.start_date < end).all()
                                                # give ONLY start dates within range
    # No dates given, get the whole table.
    else:
        records = db.session.query(typeType).all()
    if len(records) == 0:
        return ('', 204)

    si = StringIO()

    outcsv = csv.writer(si)
    outcsv.writerow(records[0].__table__.columns._data.keys())
    for row in records:
        row_as_list = []
        for thing in row.__table__.columns._data:
            row_as_list.append(getattr(row, thing))
        outcsv.writerow(row_as_list)

    csvVals = si.getvalue()
    response = make_response(csvVals)
    response.headers["Content-Disposition"] = "attachment; filename={}_{}-{}-{}.csv".format(typeStr,
                                                                                            dt.datetime.today().month,
                                                                                            dt.datetime.today().day,
                                                                                            dt.datetime.today().year,)
    response.headers["Content-Type"] = "text/csv"

    return response


#@app.route('/download')
@getfromDB_Error
def reportInfoCSV(db, dateTup = None):
    """
    Optional date range; gives a joined csv of things.
    :param db: database pointer
    :param dateTup: tuple; optional- should be of type (start_date,end_date,) #Doesn't make sense in context#
    :return: response to a flask app that instantiates a download
    """
    # SQLAlchemy is fucking magic. Look at this shit:
    allItemInfo = db.session.query(Item).join(Product).join(Supplier).all()
    # That's supposed to work just right; automagically joins on foreign keys without specifications. Boom.
    si = StringIO()

    outcsv = csv.writer(si)
    outcsv.writerow(allItemInfo[0].__table__.columns._data.keys())
    for row in allItemInfo:
        row_as_list = []
        for thing in row.__table__.columns._data:
            row_as_list.append(getattr(row, thing))
        outcsv.writerow(row_as_list)

    csvVals = si.getvalue()
    response = make_response(csvVals)
    response.headers["Content-Disposition"] =\
        "attachment; filename=inventory_report_{}-{}-{}.csv".format(dt.datetime.today().month,
                                                                    dt.datetime.today().day,
                                                                    dt.datetime.today().year, )
    response.headers["Content-Type"] = "text/csv"
    return response


@getfromDB_Error
def reportRevenueAudit(db, dateTup = None):
    """
    Optional date range; gives a joined csv of things.
    :param db: database pointer
    :param dateTup: tuple; optional- should be of type (start_date,end_date,)
    :return: response to a flask app that instantiates a download
    """
    # SQLAlchemy is fucking magic. Look at this shit:
    start = dateTup[0]
    end = dateTup[1]
    allItemInfo = db.session.query(ItemSold).join(Transaction, ItemSold.transaction_id==Transaction.id).\
        filter(getTransaction(db, ItemSold.transaction_id)[3] >= start).\
        filter(getTransaction(db, ItemSold.transaction_id)[3] <= end).all()
    # That's supposed to work just right; automagically joins on foreign keys without specifications. Boom.
    si = StringIO()

    outcsv = csv.writer(si)
    outcsv.writerow(allItemInfo[0].__table__.columns._data.keys())
    for row in allItemInfo:
        row_as_list = []
        for thing in row.__table__.columns._data:
            row_as_list.append(getattr(row, thing))
        outcsv.writerow(row_as_list)
    csvVals = si.getvalue()
    response = make_response(csvVals)
    response.headers["Content-Disposition"] = \
        "attachment; filename=revenue_audit_{}-{}-{}.csv".format(dt.datetime.today().month,
                                                                    dt.datetime.today().day,
                                                                    dt.datetime.today().year)
    response.headers["Content-Type"] = "text/csv"
    return response


#########################################################################
# Determine Ordering                                                    #
#########################################################################
@getfromDB_Error
def areWeGoingToRunOutOf(db, product_id):
    """
    Are we going to run out this week?
    :param db: database pointer
    :param product_id: int
    :return: True/False, prediction
    """
    oneWeekAgo   = dt.date.today() - dt.timedelta(weeks=1) # Does what it says on the box.
    productDelta = db.session.query(ItemSold).filter(ItemSold.product_id == product_id)\
        .filter(oneWeekAgo <= getTransaction(db, ItemSold.transaction_id)[3])\
        .count() # Count how many we would've had.
    thisProduct = db.session.query(Product).filter(Product.id == product_id).first()
    if (thisProduct.inventory_count - productDelta) < thisProduct.min_inventory:
        return thisProduct.join(Supplier)
        # return True  # We WILL run out (maybe)
    else:
        return False # We WONT run out (maybe)


#@app.route('/download')
@getfromDB_Error
def runOutReport(db):
    """
    What things will we run out of this week
    :param db: database pointer
    :return: response to a flask app that instantiates a download
    """
    fullTable = db.session.query(Product).all()
    predictionsList = []
    for line in fullTable:
        thisPrediction = areWeGoingToRunOutOf(db, line.id)
        if thisPrediction != False:
            #thisPrediction = thisPrediction.join(Supplier)
            predictionsList.append(thisPrediction)
        else:
            continue
    # If there are no predictions, empty response.
    if len(predictionsList) == 0:
        return ('', 204)

    si = StringIO()
    outcsv = csv.writer(si)
    outcsv.writerow(predictionsList[0].__table__.columns._data)
    for row in predictionsList:
        row_as_list = []
        for thing in row.__table__.columns._data:
            row_as_list.append(getattr(row, thing))
        outcsv.writerow(row_as_list)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] =\
        "attachment; filename = product_order_{}-{}-{}.csv".format(dt.datetime.today().month,
                                                                   dt.datetime.today().day,
                                                                   dt.datetime.today().year)
    output.headers["Content-type"] = "text/csv"
    return output

#########################################################################
# On-the-fly reporting                                                  #
#########################################################################
@getfromDB_Error
def revenueCheck(db, time):
    """
    Get the revenue for a given custom time-tuple or a given string (day, week, month)
    :param db: database pointer
    :param time: "day", "week", "month", or a tuple of (start, end)
    :return: (revenue, cost, prophet,) tuple
    """
    if time == 'day':
        thisMorning = dt.date.today() -dt.timedelta(days=1)
        timetup = (thisMorning, dt.date.today()+dt.timedelta(days=1),)
    elif time == 'week':
        aWeekAgo = dt.date.today() - dt.timedelta(weeks = 1)
        timetup = (aWeekAgo, dt.date.today()+dt.timedelta(days=1),)
    elif time == 'month':
        aMonthAgo = dt.date.today() - dt.timedelta(weeks = 4)
        timetup = (aMonthAgo, dt.date.today()+dt.timedelta(days=1),)
    elif (type(time) == tuple):
        timetup = time
    else:
        raise ValueError
    items_sold = db.session.query(ItemSold).all()
    in_range = []
    for itemSold in items_sold:
        if getTransaction(db, itemSold.transaction_id)[3] >= timetup[0]:
            if getTransaction(db, itemSold.transaction_id)[3] <= timetup[1]:
                in_range.append(itemSold)
    revenue = 0
    cost = 0
    for itemsold in in_range:
        revenue += itemsold.price_sold
        cost += itemsold.inventory_cost

    return [revenue, cost, revenue-cost]
