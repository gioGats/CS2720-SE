# Author: Ethan Morisette
# Created: 4/1/2016
# Purpose: module that holds all class definitions, function definitions, and variables for displaying information
# to the WEBSITE tables (not to be confused with our db tables)

#######################################################################################################################
#  IMPORTS
#######################################################################################################################
from flask import *


#######################################################################################################################
#  CLASS DEFINITIONS
#######################################################################################################################
class Row:
    def __init__(self):
        self.data = ""


class UserRow(Row):
    def __init__(self, user_id, username, password, permissions):
        """
        Holds data for the display of an entry from the users database table.
        :param user_id: int
        :param username: str
        :param password: str
        :param permissions: int
        :return: None
        """
        Row.__init__(self)
        self.user_id = user_id
        self.username = username
        self.password = password
        self.permissions = permissions


class SupplierRow(Row):
    def __init__(self, supplier_id, name, email):
        """
        Holds data for the display of an entry from the suppliers database table.
        :param supplier_id: int
        :param name: str
        :param email: str
        :return:
        """
        Row.__init__(self)
        self.supplier_id = supplier_id
        self.name = name
        self.email = email


class ProductsRow(Row):

    def __init__(self, product_id, name, supplier_id,
                 inventory_count, min_inventory, shelf_life, standard_price):
        """
        Holds data for the display of an entry from the products database table.
        :param product_id: int
        :param name: str
        :param supplier_id: int
        :param inventory_count: int
        :param min_inventory: int
        :param shelf_life: int
        :param standard_price: float
        :return: None
        """
        Row.__init__(self)
        self.product_id = product_id
        self.name = name
        self.supplier_id = supplier_id
        self.inventory_count = inventory_count
        self.min_inventory = min_inventory
        self.shelf_life = shelf_life
        self.standard_price = standard_price


class ItemRow(Row):
    def __init__(self, item_id, product_id, inventory_cost, expiration_date):
        """
        Holds data for the display of an entry from the items database table.
        :param item_id: int
        :param product_id: int
        :param inventory_cost: float
        :param expiration_date: datetime.date
        :return: None
        """
        Row.__init__(self)
        self.item_id = item_id
        self.product_id = product_id
        self.inventory_cost = inventory_cost
        self.expiration_date = expiration_date


class ItemSoldRow(Row):
    def __init__(self, item_sold_id, item_id, product_id, price_sold, inventory_cost, transaction_id):
        """
        Holds data for the display of an entry from the items_sold database table.
        :param item_sold_id: int
        :param item_id: int
        :param product_id: int
        :param price_sold: float
        :param inventory_cost: float
        :param transaction_id: int
        :return: None
        """
        Row.__init__(self)
        self.item_sold_id = item_sold_id
        self.item_id = item_id
        self.product_id = product_id
        self.price_sold = price_sold
        self.inventory_cost = inventory_cost
        self.transaction_id = transaction_id


class DiscountRow(Row):
    def __init__(self, discount_id, product_id, start_date, end_date, discount):
        """
        Holds data for the display of an entry from the discounts database table.
        :param discount_id: int
        :param product_id: int
        :param start_date: datetime.date
        :param end_date: datetime.date
        :param discount: float
        :return: None
        """
        Row.__init__(self)
        self.discount_id = discount_id
        self.product_id = product_id
        self.start_date = start_date
        self.end_date = end_date
        self.discount = discount


class TransactionRow(Row):
    def __init__(self, trans_id, cust_name, cust_contact, payment_type, date):
        """
        Holds data for the display of an entry from the transactions database table.
        :param trans_id: int
        :param cust_name: str
        :param cust_contact: str
        :param payment_type: int
        :param date: datetime.date
        :return: None
        """
        Row.__init__(self)
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


#######################################################################################################################
# GLOBAL VARIABLES
#######################################################################################################################

users_table = Table()
suppliers_table = Table()
products_table = Table()
items_table = Table()
items_sold_table = Table()
discounts_table = Table()
transactions_table = Table()

######################################################################################################################
# FUNCTION DEFINITIONS
######################################################################################################################

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


#######################################################################################################################
# TEST FUNCTION DEFINITIONS
#######################################################################################################################

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
