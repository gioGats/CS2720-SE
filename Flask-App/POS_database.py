# Author: Ethan Morisette
# Created: 04/09/2016
# Last Modified:
# Purpose: to hold all of our database interactions in a single module 

#################################################################################################################################################
# IMPORTS																																		#
#################################################################################################################################################
from app import db
from models import *
from POS_display import *

#################################################################################################################################################
# FUNCTION DEFINITIONS																															#
#################################################################################################################################################

# In: 		productId (integer) 
# Out: 		productName (string)
# Purpose: 	to return the name of a given product ID
# Notes:
def getProductName(productID):
	#TODO add error handling
	# make the query and receive a single tuple (first() allows us to do this)
	result = db.session.query(Product.name).filter(Product.id == productID).first()
	# grab the name in the keyed tuple received 
	name = result.name
	return name

# In: 		productID (integer)
# Out: 		productPrice (float)
# Purpose:	to retun the price of a given product ID
# Notes:
def getProductPrice(productID):
	#TODO check if there is a sale price and if there is use that instead
	#TODO add error handling
	# make the query and receive a single tuple (first() allows us to do this)
	result = db.session.query(Product.standard_price).filter(Product.id == productID).first()
	# grab the name in the keyed tuple received 
	price = result.standard_price
	return price

# In: 		localTable (POS_display.table object), databaseTable (models class)
# Out:		none
# Purpose:	to commit a batch of data held in the current user's session
# Notes:	this is intended to take all of the rows we add locally and commit them together to the DB; 
#			"Update Stock" and "Finish Transaction" buttons will use this procedure
def updateTable(localTable, databaseTable):
	return localTable
