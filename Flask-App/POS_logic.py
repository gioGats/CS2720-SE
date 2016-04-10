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
class transactionRow:
	def __init__(self, productName, productID, quantity, pricePerUnit):
		self.productName 	= productName			# string
		self.productID 		= productID				# integer
		self.quantity 		= quantity				# integer
		self.pricePerUnit 	= pricePerUnit			# float

# Purpose: holds all information in a row of the stocking table 
class inventoryRow:
	def __init__(self, productName, productID, quantity, expDate, itemCost):
		self.productName 	= productName			# string
		self.productID		= productID				# integer
		self.quantity 		= quantity				# integer
		self.expDate		= expDate				# POS_display.formattedDate
		self.itemCost		= itemCost				# float

# Purpose: holds all information in a row of the sale table
class discountRow:
	def __init__(self, productName, productID, saleStart, saleEnd, salePrice):
		self.productName 	= productName			# string
		self.productID 		= productID				# integer
		self.saleStart		= saleStart				# POS_display.formattedDate 
		self.saleEnd 		= saleEnd				# POS_display.formattedDate
		self.salePrice 		= salePrice				# float

# Purpose: to hold a variety of table information beyond the rows themselves (e.g. table rows, potential profit from all items currently in the table, etc.)
class table:
	def __init__(self):
		self.rowsList 		= []		# list of row objects (receiptRow, stockRow, or saleRow)
		self.rowCount 		= 0			# integer
		self.mostRecentRow 	= None		# row object (receiptRow, stockRow, or saleRow)

	# In: 		none
	# Out: 		none
	# Purpose: 	to clear all contents of a display table
	# Note: 	this is intended to be used after a batch of data is committed to the database
	def clearTable(self):
		self.rowsList.clear()
		self.rowCount			= 0
		self.mostRecentRow 		= None

	# In: 		newRow (row object (receiptRow, stockRow, or saleRow))
	# Out: 		none
	# Purpose: 	to update the contents of a table object
	# Note: 	
	def addRow(self, newRow):
		self.rowsList.append(newRow)
		self.rowCount 		+= 1
		self.mostRecentRow 	= newRow

class inventoryTable(table):
	def __init__(self):
		table.__init__(self)
		self.profitPotential = 0.00

	def clearTable(self):
		table.clearTable(self)
		self.profitPotential = 0.00

	def addRow(self, newRow):
		table.addRow(self, newRow)
		self.profitPotential = 0

	# In:		itemCost (float), productSalePrice (float)
	# Out:		none
	# Purpose:	to update the profit potential of the current inventory session by calculating productPrice - itemCost for each item added
	# Note:	
	def addProfitPotential(self, itemCost, productSalePrice):
		itemProfit = productSalePrice - itemCost
		profitPotential += itemProfit


#######################################################################################################################################################################################
# GLOBAL VARIABLES          																																						  #
#######################################################################################################################################################################################

transactionTable	= table()
inventoryTable		= inventoryTable()
discountTable		= table()

#######################################################################################################################################################################################
# FUNCTION DEFINITIONS         																																						  #
#######################################################################################################################################################################################

# In: 		productName (string), productID (integer), quantity (integer), pricePerUnit(float)
# Out: 		none
# Purpose: 	
# Note: 	the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addTransactionRow(productName, productID, quantity, pricePerUnit):
	newRow = transactionRow(productName, productID, quantity, pricePerUnit)
	transactionTable.addRow(newRow)

# In:		productID (integer), quantity (integer), expDate (POS_display.formattedDate), itemCost (float)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addInventoryRow(productName, productID, quantity, expDate, itemCost):
	newRow = inventoryRow(productName, productID, quantity, expDate, itemCost)
	inventoryTable.addRow(newRow)

# In:		productID (integer), saleStart (date), saleEnd (date), salePrice (float)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addDiscountRow(productName, productID, saleStart, saleEnd, salePrice):
	newRow = discountRow(productName, productID, saleStart, saleEnd, salePrice)
	discountTable.addRow(newRow)

#####################################################################################################################################################################################
# TEST FUNCTION DEFINITIONS 																																						#
#####################################################################################################################################################################################

# In:		tableName (table object)
# Out:		none
# Purpose:	to populate the GUI tables for testing purposes
def fillTable(tableName):
	if (tableName == "transactionTable"):
		for x in range(100):
			newRow = transactionRow("bananas", 12345, "N/A", 0.57)
			receiptTable.rowsList.append(newRow)
	elif (tableName == "inventoryTable"):
		for x in range(100):
			newRow = inventoryRow("matches", 13200, "N/A")
			stockingTable.rowsList.append(newRow)
	elif (tableName == "discountTable"):
		for x in range(100):
			newRow = discountRow("shoes", 13402, "07/23/2016", "07/25/2016", 0.02)
			saleTable.rowsList.append(newRow)
