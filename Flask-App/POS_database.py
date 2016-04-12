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

# TODO add supplier to db
# TODO get supplier from db
# TODO getDiscount
# TODO getTransaction
