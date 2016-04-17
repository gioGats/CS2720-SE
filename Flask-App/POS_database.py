# Author: Ethan Morisette; Braden Menke
# Created: 04/09/2016
# Last Modified: 3/20/2016
# Purpose: to hold all of our database interactions in a single module 

########################################################################################################################
# IMPORTS																											   #
########################################################################################################################

# from flask_sqlalchemy import SQLAlchemy
from models import *
from datetime import datetime


########################################################################################################################
# WRAPPER FUNCTION      																					           #
########################################################################################################################
def getfromDB_Error(func):
    """
    Does error-checking on get functions
        ErrorCodes: -1 : failed and rolled back
    """

    def wrapperFunction(db, *args, **kwargs):
        try:
            func(db, *args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            return -1  # !!

    # Hand back the function for future usage.
    return wrapperFunction


# Defined: Products      (FULL)
#         Transaction   (FULL)
#         Items/Sold    (FULL)
#         Supplier      (FULL)
#         Discounts     (FULL)
#
#
# Product access: getProduct{}(db, productID)
#                   Viable {}'s: Name, Price, Type, ShelfLife, MinInventory, InventoryCount, SupplierID
# Products also have: destroyProduct(db, id),
#                     addProduct(db, supplier_id, inventory_count, min_inventory, shelf_life, standard_price) (creative)
#
# Transaction Access: add,
#                     get(tuple, consisting of customer_name, customer_contact, payment_type, date-of-transaction),
#                     destroy
#
# Supplier Access: get(tuple of name, email),
#                  getID,
#                  add,
#                  destroy
#
# Others follow a similar vein


########################################################################################################################
# FUNCTION DEFINITIONS																								   #
########################################################################################################################


#########################################################################
# Product database Access                                               #
#########################################################################
@getfromDB_Error
def getProductName(db, productID):
    """
    Gives the product's name
    :param db: database pointer
    :param productID: int
    :return: str (name)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.name).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    name = result.name
    return name


@getfromDB_Error
def getProductPrice(db, productID):
    """
    gets the price for a given ID
    :param db: database pointer
    :param productID: int
    :return: float (discounted price)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.standard_price).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    price = result.standard_price
    # get the product from the discounts db
    discount = getDiscountFor(db, productID)
    # Get the total price!
    newPrice = price * (1 - discount)
    return newPrice  # PRICE (FLOAT)


@getfromDB_Error
def getProductShelfLife(db, productID):
    """
    get the shelf life for a given product (in days)
    :param db: database pointer
    :param productID: int
    :return: int (days)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.shelf_life).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    shelfLife = result.shelf_life
    return shelfLife  # product's shelf life (INT)


@getfromDB_Error
def getProductMinInventory(db, productID):
    """
    Gives back the minimum inventory for a given product
    :param db: database pointer
    :param productID: int
    :return: int
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.min_inventory).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    mInventory = result.min_inventory
    return mInventory  # product's min inventory (INT)


@getfromDB_Error
def getProductInventoryCount(db, productID):
    """
    Get the actual current inventory cost
    :param db: database pointer
    :param productID: int
    :return: int (current inventory)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.inventory_count).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    currInventory = result.inventory_count
    return currInventory  # product's current inventory count


@getfromDB_Error
def getProductSupplierID(db, productID):
    """
    get the supplier from a product
    :param db: database pointer
    :param productID: int
    :return: int (supplier ID)
    """
    # make the query and receive a single tuple (first() allows us to do this)
    result = db.session.query(Product.supplier_id).filter(Product.id == productID).first()
    # grab the name in the keyed tuple received
    supplierID = result.supplier_id
    return supplierID  # product's supplier's ID


@getfromDB_Error
def destroyProduct(db, productID):
    """
    Destroys a productID from the database
    :param db: database pointer
    :param productID: int
    :return: -
    """
    # Kill it!
    db.session.query(Product).filter(Product.id == productID).delete()
    # Commit
    db.session.commit()


@getfromDB_Error
def addProduct(db, supplier_id, inventory_count, min_inventory, shelf_life, standard_price):
    """
    Builds and creates a product given all the info about it.
    :param db: database pointer
    :param supplier_id: int
    :param inventory_count: int
    :param min_inventory: int
    :param shelf_life: integer
    :param standard_price: float
    :return: -
    """
    # Build one
    db.session.add(Product(supplier_id, inventory_count, min_inventory, shelf_life, standard_price))
    # commit our addition!
    db.session.commit()


#########################################################################
# Items/ItemSold database Access                                        #
#########################################################################
# Notes:	this is intended to take all of the rows we add locally and commit them together to the DB; 
#			"Update Stock" and "Finish Transaction" buttons will use this procedure
@getfromDB_Error
def updateItemTable(db, rowsList):
    """
    Update the table given a list of rows
    :param db: database pointer
    :param rowsList: list of rows
    :return: -
    """
    for row in rowsList:
        db.session.add(Item(row.productID, row.itemCost))
    db.session.commit()


@getfromDB_Error
def popItemToItemSold(db, itemID, priceSoldAt, transactionID):
    """
    Given an item, price, and a transactionID, moves an item from Items to ItemSold
    :param db: database pointer
    :param itemID: int
    :param priceSoldAt: float
    :param transactionID: int
    :return: -
    """
    # Add the new thing into the ItemSold portion
    db.session.add(ItemSold(itemID, priceSoldAt, transactionID))
    # Get and destroy the old Item out of the database
    db.session.query(Item).filter(Item.id == itemID).delete()


@getfromDB_Error
def getItemProduct(db, itemID):
    """
    Get an item's linked product id
    :param db: database pointer
    :param itemID: int
    :return: int
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.product_id


