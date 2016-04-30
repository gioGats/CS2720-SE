"""
File: app.py
Author: Jacob Campbell; Ethan Morisette; Ryan Giarusso; Braden Menke
Created: 3/11/2016 (Last Modified: 4/29/2016)
Purpose: This is the master file for the Flask application, contains logic for generating webpages, routing
data, and managing the flow of the entire system.
"""

###############################################################################################################################################
# IMPORT STATEMENTS ###########################################################################################################################
###############################################################################################################################################
from flask import *
from POS_helpers import *
from templates.form import LoginForm, RegisterForm
from helper import *
from helper import login_user, login_required, logout_user
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy.engine import Engine
# from sqlalchemy import event
from datetime import *
import POS_display
import POS_logic
from werkzeug.exceptions import HTTPException, NotFound, BadRequest

################################################################################################################################################
# APPLICATION CONFIGURATION ####################################################################################################################
################################################################################################################################################


# Grabs the domain name the app is running on #
app = Flask(__name__)

# Sets bcrypt for unique password hashing #
bcrypt = Bcrypt(app)

# Configure our application secret key [DO NOT CHANGE!!!]#
app.secret_key = '\xb7{\xbb\x9b\x9b\x11\xa7\\Ib\xcf\xe4\x00\x99Yi\xafg\xd2\x96\x82\x18\x18\x9d'

# Configure our database settings #

# Production Database Settings #

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#    username="SailingSales",
#    password="sailin123$",
#    hostname="SailingSales.mysql.pythonanywhere-services.com",
#    databasename="SailingSales$master",
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

# For a local database, using SQLite, the settings would look like this, instead of what is above. so comment that out #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
# Where items.db is the created database locally #

# Setup a global instance of the database #
# use: 'from app import db' #
db = SQLAlchemy(app)

# Import all the database models from our 'models.py' file
# NOTE: We import down here because we have to set up the database
# (right above this) BEFORE we can import our models
# (thus it cannot go on the top of the page) #
from models import *
import POS_database

# Setup Flask Login Manager #
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Points to our "login" function "


# The magic that makes foreign keys activated in sqlite
@login_manager.user_loader
def load_user(user_id):
    global current_user
    current_user = User.query.filter(User.id == int(user_id)).first()
    return User.query.filter(User.id == int(user_id)).first()

###############################################################################################################################################
# GLOBAL VARIABLES ############################################################################################################################
###############################################################################################################################################
current_user = None     # stores information on the current user logged in 

# each page has its own channel for errors to prevent trailing errors
productError = None
itemError = None
itemSoldError = None
supplierError = None
userError = None
discountError = None
transactionError = None
reportError = None
stockerError = None
cashierError = None
loginError = None

###############################################################################################################################################
# ROUTE DECLARATIONS ##########################################################################################################################
###############################################################################################################################################

###############################################################################################################################################
# DATABASE PAGE ROUTES ########################################################################################################################
###############################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------------------#
# home/login page functions                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    none                                                                                                                       #
# > login:         not required                                                                                                               #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def login():
    global loginError
    form = LoginForm(request.form)
    global current_user  # allows changing of the globally defined current_user #

    if request.method == 'POST':  # If the login button was clicked #
        if form.validate_on_submit():

            user = User.query.filter_by(name=request.form['username']).first()

            if user is None:
                loginError = "Invalid username. Please try again"
                render_template('login.html', form=form, error=loginError)
            else:
                if bcrypt.check_password_hash(user.password, request.form['password']):
                    login_user(user)
                    current_user = user
                    flash('You have been successfully logged in.')

                    return redirect_after_login(current_user)  # from POS_helpers #
                else:
                    error = "Username found, but invalid password. Please try again."
                    render_template('login.html', form=form, error=loginError)
        else:
            render_template('login.html', form=form, error=loginError)

    # If the form was not a submit, we just need to grab the page data (GET request) #
    return render_template('login.html', form=form, error=loginError)

@app.route('/logout')
def logout():
    global current_user
    if current_user is None:
        flash("You are already signed out.")
        return redirect(url_for('login'))
    logout_user()
    current_user = None
    flash('You have been successfully logged out.')
    return redirect(url_for('login'))




