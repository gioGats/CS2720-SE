"""
File : POS_helpers.py
Author: Ethan Morisette
Created : 3/15/2016 (Last Modified: 4/18/2016)
Purpose : This is the file with helper functions for the POS Application.
"""
#############################
# Import Statements
#############################
from app import *
# -------------------------------------------------- #

#############################
# Helper Statements
#############################


# Functions to help manage user login and permissions #
def is_manager(current_user):
    return current_user.permissions == 1


def is_cashier(current_user):
    return current_user.permissions == 2


def is_stocker(current_user):
    return current_user.permissions == 3


def redirect_after_login(current_user):
    if is_manager(current_user):
        return redirect('/reports')
    elif is_cashier(current_user):
        return redirect('/cashier')
    elif is_stocker(current_user):
        return redirect('/stocker')
    else:
        return redirect('/')
# -------------------------------------------------- #

