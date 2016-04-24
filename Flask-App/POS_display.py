"""
File: POS_display.py
Author: Ethan Morisette
Created: 3/9/2016
Purpose: a module that holds all data specifically dealing with getting code from and to the GUI
"""

######################################################################################
# IMPORTS																			 #
######################################################################################
from flask import *
from datetime import date


######################################################################################
# CLASS DEFINITIONS				  													 #
######################################################################################


class FormattedDate(date):
    """
    Purpose: to hold a date formatted as MM-DD-YYYY
    """
    def __repr__(self):
        return "{}-{}-{}".format(self.month, self.day, self.year)

    def __str__(self):
        return "{}-{}-{}".format(self.month, self.day, self.year)


######################################################################################
# FUNCTION DEFINITIONS																 #
######################################################################################


def convert_string_to_date(dateString):
    """
    Purpose: 	to convert date inputs to a date object
    :param dateString: String coming from HTML user-input in format YYYY-MM-DD
    :return: Instance of FormattedDate
    """
    string_list = dateString.split("-")
    year = int(string_list[0])
    month = int(string_list[1])
    day = int(string_list[2])
    date_result = FormattedDate(year=year, month=month, day=day)

    return date_result


def get_cashier_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: dictionary
    """
    input_dict = dict()
    input_dict["row_number"] = request.form["row_number"]
    input_dict["item_id"] = request.form["item_id"]
    input_dict["price_per_unit"] = request.form["price_per_unit"]
    return input_dict


def get_stocker_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["row_number"] = request.form["row_number"]
    input_dict["product_id"] = request.form["product_id"]
    input_dict["quantity"]   = request.form["quantity"]
    input_dict["inventory_cost"] = request.form["inventory_cost"]
    return input_dict


def get_discount_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["discount-id"] = request.form["DatabaseID"]
    input_dict["product-id"] = request.form["product-id"]
    #TODO convert both start date and end date to formatted date
    input_dict["start-date"] = convert_string_to_date(request.form["start-date"])
    input_dict["end-date"] = convert_string_to_date(request.form["end-date"])
    input_dict["percent-off"] = request.form["percent-off"]
    return input_dict

def get_user_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["user-id"] = request.form["DatabaseID"]
    input_dict["username"] = request.form["username"]
    input_dict["password"] = request.form["password"]
    input_dict["permissions"] = request.form["permissions"]
    return input_dict

def get_item_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["item-id"] = request.form["DatabaseID"]
    input_dict["product-id"] = request.form["product-id"]
    input_dict["inventory-cost"] = request.form["inventory-cost"]
    return input_dict

def get_itemsold_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["itemsold_id"] = request.form["DatabaseID"]
    input_dict["item-id"] = request.form["item-id"]
    input_dict["price-sold"] = request.form["price-sold"]
    input_dict["transaction-id"] = request.form["transaction-id"]
    return input_dict

def get_product_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["product-id"] = request.form["DatabaseID"]
    input_dict["product-name"] = request.form["product-name"]
    input_dict["supplier-id"] = request.form["supplier-id"]
    input_dict["inventory-count"] = request.form["inventory-count"]
    input_dict["min-inventory"] = request.form["min-inventory"]
    input_dict["shelf-life"] = request.form["shelf-life"]
    input_dict["standard-price"] = request.form["standard-price"]
    return input_dict

def get_supplier_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["supplier-id"] = request.form["DatabaseID"]
    input_dict["supplier-name"] = request.form["supplier-name"]
    input_dict["supplier-email"] = request.form["supplier-email"]
    return input_dict

def get_transaction_row(request):
    """
    Purpose:    to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a dictionary of form data
    """
    input_dict = dict()
    input_dict["transaction-id"] = request.form["DatabaseID"]
    input_dict["customer-name"] = request.form["customer-name"]
    input_dict["customer-contact"] = request.form["customer-contact"]
    input_dict["payment-type"] = request.form["payment-type"]
    return input_dict