#---------------------------------------------------------------------------------------------------------------------------------------------#
# reports page functions                                                                                                                      #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager                                                                                                                    #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/reports', methods=["GET", "POST"])
@login_required
def reports():
    global reportError
    startDate = date(1990, 5, 27)
    endDate = datetime.date.today() + datetime.timedelta(days=1) 
    endDate = date(1990, 6, 27)
    # get the dates for the custom rows
    # whenever the page is first loaded it will try to get the custom dates, so we raise an exception in this case
    try:
        inputDict = POS_display.get_report_custom_row(request)
        startDate = POS_display.convert_string_to_date(inputDict["custom_start_date"])
        endDate = POS_display.convert_string_to_date(inputDict["custom_end_date"])
        print(inputDict["custom_start_date"])
        print(inputDict["custom_end_date"])
    except BadRequest as e:
        print("Could not grab the custom row information.")

    # get the report table information
    reportTableDict     = getReportTableInfo(db, startDate, endDate)
    customList          = reportTableDict["custom"] 
    # print(customList)

    # add the information to the report table
    POS_logic.report_table.make_table(reportTableDict["revenues"], reportTableDict["costs"], reportTableDict["profits"])
    POS_logic.report_table.update_custom_column(customList[0], customList[1], customList[2])

    # display the page
    if is_manager(current_user):
        return render_template("reports.html", reportTable=POS_logic.report_table, error=reportError)
    else:
        return redirect('/')

@app.route('/download', methods=["POST"])
def downloadReport():
    dropDownItem = request.form["report-dropdown"]
    if request.form["report-start-date"]:
        startDate = POS_display.convert_string_to_date(request.form["report-start-date"])
    else:
        startDate = datetime.date(1990, 5, 27)  # Before the creation of the system.
    if request.form["report-end-date"]:
        endDate = POS_display.convert_string_to_date(request.form["report-end-date"])
    else:
        endDate = datetime.date.today()+datetime.timedelta(days=1)  # Last possible date

    # if the report type is inventory worth report, do special download
    if dropDownItem == 'inventory_worth_report':
        r = POS_database.reportInfoCSV(db)  # Dating doesn't make sense in this context.
    # if the report type is revenue audit report, do special download
    elif dropDownItem == "revenue_audit_report":
        r = POS_database.reportRevenueAudit(db, (startDate, endDate,))
    # if the report type is purchase order report, do special download
    elif dropDownItem == 'purchase_order_report':
        r = POS_database.runOutReport(db)
    # otherwise do a database table report download
    else:
        r = POS_database.toCSV(db, dropDownItem, (startDate, endDate,))

    return r

    #return redirect(url_for("reports"))

@app.route('/updatecustom', methods=["POST"])
def updateCustomRange():
    inputDict = POS_display.get_report_custom_row(request)
    print(inputDict["custom_start_date"])
    print(inputDict["custom_end_date"])
    startDate = date(2016, 4, 27)
    endDate = date(2016, 4, 28)
    startDate = POS_display.convert_string_to_date(inputDict["custom_start_date"])
    endDate = POS_display.convert_string_to_date(inputDict["custom_end_date"])
    print(startDate)
    print(endDate)
    customRep = POS_database.revenueCheck(db, (startDate, endDate))
    print(customRep)

    POS_logic.report_table.update_custom_column(customRep[0], customRep[1], customRep[2])

    return redirect(url_for("reports"))

def getReportTableInfo(db, startDate, endDate):
    """
    gets report information for the table displayed in the reports tab
    :param db: database pointer
    :return: dictionary of arrays
    """
    reportTableDict = dict()



    # get info from the databases
    dailyRep = POS_database.revenueCheck(db, "day")
    weeklyRep = POS_database.revenueCheck(db, "week")
    monthlyRep = POS_database.revenueCheck(db, "month")
    customRep = POS_database.revenueCheck(db, (startDate, endDate))
    # print(customRep)

    # store info in arrays representing rows
    revenues = [dailyRep[0], weeklyRep[0], monthlyRep[0]]
    costs = [dailyRep[1], weeklyRep[1], monthlyRep[1]]
    profits = [dailyRep[2], weeklyRep[2], monthlyRep[2]]

    # add rows to dictionary
    reportTableDict["revenues"] = revenues
    reportTableDict["costs"] = costs
    reportTableDict["profits"] = profits
    reportTableDict["custom"] = customRep    # order: revenues, costs, profits

    return reportTableDict


