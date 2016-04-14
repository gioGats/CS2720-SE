# Author: Ethan Morisette
# Created: 04/09/2016
# Last Modified:
# Purpose: to hold all of our database interactions in a single module 

#################################################################################################################################################
# IMPORTS																																		#
#################################################################################################################################################
from models import *
from datetime import date


#################################################################################################################################################
# FUNCTION DEFINITIONS																															#
#################################################################################################################################################

# In: 		db (pointer to a database), productId (integer) 
# Out: 		productName (string)
# Purpose: 	to return the name of a given product ID
# Notes:
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
def getProductPrice(db, productID):
    # TODO check if there is a sale price and if there is use that instead
    # TODO add error handling
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.standard_price).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    price = result.standard_price
    return price


# TODO getProduct : type, shelf_life, min_inventory, inventory_count, supplier_id

# In: 		db (pointer to a database), rowsList (a list of stockRow objects)
# Out:		none
# Purpose:	to commit a batch of data held in the current user's session
# Notes:	this is intended to take all of the rows we add locally and commit them together to the DB; 
#			"Update Stock" and "Finish Transaction" buttons will use this procedure
def updateItemTable(db, rowsList):
    for row in rowsList:
        db.session.add(Item(row.productID, row.expDate, row.itemCost, 1))
    db.session.commit()

# In: 		db (pointer to a database), supplierID (integer)
# Out:      tuple of supplier: name,email (str, str)
# Purpose:	gives all info about a supplier
# Notes:
def getSupplier(db, supplierID):
    #Grab the whole Supplier
    result = db.session.query(Supplier).filter(Supplier.id == supplierID).first()
    #filter the ID since we already have that.
    retTuple = tuple([result.name, result.email])
    return retTuple

# In: 		db (pointer to a database), supplierName (string)
# Out:      The ID of the supplier (since it's genned)
# Purpose:	gets the ID from a name. May just be supplemental for insSupplier
# Notes:
def getSupplierID(db, supplierString):
    #Get the supplier
    result = db.session.query(Supplier).filter(Supplier.name == supplierString).first()
    # just hand back the ID
    return result.id

# In: 		db (pointer to a database), supplierName (string), supplierEmail (string)
# Out:      The ID of the supplier (since it's genned)
# Purpose:	inserts a supplier into the supplier db
# Notes:
def insertSupplier(db, supplierName, supplierEmail):
    #Add and construct the supplier
    db.session.add(Supplier(supplierName, supplierEmail))
    #Extract the ID from the database (since it gens on-the-spot)
    retID = getSupplierID(db, supplierName)
    #Return
    return retID

# In: 		db (pointer to a database), productID
# Out:      Any sale price for the given productID
# Purpose:	gets the sale price for an item
# Notes:
def getDiscount(db, productID):
    #Get the a discount object if it exists
    #Filter the price out
    #return TODO: Do this coding.

# TODO getTransaction
