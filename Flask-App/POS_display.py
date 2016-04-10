# Author: Ethan Morisette
# Created: 4/9/2016
# Last Modified: 
# Description: a module that holds all data specifically dealing with getting code from and to the GUI

######################################################################################
# IMPORTS																			 #
######################################################################################
from flask import *
from datetime import date

######################################################################################
# CLASS DEFINITIONS				  													 #
######################################################################################

# Purpose: to hold a date formatted as MM-DD-YYYY
class formattedDate(date):
	def __repr__(self):
		return "{}-{}-{}".format(self.month, self.day, self.year)

	def __str__(self):
		return "{}-{}-{}".format(self.month, self.day, self.year)


######################################################################################
# FUNCTION DEFINITIONS																 #
######################################################################################

# In: 		dateString (string) 
# Out: 		dateResult (formattedDate)
# Purpose: 	to convert date inputs to a date object
# Note: 	expecting this format: YYYY-MM-DD
def convertStringToDate(dateString):
	stringList 	= 	dateString.split("-")
	year 		= 	int(stringList[0])
	month		= 	int(stringList[1])
	day 		= 	int(stringList[2])
	dateResult	= 	formattedDate(year=year, month=month, day=day)
	
	return dateResult

# In: 		request (request object)
# Out: 		dictionary
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getTransactionRow(request):
	inputDict = dict()
	inputDict["productID"] 	= 	request.form["productID"]
	inputDict["quantity"] 	= 	request.form["quantity"]
	return inputDict

# In: 		request (request object)
# Out: 		a list of entries
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getInventoryRow(request):
	inputDict = dict()
	inputDict["productID"] 	= 	request.form["productID"]
	inputDict["quantity"] 	= 	request.form["quantity"]
	inputDict["exp-date"]	=	convertStringToDate(request.form["exp-date"])
	return inputDict

# In: 		request (request object)
# Out: 		a list of entries
# Purpose: 	to get user input from the GUI and pass it into the system
# Note: 
def getDiscountRow(request):
	inputDict = dict()
	inputDict["productID"] 	= 	request.form["productID"]
	inputDict["saleStart"] 	= 	convertStringToDate(request.form["saleStart"])
	inputDict["saleEnd"] 	= 	convertStringToDate(request.form["saleEnd"])
	inputDict["salePrice"] 	= 	request.form["salePrice"]
	return inputDict
