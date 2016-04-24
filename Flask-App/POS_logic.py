"""
Author: Ethan Morisette; Ryan Giarusso
Created: 3/1/2016
Purpose: module that holds all class definitions, function definitions, and variables for displaying information
to the WEBSITE tables (not to be confused with our db tables)
"""

#######################################################################################################################
#  IMPORTS
#######################################################################################################################
from flask import *


#######################################################################################################################
#  CLASS DEFINITIONS
#######################################################################################################################
class Row:
    """
    Parent class for specialized rows.
    """
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
        :param discount: float (percentage off)
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


class CashierRow(Row):
    def __init__(self, item_id, product_name, price):
        """
        Holds data for the display of an item in a customer's cart currently checking out.
        :param item_id: int
        :param product_name: str
        :param price: float
        :return: None
        """
        Row.__init__(self)
        self.item_id = item_id
        self.product_name = product_name
        self.price = price


class StockerRow(ItemRow):
    def __init__(self, product_id, name, inventory_cost, quantity = 1):
        """
        Holds data for the display of an item currently being added to inventory.
        :param product_id: int
        :param name: string
        :param quantity: int
        :param inventory_cost: float
        :return: None
        """
        Row.__init__(self)
        self.product_id = product_id
        self.name = name
        self.quantity = quantity
        self.inventory_cost = inventory_cost

class ReportRow(Row):
    def __init__(self, name, daily, weekly, monthly, custom=0):
        """
        Holds data for the display of accounting information.
        :param name: string; Title of row
        :param daily: float; Value of this row for the past day
        :param weekly: float; Value of this row for the past week
        :param custom: float; Value of this row for a user defined date range
        :return: None
        """
        Row.__init__(self)
        self.name = name
        self.daily = daily
        self.weekly = weekly
        self.monthly = monthly
        self.custom = custom

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

    def delete_row(self, row_number):
        """
        Deletes the row at index row_number-1
        :param row_number: int
        :return: None
        """
        if self.mostRecentRow == self.rowsList[row_number-1]:
            self.mostRecentRow = self.rowsList[row_number-2]
        self.rowsList.pop(row_number-1)
        self.rowCount -= 1


class CashierTable(Table):

    def add_row(self, item_id, product_name, price):
        """
        Adds a cashier row to the cashier table.
        :param item_id: int
        :param product_name: str
        :param price: float
        :return: None
        """
        new_row = CashierRow(item_id, product_name, price)
        self.rowsList.append(new_row)
        self.rowCount += 1
        self.mostRecentRow = new_row

    def edit_row(self, row_number, item_id, price):
        """
        Changes a current row at index row_number-1 to the parameters specified.
        If any row parameter is the empty string, it will default to its current setting.
        :param row_number: int
        :param item_id: int
        :param product_name: str
        :param price: float
        :return:
        """
        if item_id == '':
            item_id = self.rowsList[row_number-1].item_id
        if price == '':
            price = self.rowsList[row_number-1].price
        self.rowsList[row_number-1] = CashierRow(item_id, price)


class StockerTable(Table):

    def add_row(self, product_id, name, quantity, inventory_cost):
        """
        Adds a stocker row to the stocker table.
        :param product_id: int
        :param name: string
        :param inventory_cost: float
        :return: None
        """

        new_row = StockerRow(product_id, name, inventory_cost, quantity)
        self.rowsList.append(new_row)
        self.rowCount += 1
        self.mostRecentRow = new_row

    def edit_row(self, row_number, product_id, name, quantity, inventory_cost):
        """
        Changes a current row at index row_number-1 to the parameters specified.
        If any row parameter is the empty string, it will default to its current setting.
        :param row_number: int
        :param product_id: int
        :param inventory_cost: float
        :return: None
        """
        if product_id == '':
            product_id = self.rowsList[row_number-1].product_id
        if quantity == "":
            quantity = self.rowsList[row_number-1].quantity
        if inventory_cost == '':
            inventory_cost = self.rowsList[row_number-1].inventory_cost
        self.rowsList[row_number-1] = StockerRow(product_id, name, inventory_cost, quantity)

class ReportTable(Table):

    def __init__(self, revenue_list, cost_list, profit_list):
        """
        Holds data for the dashboard table in the reports window.
        Takes as input three lists, one for each accounting line,
        in the form: [daily, weekly, monthly]
        :param revenue_list:
        :param cost_list:
        :param profit_list:
        :return: None
        """
        Table.__init__(self)
        self.add_row("Revenue", revenue_list[0], revenue_list[1], revenue_list[2])
        self.add_row("Cost of Sale", cost_list[0], cost_list[1], cost_list[2])
        self.add_row("Profit", profit_list[0], profit_list[1], profit_list[2])

    def add_row(self, name, daily, weekly, monthly):
        """
        Adds a new row to the table.
        :param name: Accounting line title {Revenue, Cost of Sale, Profit}
        :param daily: float value for today
        :param weekly: float value for this week
        :param monthly: float value for this month
        :return: None
        """
        new_row = ReportRow(name, daily, weekly, monthly)
        self.rowsList.append(new_row)
        self.rowCount += 1
        self.mostRecentRow = new_row

    def update_custom_column(self, new_revenue, new_cost, new_profit):
        """
        Updates all rows in the table with appropriate values for a new custom date range.
        :param new_revenue: float
        :param new_cost: float
        :param new_profit: float
        :return: None
        """
        self.rowsList[0].custom = new_revenue
        self.rowsList[1].custom = new_cost
        self.rowsList[2].custom = new_profit




#######################################################################################################################
# GLOBAL VARIABLES
#######################################################################################################################

# Tables for cashier/stocker
cashier_table = CashierTable()
stocker_table = StockerTable()