#---------------------------------------------------------------------------------------------------------------------------------------------#
# cashier page functions                                                                                                                      #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager, cashier                                                                                                           #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/cashier')
@login_required
def cashier():
    global cashierError
    if is_manager(current_user) or is_cashier(current_user):
        return render_template("cashier.html", cashierTable=POS_logic.cashier_table, error=cashierError)
    else:
        return redirect('/')

@app.route('/cashieradd', methods=["POST"])
def cashierAddRow():
    global cashierError
    cashierError = None
    # get the information from the user
    inputDict = POS_display.get_cashier_row(request)
    

    if (not inputDict["row_number"] and not inputDict["item_id"] and not inputDict["price_per_unit"]):
        cashierError = "You didn't enter anything!"
    elif (inputDict["row_number"]):
        POS_logic.cashier_table.edit_row(inputDict["row_number"], inputDict["item_id"], inputDict["price_per_unit"])
    else:
        # get the product name and price from the database
        productID = POS_database.getItemProduct(db, inputDict["item_id"])
        # print("Item ID:", inputDict["item_id"])

        # if there was no result returned that means there was no item in the database with that id
        # so return with an productError
        if (productID == POS_database.NO_RESULT):
            cashierError = "That item is not in the database."
        
        # if there is a result but the id is already in the table, return an productError
        elif (POS_logic.cashier_table.check_id_exists(int(inputDict["item_id"]))):
            cashierError = "That item is already in your table!"
        # otherwise, add the item
        else:
            productName = POS_database.getProductName(db, productID)

            # if the user enters a price per unit, than use that one
            if (inputDict["price_per_unit"]):
                pricePerUnit = float(inputDict["price_per_unit"])
            # otherwise use the one in the database
            else:
                pricePerUnit = POS_database.getProductPrice(db, productID)
            # add the received information to the local receipt table
            POS_logic.cashier_table.add_row(inputDict["item_id"], productName, pricePerUnit)

    # reload page
    return redirect(url_for('cashier'))

@app.route('/cashierdelete', methods=["POST"])
def cashierDeleteRow():
    global cashierError
    cashierError = None
    inputDict = POS_display.get_cashier_row(request)

    # if no row id was entered then print an cashierError
    if (not inputDict["row_number"]):
        cashierError = "What are you trying to delete?"

    # if the row number does not exist, display an cashierError
    elif (int(inputDict["row_number"]) > POS_logic.cashier_table.get_row_count()):
        cashierError = "That row number is out of bounds."

    # otherwise, delete the row number
    else:
        POS_logic.cashier_table.delete_row(int(inputDict["row_number"]))
    
    # always reload the page
    return redirect(url_for('cashier'))

@app.route('/customerinfo', methods=["POST"])
def enterCustomerInfo():
    global cashierError
    cashierError = None

    # if the cart is empty print an cashierError and reload the cashier page
    print(POS_logic.cashier_table.isEmpty())
    if (POS_logic.cashier_table.isEmpty()):
        cashierError = "You don't have any items in your cart!"
        return redirect(url_for("cashier"))

    # otherwise go to the customerinfo page
    return render_template("customerinfo.html")

@app.route('/cashiercommit', methods=["POST"])
def finishTransaction():
    customer_name = request.form["customer-name"]
    customer_contact = request.form["customer-contact"]
    payment_type = int(request.form["payment-type"])

    # TODO send all information from the local receipt table to the database for storage
    POS_database.updateCashierTable(db, POS_logic.cashier_table.rowsList, customer_name, customer_contact, payment_type)
    # clear the local receipt table out
    POS_logic.cashier_table.clear_table()
    return redirect(url_for('cashier'))

@app.route('/cashiercancel', methods=["POST"])
def cashierCancel():
    global cashierError
    cashierError = None
    POS_logic.cashier_table.clear_table()
    return redirect(url_for('cashier'))


#---------------------------------------------------------------------------------------------------------------------------------------------#
# stocker page functions                                                                                                                      #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager, stocker                                                                                                           #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/stocker')
@login_required
def stocker():
    global stockerError
    if is_manager(current_user) or is_stocker(current_user):
        return render_template("stocker.html", stockerTable=POS_logic.stocker_table, error=stockerError)
    else:
        return redirect('/')

