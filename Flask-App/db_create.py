from app import db
from models import *
from datetime import *

# Create the database and the db tables #
db.create_all()

#######################################################################################################################
#  INSERT ITEMS INTO TABLES!																																									#
#######################################################################################################################

# SUPPLIERS				name		email
db.session.add(Supplier("Ethan", 	"myEmail@email.com"))


# USERS				username	password	permissions
db.session.add(User("admin", 	"admin", 	1))
db.session.add(User("cashier",  "admin",    2))
db.session.add(User("stocker",  "admin",    3))

# PRODUCTS				name			type			s_id	qty.	shelf	std. price
db.session.add(Product("poop", 			"human waste", 	1, 		10, 	1, 		10.40))
db.session.add(Product("apples",		"fruit", 		1, 		3,	 	32, 	0.40))
db.session.add(Product("carrots",		"vegetable", 	1, 		34, 	43, 	1.45))
db.session.add(Product("matches",		"tool", 		1, 		84, 	1, 		0.34))
db.session.add(Product("shoes",			"clothing", 	1, 		120, 	4, 		20.00))
db.session.add(Product("hat",			"clothing", 	1, 		305, 	123, 	10.21))
db.session.add(Product("shirt",			"clothing", 	1, 		991, 	10, 	2.99))
db.session.add(Product("pants",			"clothing", 	1, 		403, 	5, 		10.50))
db.session.add(Product("baseball bat",	"toy", 			1, 		12, 	100, 	3.56))

# ITEMS				p_id	exp. date			cost	a_id
db.session.add(Item(1, 		date(2016, 5, 4), 	0.50, 	1))
db.session.add(Item(2, 		date(2011, 9, 5), 	0.35, 	1))
db.session.add(Item(3, 		date(2020, 10, 4), 	2.00, 	1))
db.session.add(Item(1, 		date(2017, 5, 9), 	1.98, 	1))
db.session.add(Item(4, 		date(2009, 1, 1), 	60.00, 	1))
db.session.add(Item(2, 		date(2001, 5, 4), 	4.09, 	1))
db.session.add(Item(9, 		date(2019, 4, 6), 	5.04, 	1))

# Commit changes #
db.session.commit()