@getfromDB_Error
def getItemCost(db, itemID):
    """
    Get an item's cost
    :param db: database pointer
    :param itemID: int
    :return: float (cost)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.inventory_cost


@getfromDB_Error
def getItemExpirationDate(db, itemID):
    """
    Get an item's expiration date
    :param db: database pointer
    :param itemID: int
    :return: datetime object (of expiration)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.expiration_date


@getfromDB_Error
def getItemAuthor(db, itemID):
    """
    Get the author of an item (?)
    :param db: database pointer
    :param itemID: int
    :return: int (the author's id)
    """
    # get the one we want
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # Filter the thing;
    return item.author_id


@getfromDB_Error
def getItemData(db, itemID):
    """
    Function to get all the data from the db about an item.
    :param db: database pointer
    :param itemID: int
    :return: Tuple, containing: product_id, inventory_cost, expiration_date, author_id
    """
    # Get ALL THE DATA
    item = db.session.query(Item).filter(Item.id == itemID).first()
    # construct a tuple
    itemTup = tuple([item.product_id,
                     item.inventory_cost,
                     item.expiration_date,
                     item.author_id])
    return itemTup


#########################################################################
# Supplier database Access                                              #
#########################################################################
@getfromDB_Error
def getSupplier(db, supplierID):
    """
    Get the supplier's information
    :param db: database pointer
    :param supplierID: int
    :return: tuple containing name, email
    """
    # Grab the whole Supplier
    result = db.session.query(Supplier).filter(Supplier.id == supplierID).first()
    # filter the ID since we already have that.
    retTuple = tuple([result.name, result.email])
    return retTuple


@getfromDB_Error
def getSupplierID(db, supplierString):
    """
    Get the supplier's ID based on their name
    :param db: database pointer
    :param supplierString: string, composed of supplier's name
    :return: int : supplier's ID
    """
    # Get the supplier
    result = db.session.query(Supplier).filter(Supplier.name == supplierString).first()
    # just hand back the ID
    return result.id


@getfromDB_Error
def addSupplier(db, supplierName, supplierEmail):
    """
    add a supplier to the database.
    :param db: database pointer
    :param supplierName: str
    :param supplierEmail: str
    :return: int (supplier's generated ID)
    """
    # Add and construct the supplier
    db.session.add(Supplier(supplierName, supplierEmail))
    # Extract the ID from the database (since it gens on-the-spot)
    retID = getSupplierID(db, supplierName)
    # Return
    return retID


@getfromDB_Error
def destroySupplier(db, supplierID):
    """
    Destroys a supplier from the db
    :param db: database pointer
    :param supplierID: int
    :return: -
    """
    # Kill it!
    db.session.query(Supplier).filter(Supplier.id == supplierID).delete()
    # Commit our changes
    db.session.commit()


#########################################################################
# Discount database Access                                              #
#########################################################################
@getfromDB_Error
def getDiscountFor(db, productID):
    """
    Get any discounts for the product ID
    :param db: database pointer
    :param productID: int
    :return: float (between 0.0-1.0; a percentage)
    """
    # Get the discount tuple if it satisfies conditionals
    currentDiscount = db.session.query(Discount).filter(Discount.product_id == productID,  # Is the right product
                                                        # Verify the discount has started
                                                        Discount.start_date <= datetime.date(datetime.today()),
                                                        # Verify the discount has NOT ended
                                                        Discount.end_date > datetime.date(datetime.today())
                                                        ).first()  # Pick the first one.
    # Filter the price out; or 0 for no matches
    if currentDiscount is None:
        return 0
    else:
        return currentDiscount.discount


@getfromDB_Error
def addDiscount(db, productID, discPercent, startDate, endDate):
    """
    Add a discount to the table
    :param db: database pointer
    :param productID: int
    :param discPercent: float (0.0-1.0, a percentage)
    :param startDate: datetime object
    :param endDate: datetime object
    :return: -
    """
    # Create the discount portion
    db.session.add(Discount(productID, startDate, endDate, discPercent))
    # Save it to the database
    db.session.commit()


@getfromDB_Error
def destroyDiscount(db, discountID):
    """
    Destroy a discount out of the db
    :param db: database pointer
    :param discountID: int
    :return: -
    """
    # Kill it!
    db.session.query(Discount).filter(Discount.id == discountID).delete()
    # Commit our changes
    db.session.commit()


#########################################################################
# Transaction database Access                                           #
#########################################################################
@getfromDB_Error
def getTransaction(db, transactionID):
    """
    Get all the stuff about a transaction given the ID
    :param db: database pointer
    :param transactionID: int
    :return: tuple, consisting of customer_name, customer_contact, payment_type, date-of-transaction
    """
    # Get the transaction
    transaction = db.session.query(Transaction).filter(Transaction.id == transactionID).first()
    # Structure it into a tuple
    retT = tuple([transaction.cust_name, transaction.cust_contact,
                  transaction.payment_type, transaction.date])
    # Return that.
    return retT


@getfromDB_Error
def destroyTransaction(db, transactionID):
    """
    Destroy a transaction given the ID
    :param db: database pointer
    :param transactionID: int
    :return: -
    """
    # Kill it!
    db.session.query(Transaction).filter(Transaction.id == transactionID).delete()
    # Commit this obliteration
    db.session.commit()


@getfromDB_Error
def addTransaction(db, cust_name, cust_contact, payment_type):
    """
    Add a transaction
    :param db: database pointer
    :param cust_name: str
    :param cust_contact: str
    :param payment_type: int
    :return: -
    """
    # Create the transaction
    db.session.add(Transaction(cust_name, cust_contact, payment_type))
    # Commit that
    db.session.commit()
