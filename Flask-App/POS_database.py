# Author: Ethan Morisette; Braden Menke
# Created: 04/09/2016
# Last Modified: 3/20/2016
# Purpose: to hold all of our database interactions in a single module 

########################################################################################################################
# IMPORTS																											   #
########################################################################################################################

from flask_sqlalchemy import *
from sqlalchemy import func
from models import *
import re
import csv
import datetime as dt
from datetime import datetime


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
def addProduct(db, supplier_id, inventory_count, min_inventory, shelf_life, standard_price):
    """
    Builds and creates a product given all the info about it.
    :param db: database pointer
    :param supplier_id: int
    :param inventory_count: int
    :param min_inventory: int
    :param shelf_life: integer
    :param standard_price: float
    :return: -
    """
    # Build one
    db.session.add(Product(supplier_id, inventory_count, min_inventory, shelf_life, standard_price))
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
        db.session.add(Item(row.product_id, row.inventory_cost))
        incProduct(db, row.product_id)
    db.session.commit()

def updateCashierTable(db, rowsList):
    """
    update the items_sold, items, and transaction tables given a list of rows
    :param db: database pointer
    :param rowsList: list of row objects
    :return: -
    """
    for row in rowsList:
        transactionID = addTransaction(db, "Bob", "no@no.com", 1)
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
    decProduct(db, getItemProduct(db, itemID))
    # Add the new thing into the ItemSold portion
    db.session.add(ItemSold(itemID, priceSoldAt, transactionID))
    # Get and destroy the old Item out of the database
    db.session.query(Item).filter(Item.id == itemID).delete()
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
    db.commit()


@commitDB_Errorcatch
def destroyItem(db, itemID):    #TODO : actually document this
    """

    :param db:
    :param itemID:
    :return:
    """
    # Decrement the product
    decProduct(db, getItemProduct(itemID))
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
    currentDiscount = db.session.query(Discount).filter(Discount.product_id == productID)\
            .filter(Discount.start_date <= datetime.date(datetime.today()))\
            .filter(Discount.end_date > datetime.date(datetime.today())).first() # Pick the first one.
    # Get the discount tuple if it satisfies conditionals
    currentDiscount = db.session.query(Discount).filter(Discount.product_id == productID)\
                                                .filter(Discount.start_date <= datetime.date(datetime.today()))\
                                                .filter(Discount.end_date > datetime.date(datetime.today()))\
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


def getUserName(db, id):
    """
    Gets the user's name
    :param db: database pointer
    :param id: int
    :return: str (user's name)
    """
    return getUser(db, id)[0]


def getUserPassword(db, id):
    """
    Get the user's password (HASHED)
    :param db: database pointer
    :param id: int
    :return: str (hashed password)
    """
    return getUser(db, id)[1]


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
        match = re.match(r'''(?P<month>\d\d?).(?P<day>\d\d?).(?P<year>\d\d\d\d)''', start_date)
        result.start_date = dt.datetime(match.groups('year'), match.groups('month'), match.groups('day'))
    if end_date != '':
        match = re.match(r'''(?P<month>\d\d?).(?P<day>\d\d?).(?P<year>\d\d\d\d)''', end_date)
        result.end_date = dt.datetime(match.groups('year'), match.groups('month'), match.groups('day'))
    if percent != '':
        result.discount = float(percent)
    db.session.commit()


@commitDB_Errorcatch
def editItem(db, id, product_id, inventory_cost):
    """
    Give it all the things, it'll fix them up real good.
    :param db: database pointer
    :param id:
    :param product_id: int
    :param inventory_cost: float
    :return: -
    """
    result = db.session.query(Item).filter(Item.id == id).first()
    if product_id != '':
        result.product_id = int(product_id)
    if inventory_cost != '':
        result.inventory_count = float(inventory_cost)
    db.session.commit()


#########################################################################
# Reporting Databases                                                   #
#########################################################################
@commitDB_Errorcatch
def toCSV(db, theRedPill): # Should ask for a string and properly give back the right database's setup
    """
    Brings in a string of the type, gives ya' a .csv for that.
    :param db: database pointer
    :param theRedPill: str (the string of the type)
    :return: - , but creates a .csv file locally (?)
    """
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

    outfile = open('{}.csv'.format(typeStr), 'wb')
    outcsv = csv.writer(outfile)
    records = db.session.query(typeType).all()
    [outcsv.writerow([getattr(curr, column.name) for column in typeType.__mapper__.columns]) for curr in records]
    outfile.close()
