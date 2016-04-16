"""
Author: Ethan Morisette
Created: 4/9/2016
Last Modified:
Description: a module that holds all data specifically dealing with getting code from and to the GUI
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


def get_transaction_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: dictionary
    """
    input_dict = dict()
    input_dict["productID"] = request.form["productID"]
    input_dict["quantity"] = request.form["quantity"]
    return input_dict


def get_inventory_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a list of entries
    """
    input_dict = dict()
    input_dict["productID"] = request.form["productID"]
    input_dict["quantity"] = request.form["quantity"]
    input_dict["exp-date"] = convert_string_to_date(request.form["exp-date"])
    input_dict["item-cost"] = request.form["item-cost"]
    return input_dict


def get_discount_row(request):
    """
    Purpose: 	to get user input from the GUI and pass it into the system
    :param request: request (request object)
    :return: a list of entries
    """
    input_dict = dict()
    input_dict["productID"] = request.form["productID"]
    input_dict["saleStart"] = convert_string_to_date(request.form["saleStart"])
    input_dict["saleEnd"] = convert_string_to_date(request.form["saleEnd"])
    input_dict["salePrice"] = request.form["salePrice"]
    return input_dict
