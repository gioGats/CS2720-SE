# Author: Ethan Morisette; Braden Menke
# Created: 04/09/2016
# Last Modified: 4/16/2016
# Purpose: to hold all of our database interactions in a single module 

########################################################################################################################
# IMPORTS																											   #
########################################################################################################################
from flask.ext.sqlalchemy import SQLAlchemy
from models import *
from models_new import *
from datetime import datetime


########################################################################################################################
# WRAPPER FUNCTION      																					           #
########################################################################################################################
def getfromDB_Error(func):
    """
    Does errorchecking on get functions
        ErrorCodes:
    """

    def wrapperFunction(db, *args, **kwargs):
        try:
            func(db, *args, **kwargs)
        except SQLAlchemy.SQLAlchemyError as e:
            # TODO Error handle here!
            pass
    #Hand back the function for future usage.
    return wrapperFunction


#Defined: Products (Access)
#         Transaction (Access)
#         Supplier (FULL)
#

########################################################################################################################
# FUNCTION DEFINITIONS																								   #
########################################################################################################################

# In: 		db (pointer to a database), productId (integer) 
# Out: 		productName (string)
# Purpose: 	to return the name of a given product ID
# Notes:
@getfromDB_Error
def getProductName(db, productID):
    # TODO add error handling
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.name).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    name = result.name
    return name


# In: 		db (pointer to a database), productID (integer)
# Out: 		productPrice (float)
# Purpose:	to retun the price of a given product ID
# Notes:
@getfromDB_Error
def getProductPrice(db, productID):
    # TODO check if there is a sale price and if there is use that instead
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.standard_price).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    price = result.standard_price
    return price  # PRICE (FLOAT)


@getfromDB_Error
def getProductType(db, productID):
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.type).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    t = result.type
    return t  # type of product! (STRING)


@getfromDB_Error
def getProductShelfLife(db, productID):
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.shelf_life).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    shelfLife = result.shelf_life
    return shelfLife  # product's shelf life (INT)


@getfromDB_Error
def getProductMinInventory(db, productID):
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.min_inventory).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    mInventory = result.min_inventory
    return mInventory  # product's min inventory (INT)


@getfromDB_Error
def getProductInventoryCount(db, productID):
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.inventory_count).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    currInventory = result.inventory_count
    return currInventory  # product's current inventory count


@getfromDB_Error
def getProductSupplierID(db, productID):
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.supplier_id).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    supplierID = result.supplier_id
    return supplierID  # product's supplier's ID


# In: 		db (pointer to a database), rowsList (a list of stockRow objects)
# Out:		none
# Purpose:	to commit a batch of data held in the current user's session
# Notes:	this is intended to take all of the rows we add locally and commit them together to the DB; 
#			"Update Stock" and "Finish Transaction" buttons will use this procedure

@getfromDB_Error
def updateItemTable(db, rowsList):
    for row in rowsList:
        db.session.add(Item(row.productID, row.expDate, row.itemCost, 1))
    db.session.commit()


# In: 		db (pointer to a database), supplierID (integer)
# Out:      tuple of supplier: name,email (str, str)
# Purpose:	gives all info about a supplier
# Notes:
@getfromDB_Error
def getSupplier(db, supplierID):
    # Grab the whole Supplier
    result = db.session.query(Supplier).filter(Supplier.id == supplierID).first()
    # filter the ID since we already have that.
    retTuple = tuple([result.name, result.email])
    return retTuple


# In: 		db (pointer to a database), supplierName (string)
# Out:      The ID of the supplier (since it's genned)
# Purpose:	gets the ID from a name. May just be supplemental for insSupplier
# Notes:
@getfromDB_Error
def getSupplierID(db, supplierString):
    # Get the supplier
    result = db.session.query(Supplier).filter(Supplier.name == supplierString).first()
    # just hand back the ID
    return result.id


# In: 		db (pointer to a database), supplierName (string), supplierEmail (string)
# Out:      The ID of the supplier (since it's genned)
# Purpose:	inserts a supplier into the supplier db
# Notes:
@getfromDB_Error
def insertSupplier(db, supplierName, supplierEmail):
    # Add and construct the supplier
    db.session.add(Supplier(supplierName, supplierEmail))
    # Extract the ID from the database (since it gens on-the-spot)
    retID = getSupplierID(db, supplierName)
    # Return
    return retID


# In: 		db (pointer to a database), productID
# Out:      Any sale price for the given productID
# Purpose:	gets the sale price for an item
# Notes:
@getfromDB_Error
def getDiscountFor(db, productID):
    # Get the discount tuple if it satisfies conditionals
    currentDiscount = db.session.query(Discounts).filter(Discounts.product_id == productID,  # Is the right product
                                                         Discounts.start_date <= datetime.date(datetime.today()),
                                                         # Discount is running
                                                         Discounts.end_date > datetime.date(datetime.today())
                                                         # Discount hasn't ended
                                                         ).first()
    # Filter the price out; or 0 for no matches
    if currentDiscount is None:
        return 0
    else:
        return currentDiscount.discount

def addDiscount(db, productID, discPercent, startDate, endDate)


@getfromDB_Error
def getTransaction(db, transactionID):
    # Get the transaction
    transaction = db.session.query(Transaction).filter(Transaction.id == transactionID).first()
    # Structure it into a tuple
    retT = tuple([transaction.cust_name, transaction.cust_contact,
                  transaction.payment_type, transaction.date])
    # Return that.
    return retT