@app.route('/stockeradd', methods=["POST"])
def stockerAddRow():
    global stockerError
    stockerError = None
    # get the information from the user
    inputDict = POS_display.get_stocker_row(request)
    


    if (not inputDict["row_number"] and not inputDict["product_id"] and not inputDict["quantity"] and not inputDict["inventory_cost"]):
        stockerError = "You didn't enter anything!"
    # if the user enters a number they want to edit!
    elif (inputDict["row_number"]):
        productName = POS_database.getProductName(db, inputDict["product_id"])
    
        # if there is no result for productName, then that means the product ID is not in the database
        if (productName == POS_database.NO_RESULT):
            stockerError = "That product is not in the database"
        POS_logic.stocker_table.edit_row(int(inputDict["row_number"]), inputDict["product_id"], productName, inputDict["quantity"], inputDict["inventory_cost"])
    # otherwise, they want to add something!
    else:
        # if the user did not enter and inventory cost, give it a default value
        if (not inputDict["inventory_cost"]):
            inventory_cost = 0.00
        # otherwise use the one they entered
        else:
            inventory_cost = inputDict["inventory_cost"]

        # if the user did not enter a quantity, give it a default value
        if (not inputDict["quantity"]):
            quantity = 0
        # otherwise use the one they entered
        else:
            quantity = inputDict["quantity"]
        # get the product name from the database
        productName = POS_database.getProductName(db, inputDict["product_id"])
    
        # if there is no result for productName, then that means the product ID is not in the database
        if (productName == POS_database.NO_RESULT):
            stockerError = "That product is not in the database"
        else:    
            # add all of the information received to the local stocking table
            POS_logic.stocker_table.add_row(inputDict["product_id"], productName, int(quantity), float(inventory_cost))
    
    return redirect(url_for('stocker'))

    # productID = inputDict['product_id']

    # if (productID == ''):
    #     productID = POS_logic.stocker_table.rowsList[int(inputDict["row_number"])-1].product_id


    # # get the product name from the database
    # productName = POS_database.getProductName(db, productID)

    # # if there is no result for productName, then that means the product ID is not in the database
    # if (productName == POS_database.NO_RESULT):
    #     stockerError = "That product is not in the database"

    # # otherwise edit/add the row
    # else:
    #     if (inputDict["row_number"]):
    #         POS_logic.stocker_table.edit_row(int(inputDict["row_number"]), productID, productName, inputDict["quantity"], float(inputDict["inventory_cost"]))
    #     else:
    #         # add all of the information received to the local stocking table
    #         POS_logic.stocker_table.add_row(productID, productName, int(inputDict['quantity']), float(inputDict['inventory_cost']))
    
    # return redirect(url_for('stocker'))

@app.route('/stockerdelete', methods=["POST"])
def stockerDeleteRow():
    global stockerError
    stockerError = None
    inputDict = POS_display.get_stocker_row(request)

    # if no row id was entered then print an erro
    if (not inputDict["row_number"]):
        stockerError = "What are you trying to delete?"

    # if the enter row number is out of bounds, print stockerError
    elif (int(inputDict["row_number"]) > POS_logic.stocker_table.get_row_count()):
        stockerError = "That row number is out of bounds!"

    # otherwise go ahead and delete the row
    else:
        POS_logic.stocker_table.delete_row(int(inputDict["row_number"]))

    # always reload the stocker page
    return redirect(url_for('stocker'))

@app.route('/stockercommit', methods=["POST"])
def updateInventory():
    global stockerError
    stockerError = None

    # if there aren't any items in the inventory, print stockerError
    if (POS_logic.stocker_table.isEmpty()):
        stockerError = "You don't have any items in your cart!"

    # otherwise update the database table
    else:
        # send all information from the local stocking table to the database for storage
        POS_database.updateItemTable(db, POS_logic.stocker_table.rowsList)
        # clear the local stocking table out
        POS_logic.stocker_table.clear_table()

    # always go back to the stocker page 
    return redirect(url_for('stocker'))

@app.route('/stockercancel', methods=["POST"])
def stockerCancel():
    global stockerError
    stockerError = None
    POS_logic.stocker_table.clear_table()
    return redirect(url_for('stocker'))

#####################################################################################################################################################################################
# DATABASE PAGE ROUTES ##############################################################################################################################################################
#####################################################################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------------------#
# items page functions                                                                                                                        #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager, cashier                                                                                                           #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/itemsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/itemsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def itemsDB(page):
    global itemError

    if is_manager(current_user) or is_stocker(current_user):
        pagination = Item.query.paginate(page, 16)
        return render_template("itemsDB.html", pagination=pagination, error=itemError)
    else:
        return redirect(url_for('login'))

