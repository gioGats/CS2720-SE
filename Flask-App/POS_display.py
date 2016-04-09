# Author: Ethan Morisette
# Created: 4/1/2016
# Purpose: module that holds all class definitions, function definitions, and variables for displaying information to the WEBSITE tables (not to be confused with our db tables)

#######################################################################################################################################################################################
# IMPORTS																																											  #
#######################################################################################################################################################################################
from flask import *

#######################################################################################################################################################################################
# CLASS DEFINITIONS         																																						  #
#######################################################################################################################################################################################

# Purpose: holds all information in a row of the receipt table (aka information for a receipt!)
class receiptRow:
	def __init__(self, productName, productID, quantity, weight, pricePerUnit):
		self.productName 	= productName			# string
		self.productID 		= productID				# integer
		self.quantity 		= quantity				# integer
		self.weight 		= weight				# float	
		self.pricePerUnit 	= pricePerUnit			# float

# Purpose: holds all information in a row of the stocking table 
class stockRow:
	def __init__(self, productName, productID, quantity, weight):
		self.productName 	= productName			# string
		self.productID		= productID				# integer
		self.quantity 		= quantity				# integer
		self.weight			= weight				# float

# Purpose: holds all information in a row of the sale table
class saleRow:
	def __init__(self, productName, productID, saleStart, saleEnd, salePrice):
		self.productName 	= productName			# string
		self.productID 		= productID				# integer
		self.saleStart		= saleStart				# string
		self.saleEnd 		= saleEnd				# string
		self.salePrice 		= salePrice				# float

# Purpose: to hold a variety of table information beyond the rows themselves (e.g. table rows, potential profit from all items currently in the table, etc.)
class table:
	def __init__(self):
		self.rowsList 		= []		# list of row objects (receiptRow, stockRow, or saleRow)
		self.rowCount 		= 0			# integer
		self.mostRecentRow 	= None		# row object (receiptRow, stockRow, or saleRow)

#######################################################################################################################################################################################
# GLOBAL VARIABLES          																																						  #
#######################################################################################################################################################################################

receiptTable	= table()
stockingTable	= table()
saleTable		= table()

#######################################################################################################################################################################################
# FUNCTION DEFINITIONS         																																						  #
#######################################################################################################################################################################################

# In: 		productID (string), quantity (string), weight (string)
# Out: 		none
# Purpose: 	
# Note: 	the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addReceiptRow(productID, quantity, weight):
	productName 	= "bananas"
	pricePerUnit 	= 1.20
	newRow			= receiptRow(productName, request.form[productID], request.form[quantity], request.form[weight], pricePerUnit)
	receiptTable.rowsList.append(newRow)
	receiptTable.rowCount += 1
	receiptTable.mostRecentRow = newRow

# In:		productID (string), quantity (string), weight (string)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addStockingRow(productID, quantity, weight):
	productName 	= "matches"
	newRow 			= stockRow(productName, request.form[productID], request.form[quantity], request.form[weight])
	stockingTable.rowsList.append(newRow)
	stockingTable.rowCount += 1


# In:		productID (string), saleStart (string), saleEnd (string), salePrice (string)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addSaleRow(productID, saleStart, saleEnd, salePrice):
	productName 	= "shoes"
	newRow			= saleRow(productName, request.form[productID], request.form[saleStart], request.form[saleEnd], request.form[salePrice])
	saleTable.rowsList.append(newRow)
	saleTable.rowCount += 1

#####################################################################################################################################################################################
# TEST FUNCTION DEFINITIONS 																																						#
#####################################################################################################################################################################################

# In:		tableName (table object)
# Out:		none
# Purpose:	to populate the GUI tables for testing purposes
def fillTable(tableName):
	if (tableName == "receiptTable"):
		for x in range(100):
			newRow = receiptRow("bananas", 12345, "N/A", 300, 0.57)
			receiptTable.rowsList.append(newRow)
	elif (tableName == "stockingTable"):
		for x in range(100):
			newRow = stockRow("matches", 13200, 300, "N/A")
			stockingTable.rowsList.append(newRow)
	elif (tableName == "saleTable"):
		for x in range(100):
			newRow = saleRow("shoes", 13402, "07/23/2016", "07/25/2016", 0.02)
			saleTable.rowsList.append(newRow)
