# Author: Ethan Morisette
# Created: 4/1/2016
# Purpose: module that holds all class definitions, function definitions, and variables for displaying information
# to the WEBSITE tables (not to be confused with our db tables)

#######################################################################################################################
#  IMPORTS																																											  #
#######################################################################################################################
from flask import *


#######################################################################################################################
#  CLASS DEFINITIONS         																																						  #
#######################################################################################################################
class Row:
    def __init__(self, row_id):
        self.row_id = row_id


class UserRow(Row):
    def __init__(self, row_id, user_id, username, password, permissions):
        Row.__init__(self, row_id)
        self.user_id = user_id
        self.username = username
        self.password = password
        self.permissions = permissions


class SupplierRow(Row):
    def __init__(self, row_id, supplier_id, name, email):
        Row.__init__(self, row_id)
        self.supplier_id = supplier_id
        self.name = name
        self.email = email


class ProductsRow(Row):
    def __init__(self, row_id, product_id, name, supplier_id,
                 inventory_count, min_inventory, shelf_life, standard_price):
        Row.__init__(self, row_id)
        self.product_id = product_id
        self.name = name
        self.supplier_id = supplier_id
        self.inventory_count = inventory_count
        self.min_inventory = min_inventory
        self.shelf_life = shelf_life
        self.standard_price = standard_price


class ItemRow(Row):
    def __init__(self, row_id, item_id, product_id, inventory_cost, expiration_date):
        Row.__init__(self, row_id)
        self.item_id = item_id
        self.product_id = product_id
        self.inventory_cost = inventory_cost
        self.expiration_date = expiration_date


class ItemSoldRow(Row):
    def __init__(self, row_id, item_sold_id, item_id, product_id, price_sold, inventory_cost, transaction_id):
        Row.__init__(self, row_id)
        self.item_sold_id = item_sold_id
        self.item_id = item_id
        self.product_id = product_id
        self.price_sold = price_sold
        self.inventory_cost = inventory_cost
        self.transaction_id = transaction_id


class DiscountRow(Row):
    def __init__(self, row_id, discount_id, product_id, start_date, end_date, discount):
        Row.__init__(self, row_id)
        self.discount_id = discount_id
        self.product_id = product_id
        self.start_date = start_date
        self.end_date = end_date
        self.discount = discount


class TransactionRow(Row):
    def __init__(self, row_id, trans_id, cust_name, cust_contact, payment_type, date):
        Row.__init__(self, row_id)
        self.trans_id = trans_id
        self.cust_name = cust_name
        self.cust_contact = cust_contact
        self.payment_type = payment_type
        self.date = date


class Table:
    """
    Purpose: to hold a variety of table information beyond the rows themselves (e.g. table rows, potential profit from
    all items currently in the table, etc.)
    """
    def __init__(self):
        self.rowsList = []  # list of row objects (receiptRow, stockRow, or saleRow)
        self.rowCount = 0  # integer
        self.mostRecentRow = None  # row object (receiptRow, stockRow, or saleRow)

    def clear_table(self):
        """
        Clear all contents of a display table. Intended for use after a batch of data is committed to the database.
        :return: None
        """
        self.rowsList.clear()
        self.rowCount = 0
        self.mostRecentRow = None

    def add_row(self, new_row):
        """
        Adds a row to a table object.
        Throws an error if new_row is not the same class as any other existing rows in the table.
        :param new_row: An instance of the Row class or one of its sub-classes.
        :return: None
        """
        for i in self.rowsList:
            if not isinstance(new_row, i):
                raise TypeError("The new row does not match the type of the other existing rows.")
        self.rowsList.append(new_row)
        self.rowCount += 1
        self.mostRecentRow = new_row


#######################################################################################################################################################################################
# GLOBAL VARIABLES          																																						  #
#######################################################################################################################################################################################

transactionTable = Table()
inventoryTable = inventoryTable()
discountTable = Table()


#######################################################################################################################################################################################
# FUNCTION DEFINITIONS         																																						  #
#######################################################################################################################################################################################

# In: 		productName (string), productID (integer), quantity (integer), pricePerUnit(float)
# Out: 		none
# Purpose: 	
# Note: 	the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addTransactionRow(productName, productID, quantity, pricePerUnit):
    newRow = transactionRow(productName, productID, quantity, pricePerUnit)
    transactionTable.add_row(newRow)


# In:		productID (integer), quantity (integer), expDate (POS_display.formattedDate), itemCost (float), productPrice (float)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input> html element (i.e. <input name="cashierBarcode">)
def addInventoryRow(productName, productID, quantity, expDate, itemCost, productPrice):
    newRow = inventoryRow(productName, productID, quantity, expDate, itemCost)
    inventoryTable.add_row(newRow)
    inventoryTable.addProfitPotential(itemCost, productPrice, quantity)


# In:		productID (integer), saleStart (date), saleEnd (date), salePrice (float)
# Out:		none
# Purpose:	
# Note:		the inputs are strings that correspond to the name of the <input>
# html element (i.e. <input name="cashierBarcode">)
def addDiscountRow(productName, productID, saleStart, saleEnd, salePrice):
    newRow = discountRow(productName, productID, saleStart, saleEnd, salePrice)
    discountTable.add_row(newRow)


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