@app.route('/itemdb-delete', methods=["POST"])
@login_required
def itemDBDeleteItem():
    global itemError
    itemError = None
    
    inputDict = POS_display.get_item_row(request)

    # if the user didn't enter an item id to delete print itemError
    if (not inputDict["item-id"]):
        itemError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print itemError
    elif (int(inputDict["item-id"]) > POS_database.getMaxItemID(db)):
        itemError = "You entered an item ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("item")


    return redirect(url_for('itemsDB'))

@app.route('/itemdb-add', methods=["POST"])
def itemDBUpdateItem():
    global itemError
    itemError = None

    # get the user input from the form submit
    inputDict = POS_display.get_item_row(request)

    #  if the user did enter an id number, check if its valid and modify item if it is
    if inputDict["item-id"]:
        result = POS_database.editItem(db, inputDict["item-id"], inputDict["product-id"], inputDict["inventory-cost"])

        if (result == POS_database.NO_RESULT):
            itemError = "That item is not in the database."

    # else if the user did not enter an id, add a new item
    else:
        result = POS_database.addItem(db, inputDict["product-id"], inputDict["inventory-cost"])

        if (result == POS_database.NO_RESULT):
            itemError = "That product is not in the database."

        pagination = Item.query.paginate(1, 16)
        page = pagination.pages
        return redirect(url_for('itemsDB', page=page))
    # reload the page
    return redirect(url_for('itemsDB'))


@app.route('/itemdbcancel', methods=["POST"])
def itemDBCancel():
    global itemError
    itemError = None
    return redirect(url_for('itemsDB'))




#---------------------------------------------------------------------------------------------------------------------------------------------#
# products page functions                                                                                                                     #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager , stocker                                                                                                          #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/productsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/productsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def productsDB(page):
    global productError

    if is_manager(current_user) or is_stocker(current_user):
        pagination = Product.query.paginate(page, 16)
        return render_template("productsDB.html", pagination=pagination, error=productError)
    else:
        return redirect(url_for('login'))

@app.route('/productdb-delete', methods=["POST"])
@login_required
def productDBDeleteProduct():
    global productError

    # initialize the function to have no productErrors
    productError = None
    
    inputDict = POS_display.get_product_row(request)


    # if the user didn't enter an item id to delete print productError
    if (not inputDict["product-id"]):
        productError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print productError
    elif (int(inputDict["product-id"]) > POS_database.getMaxProductID(db)):
        productError = "You entered a product ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("product")

    # always reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdb-add', methods=["POST"])
def productDBUpdateProduct():
    global productError

    # clear out the productError status
    productError = None
    # get the user input from the form submit
    inputDict = POS_display.get_product_row(request)

    # if the dictiionary doensn't have any items in it print productError
    if ((not inputDict["product-id"]) and (not inputDict["product-name"]) and (not inputDict["supplier-id"]) and (not inputDict["min-inventory"]) and (not inputDict["shelf-life"]) and (not inputDict["standard-price"])):
        productError = "You didn't enter anything!"

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    elif (inputDict["product-id"]):
        result = POS_database.editProduct(db, inputDict["product-id"], inputDict["product-name"], inputDict["supplier-id"], inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])
        
        if (result == POS_database.NO_RESULT):
            productError = "That item is not in the database."

    # else if the user did not enter an id, add a new user
    else:
        result = POS_database.addProduct(db, inputDict["product-name"], inputDict["supplier-id"],  inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])
        if (result == POS_database.NO_RESULT):
            productError = "That item is not in the database."

    # reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdbcancel', methods=["POST"])
def productDBCancel():
    global productError
    productError = None
    return redirect(url_for('productsDB'))




#---------------------------------------------------------------------------------------------------------------------------------------------#
# transactions page functions                                                                                                                 #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager, cashier                                                                                                           #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/transactionsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/transactionsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def transactionsDB(page):
    global transactionError

    if is_manager(current_user) or is_cashier(current_user):
        pagination = Transaction.query.paginate(page, 16)
        return render_template("transactionsDB.html", pagination=pagination, error=transactionError)
    else:
        return redirect(url_for('login'))

