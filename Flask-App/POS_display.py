# Author: Ethan Morisette
# Created: 4/9/2016
# Last Modified: 
# Description: a module that holds all data specifically dealing with getting code from and to the GUI

######################################################################################
# IMPORTS																			 #
######################################################################################
from flask import *

######################################################################################
# FUNCTION DEFINITIONS																 #
######################################################################################

# In: 		request (request object)
# Out: 		dictionary
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getReceiptRow(request):
	inputDict = dict()
	inputDict["productID"] 	= request.form["productID"]
	inputDict["quantity"] 	= request.form["quantity"]
	return inputDict

# In: 		request (request object)
# Out: 		a list of entries
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getStockerRow(request):
	inputDict = dict()
	inputDict["productID"] 	= request.form["productID"]
	inputDict["quantity"] 	= request.form["quantity"]
	return inputDict

# In: 		request (request object)
# Out: 		a list of entries
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getSaleRow(request):
	inputDict = dict()
	inputDict["productID"] 	= request.form["productID"]
	inputDict["saleStart"] 	= request.form["saleStart"]
	inputDict["saleEnd"] 	= request.form["saleEnd"]
	inputDict["salePrice"] 	= request.form["salePrice"]
	return inputDict