@app.route('/transactiondb-delete', methods=["POST"])
@login_required
def transactionDBDeleteTransaction():
    global transactionError
    transactionError = None
    
    inputDict = POS_display.get_transaction_row(request)

    # if no transaction id was entered then print an transactionError
    if (not inputDict["transaction-id"]):
        transactionError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print transactionError
    elif (int(inputDict["transaction-id"]) > POS_database.getMaxTransactionID(db)):
        transactionError = "You entered a transaction ID that is out of bounds."

    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("transaction")

    # always reload the page
    return redirect(url_for('transactionsDB'))

@app.route('/transactiondb-add', methods=["POST"])
def transactionDBUpdateTransaction():
    global transactionError
    transactionError = None
    # get the user input from the form submit
    inputDict = POS_display.get_transaction_row(request)

    # if the dictiionary doensn't have any items in it print transactionError
    if (not inputDict):
        transactionError = "You didn't enter anything!"

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    #TODO add database support for editing a transaction
    elif (inputDict["transaction-id"]):
        result = POS_database.editTransaction(db, inputDict["transaction-id"], inputDict["customer-name"], inputDict["customer-contact"], inputDict["payment-type"])
        if (result == POS_database.NO_RESULT):
            transactionError = "That item is not in the database."

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addTransaction(db, inputDict["customer-name"], inputDict["customer-contact"], inputDict["payment-type"])

    # reload the page
    return redirect(url_for('transactionsDB'))

@app.route('/transactiondbcancel', methods=["POST"])
def transactionDBCancel():
    global transactionError
    transactionError = None
    return redirect(url_for('transactionsDB'))





#---------------------------------------------------------------------------------------------------------------------------------------------#
# items sold page functions                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager, cashier                                                                                                           #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/itemssoldDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/itemssoldDB/<int:page>', methods=['GET', 'POST'])
@login_required
def itemssoldDB(page):
    global itemSoldError

    if is_manager(current_user) or is_cashier(current_user):
        pagination = ItemSold.query.paginate(page, 16)
        return render_template("itemssoldDB.html", pagination=pagination, error=itemSoldError)
    else:
        return redirect(url_for('login'))

@app.route('/itemsolddb-delete', methods=["POST"])
@login_required
def itemsoldDBDeleteItemsold():
    global itemSoldError
    itemSoldError = None
    
    inputDict = POS_display.get_itemsold_row(request)

    # if no transaction id was entered then print an itemSoldError
    if (not inputDict["itemsold_id"]):
        itemSoldError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print itemSoldError
    elif (int(inputDict["itemsold_id"]) > POS_database.getMaxItemSoldID(db)):
        itemSoldError = "You entered an Item Sold ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("itemsold")

    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddb-add', methods=["POST"])
def itemsoldDBUpdateItemsold():
    global itemSoldError
    itemSoldError = None

    inputDict = POS_display.get_itemsold_row(request)
    #TODO database support for adding and modifying items sold

    if (inputDict["itemsold_id"]):
        result = POS_database.editItemSold(db, inputDict["itemsold_id"], inputDict["item-id"], inputDict["price-sold"], inputDict["transaction-id"])
        if (result == POS_database.NO_RESULT):
            itemSoldError = "That item is not in the database."
    else:
        result = POS_database.addItemSold(db, inputDict["item-id"], inputDict["price-sold"], inputDict["transaction-id"])
        if (result == POS_database.NO_RESULT):
            itemSoldError = "That item is not in the database."

    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddbcancel', methods=["POST"])
def itemsoldDBCancel():
    global itemSoldError
    itemSoldError = None
    return redirect(url_for('itemssoldDB'))





#---------------------------------------------------------------------------------------------------------------------------------------------#
# discounts page functions                                                                                                                    #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager                                                                                                                    #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/discountsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/discountsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def discountsDB(page):
    global discountError

    if is_manager(current_user):
        pagination = Discount.query.paginate(page, 16)
        return render_template("discountsDB.html", pagination=pagination, error=discountError)
    else:
        return redirect(url_for('login'))

@app.route('/discountdb-delete', methods=["POST"])
@login_required
def discountDBDeleteDiscount():
    global discountError
    discountError = None
    
    inputDict = POS_display.get_discount_row(request)

    # if the user didn't enter a dicount id to delete print discountError
    if (not inputDict["discount-id"]):
        discountError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print discountError
    elif (int(inputDict["discount-id"]) > POS_database.getMaxDiscountID(db)):
        discountError = "You entered a discount ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("discount")

    # always reload the page
    return redirect(url_for('discountsDB'))

@app.route('/discountdb-add', methods=["POST"])
def discountDBUpdateDiscount():
    global discountError
    discountError = None

    # get the user input from the form submit
    inputDict = POS_display.get_discount_row(request)

    # i guess dates return -1 when nothing is entered in the date boxes!
    if (inputDict["start-date"] == -1):
        start_date = date.today()
    else:
        start_date = inputDict["start-date"]
    if (inputDict["end-date"] == -1):
        end_date = date.today()
    else:
        end_date = inputDict["end-date"]

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["discount-id"]):
        result = POS_database.editDiscount(db, inputDict["discount-id"], inputDict["product-id"], start_date, end_date, inputDict["percent-off"])
        if (result == POS_database.NO_RESULT):
            discountError = "That item is not in the database."


    # else if the user did not enter an id, add a new user
    else:
        result = POS_database.addDiscount(db, inputDict["product-id"], inputDict["percent-off"], start_date, end_date)
        if (result == POS_database.NO_RESULT):
            discountError = "That item is not in the database."

    # reload the page
    return redirect(url_for('discountsDB'))

@app.route('/discountdbcancel', methods=["POST"])
def discountDBCancel():
    global discountError
    discountError = None
    return redirect(url_for('discountsDB'))





#---------------------------------------------------------------------------------------------------------------------------------------------#
# suppliers page functions                                                                                                                    #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager                                                                                                                    #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/supplierDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/supplierDB/<int:page>', methods=['GET', 'POST'])
@login_required
def supplierDB(page):
    global supplierError

    if is_manager(current_user):
        pagination = Supplier.query.paginate(page, 16)
        return render_template("suppliersDB.html", pagination=pagination, error=supplierError)
    else:
        return redirect(url_for('login'))

@app.route('/supplierdb-delete', methods=["POST"])
@login_required
def supplierDBDeleteSupplier():
    global supplierError
    supplierError = None
    
    inputDict = POS_display.get_supplier_row(request)

    # if the user didn't enter a supplier id to delete print supplierError
    if (not inputDict["supplier-id"]):
        supplierError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print supplierError
    elif (int(inputDict["supplier-id"]) > POS_database.getMaxSupplierID(db)):
        supplierError = "You entered a supplier ID that is out of bounds."

    # otherwise delete the row
    else:
        # send it to the helper!
        deleteDBRow("supplier")

    # always reload the page
    return redirect(url_for('supplierDB'))

@app.route('/supplierdb-add', methods=["POST"])
def supplierDBUpdateSupplier():
    global supplierError
    supplierError = None
    # get the user input from the form submit
    inputDict = POS_display.get_supplier_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid

    if (not inputDict["supplier-id"] and not inputDict["supplier-name"] and not inputDict["supplier-email"]):
        supplierError = "You didn't enter anything!"
    elif (inputDict["supplier-id"]):
        result = POS_database.editSupplier(db, inputDict["supplier-id"], inputDict["supplier-name"], inputDict["supplier-email"])
        if (result == POS_database.NO_RESULT):
            supplierError = "That item is not in the database."

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addSupplier(db, inputDict["supplier-name"], inputDict["supplier-email"])

    # reload the page
    return redirect(url_for('supplierDB'))

@app.route('/supplierdbcancel', methods=["POST"])
def supplierDBCancel():
    global supplierError
    supplierError = None
    return redirect(url_for('supplierDB'))



#---------------------------------------------------------------------------------------------------------------------------------------------#
# users page functions                                                                                                                        #
#---------------------------------------------------------------------------------------------------------------------------------------------#
# > permission:    manager                                                                                                                    #
# > login:         required                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------#
@app.route('/userDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/userDB/<int:page>', methods=['GET', 'POST'])
@login_required
def userDB(page):
    global userError

    if is_manager(current_user):
        pagination = User.query.paginate(page, 16)
        return render_template("userDB.html", pagination=pagination, error=userError)
    else:
        return redirect(url_for('login'))

@app.route('/userdb-delete', methods=["POST"])
@login_required
def userDBDeleteUser():
    global userError
    userError = None
    
    inputDict = POS_display.get_user_row(request)

    # if the user didn't enter an user id to delete print userError
    if (not inputDict["user-id"]):
        userError = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print userError
    elif (int(inputDict["user-id"]) > POS_database.getMaxUserID(db)):
        userError = "You entered a user ID that is out of bounds."

    # otherwise delete the row
    else:
        # send it to the helper!
        deleteDBRow("user")

    # reload the page
    return redirect(url_for('userDB'))

@app.route('/userdb-add', methods=["POST"])
def userDBUpdateUser():
    global userError
    userError = None
    # get the user input from the form submit
    inputDict = POS_display.get_user_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["user-id"]):
        result = POS_database.editUser(db, inputDict["user-id"], inputDict["username"], inputDict["password"], inputDict["permissions"])
        if (result == POS_database.NO_RESULT):
            userError = "That item is not in the database."

    # else if the user did not enter an id, add a new user
    else:
        if (not inputDict["username"]):
            userError = "You must specify a username to add a user"
        elif (not inputDict["password"]):
            userError = "You must specify a password to add a user"
        else:    
            POS_database.addUser(db, inputDict["username"], inputDict["password"], inputDict["permissions"])

    # reload the page
    return redirect(url_for('userDB'))

@app.route('/userdbcancel', methods=["POST"])
def userDBCancel():
    global userError
    userError = None
    return redirect(url_for('userDB'))



################################################################################################################################################
# HELPER FUNCTIONS #############################################################################################################################
################################################################################################################################################
def deleteDBRow(dbTableName):
    global transactionError
    
    if (dbTableName == "user"):
        getRowFunc = POS_display.get_user_row
        destroyRowFunc = POS_database.destroyUser
        idFieldName = "user-id"
    elif (dbTableName == "supplier"):
        getRowFunc = POS_display.get_supplier_row
        destroyRowFunc = POS_database.destroySupplier
        idFieldName = "supplier-id"
    elif (dbTableName == "product"):
        getRowFunc = POS_display.get_product_row
        destroyRowFunc = POS_database.destroyProduct
        idFieldName = "product-id"
    elif (dbTableName == "item"):
        getRowFunc = POS_display.get_item_row
        destroyRowFunc = POS_database.destroyItem
        idFieldName = "item-id"
    elif (dbTableName == "discount"):
        getRowFunc = POS_display.get_discount_row
        destroyRowFunc = POS_database.destroyDiscount
        idFieldName = "discount-id"
    elif (dbTableName == "transaction"):
        getRowFunc = POS_display.get_transaction_row
        destroyRowFunc = POS_database.destroyTransaction
        idFieldName = "transaction-id"
    elif (dbTableName == "itemsold"):
        getRowFunc = POS_display.get_itemsold_row
        destroyRowFunc = POS_database.destroyItemSold
        idFieldName = "itemsold_id"


    # get the user input from the form submit
    inputDict = getRowFunc(request)
    result = destroyRowFunc(db, inputDict[idFieldName]) 

    if (result == POS_database.NO_RESULT):
        error = "That item is not in the database"
        if (dbTableName == "user"):
            userError = error
        elif (dbTableName == "supplier"):
            supplierError = error
        elif (dbTableName == "product"):
            productError = error
        elif (dbTableName == "item"):
            itemError = error
        elif (dbTableName == "discount"):
            discountError = error
        elif (dbTableName == "transaction"):
            transactionError = error
        elif (dbTableName == "itemsold"):
            itemSoldError = error

    # delete the row  
    if (result == POS_database.INTEGRITY_ERROR):
        error = "Another item in your database depends on this item. You can't delete this yet."
        if (dbTableName == "user"):
            userError = error
        elif (dbTableName == "supplier"):
            supplierError = error
        elif (dbTableName == "product"):
            productError = error
        elif (dbTableName == "item"):
            itemError = error
        elif (dbTableName == "discount"):
            discountError = error
        elif (dbTableName == "transaction"):
            transactionError = error
        elif (dbTableName == "itemsold"):
            itemSoldError = error        

################################################################################################################################################
# MAIN PROGRAM #################################################################################################################################
################################################################################################################################################

# Used for local debugging
# Turn debug=False on to run without getting errors back when running locally
# Turn debug=True on to run locally and get error reports in the browser
if __name__ == '__main__':
    app.run(debug=True)
