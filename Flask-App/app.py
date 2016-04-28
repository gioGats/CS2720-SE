"""
File: app.py
Author: Jacob Campbell; Ethan Morisette
Created: 3/11/2016 (Last Modified: 4/24/2016)
Purpose: This is the master file for the Flask application, contains logic for generating webpages, routing
data, and managing the flow of the entire system.
"""

#############################
# Import Statements
#############################
from flask import *
from POS_helpers import *
from templates.form import LoginForm, RegisterForm
from helper import *
from helper import login_user, login_required, logout_user
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import *
import POS_display
import POS_logic

# -------------------------------------------------- #


#############################
# Configure the Application
#############################

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


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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


# -------------------------------------------------- #


#############################
# Global Variables
#############################
current_user = None
error = None

#############################
# Route Declarations
#############################


# Home Route (login page) #
@app.route('/', methods=['GET', 'POST'])
def login():
    global error
    form = LoginForm(request.form)
    global current_user  # allows changing of the globally defined current_user #

    if request.method == 'POST':  # If the login button was clicked #
        if form.validate_on_submit():

            user = User.query.filter_by(name=request.form['username']).first()

            if user is None:
                error = "Invalid username. Please try again"
                render_template('login.html', form=form, error=error)
            else:
                if bcrypt.check_password_hash(user.password, request.form['password']):
                    login_user(user)
                    current_user = user
                    flash('You have been successfully logged in.')

                    return redirect_after_login(current_user)  # from POS_helpers #
                else:
                    error = "Username found, but invalid password. Please try again."
                    render_template('login.html', form=form, error=error)
        else:
            render_template('login.html', form=form, error=error)

    # If the form was not a submit, we just need to grab the page data (GET request) #
    return render_template('login.html', form=form, error=error)


# -------------------------------------------------- #


# Logout Route(has no page, merely a function) #
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


# -------------------------------------------------- #

# Discounts Page
# Requires: Login, Manager/Admin permission #
@app.route('/discounts')
@login_required
def discounts():
    discountTable = []
    if is_manager(current_user):
        return render_template("discounts.html", discountTable=discountTable)
    else:
        return redirect('/')


@app.route('/discountsadd', methods=["POST"])
def discountsAddRow():
    # get the information from the user
    inputDict = POS_display.getDiscountRow(request)
    # get the product name from the database
    productName = POS_database.getProductName(db, inputDict["productID"])
    POS_logic.addDiscountRow(productName, inputDict["productID"], inputDict["saleStart"], inputDict["saleEnd"],
                             inputDict["salePrice"])
    return redirect(url_for('discounts'))


# -------------------------------------------------- #

# Reports Page
# Requires: Login, Manager/Admin permission #
@app.route('/reports')
@login_required
def reports():
    DailyRep = POS_database.revenueCheck(db, "day")
    WeeklyRep = POS_database.revenueCheck(db, "week")
    MonthlyRep = POS_database.revenueCheck(db, "month")
    revenues = [DailyRep[0], WeeklyRep[0], MonthlyRep[0]]
    costs = [DailyRep[1], WeeklyRep[1], MonthlyRep[1]]
    profits = [DailyRep[2], WeeklyRep[2], MonthlyRep[2]]
    POS_logic.report_table.make_table(revenues, costs, profits)
    if is_manager(current_user):
        return render_template("reports.html", reportTable=POS_logic.report_table)
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

# -------------------------------------------------- #

# Cashier Page
# Requires: Login, Cashier/Manager permission #
@app.route('/cashier')
@login_required
def cashier():
    
    if is_manager(current_user) or is_cashier(current_user):
        return render_template("cashier.html", cashierTable=POS_logic.cashier_table, error=error)
    else:
        return redirect('/')


@app.route('/cashieradd', methods=["POST"])
def cashierAddRow():
    global error
    error = None
    # get the information from the user
    inputDict = POS_display.get_cashier_row(request)
    
    if (inputDict["row_number"]):
        POS_logic.cashier_table.edit_row(inputDict["row_number"], inputDict["item_id"], inputDict["price_per_unit"])
    else:
        # get the product name and price from the database
        productID = POS_database.getItemProduct(db, inputDict["item_id"])
        productName = POS_database.getProductName(db, productID)
        pricePerUnit = POS_database.getProductPrice(db, productID)
        # add the received information to the local receipt table
        POS_logic.cashier_table.add_row(inputDict["item_id"], productName, pricePerUnit)

    # reload page
    return redirect(url_for('cashier'))

@app.route('/cashierdelete', methods=["POST"])
def cashierDeleteRow():
    global error
    error = None
    inputDict = POS_display.get_cashier_row(request)

    # if no row id was entered then print an error
    if (not inputDict["row_number"]):
        error = "What are you trying to delete?"

    # if the row number does not exist, display an error
    elif (int(inputDict["row_number"]) > POS_logic.cashier_table.get_row_count()):
        error = "That row number is out of bounds."

    # otherwise, delete the row number
    else:
        POS_logic.cashier_table.delete_row(int(inputDict["row_number"]))
    
    # always reload the page
    return redirect(url_for('cashier'))

@app.route('/customerinfo', methods=["POST"])
def enterCustomerInfo():
    global error
    error = None

    # if the cart is empty print an error and reload the cashier page
    print(POS_logic.cashier_table.isEmpty())
    if (POS_logic.cashier_table.isEmpty()):
        error = "You don't have any items in your cart!"
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
    POS_logic.cashier_table.clear_table()
    return redirect(url_for('cashier'))



# -------------------------------------------------- #


# Stocker Page
# Requires: Login, Stocker/Manager permission #
@app.route('/stocker')
@login_required
def stocker():
    global error
    if is_manager(current_user) or is_stocker(current_user):
        return render_template("stocker.html", stockerTable=POS_logic.stocker_table, error=error)
    else:
        return redirect('/')


@app.route('/stockeradd', methods=["POST"])
def stockerAddRow():
    # get the information from the user
    inputDict = POS_display.get_stocker_row(request)

    productID = inputDict['product_id']

    if (productID == ''):
        productID = POS_logic.stocker_table.rowsList[int(inputDict["row_number"])-1].product_id

    # get the product name from the database
    productName = POS_database.getProductName(db, productID)

    if (inputDict["row_number"]):
        print("I am editing!")
        POS_logic.stocker_table.edit_row(inputDict["row_number"], productID, productName, inputDict["quantity"], inputDict["inventory_cost"])
    else:
        # add all of the information received to the local stocking table
        POS_logic.stocker_table.add_row(productID, productName, int(inputDict['quantity']), inputDict['inventory_cost'])
    
    return redirect(url_for('stocker'))

@app.route('/stockerdelete', methods=["POST"])
def stockerDeleteRow():
    global error
    error = None
    inputDict = POS_display.get_stocker_row(request)

    # if no row id was entered then print an erro
    if (not inputDict["row_number"]):
        error = "What are you trying to delete?"

    # if the enter row number is out of bounds, print error
    elif (int(inputDict["row_number"]) > POS_logic.stocker_table.get_row_count()):
        error = "That row number is out of bounds!"

    # otherwise go ahead and delete the row
    else:
        POS_logic.stocker_table.delete_row(int(inputDict["row_number"]))

    # always reload the stocker page
    return redirect(url_for('stocker'))

@app.route('/stockercommit', methods=["POST"])
def updateInventory():
    global error
    error = None

    # if there aren't any items in the inventory, print error
    if (POS_logic.stocker_table.isEmpty()):
        error = "You don't have any items in your cart!"

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
    POS_logic.stocker_table.clear_table()
    return redirect(url_for('stocker'))


# -------------------------------------------------- #


# Register Page
# Requires: Login, Manager/Admin permission #
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    global current_user

    form = RegisterForm()
    if is_manager(current_user):
        if form.validate_on_submit():
            user = User(
                name=form.username.data,
                password=form.password.data,
                permissions=form.permission.data
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            current_user = user
            return redirect('/')

        else:
            return render_template("register.html", form=form)
    else:
        return redirect('/')


# -------------------------------------------------- #

#############################
# Database Page Routes
#############################


# itemsDB
# Requires: Login, Manager/Admin/Cashier permission #
@app.route('/itemsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/itemsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def itemsDB(page):
    global error

    if is_manager(current_user) or is_stocker(current_user):
        pagination = Item.query.paginate(page, 16)
        return render_template("itemsDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/itemdb-delete', methods=["POST"])
@login_required
def itemDBDeleteItem():
    global error
    error = None
    
    inputDict = POS_display.get_item_row(request)

    # if the user didn't enter an item id to delete print error
    if (not inputDict["item-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["item-id"]) > POS_database.getMaxItemID(db)):
        error = "You entered an item ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("item")

    return redirect(url_for('itemsDB'))

@app.route('/itemdb-add', methods=["POST"])
def itemDBUpdateItem():
    # get the user input from the form submit
    inputDict = POS_display.get_item_row(request)

    #  if the user did enter an id number, check if its valid and modify item if it is
    #TODO check if the entered id number is valid

    if inputDict["item-id"]:
        POS_database.editItem(db, inputDict["item-id"], inputDict["product-id"], inputDict["inventory-cost"])

    # else if the user did not enter an id, add a new item
    else:
        POS_database.addItem(db, inputDict["product-id"], inputDict["inventory-cost"])
        pagination = Item.query.paginate(1, 16)
        page = pagination.pages
        return redirect(url_for('itemsDB', page=page))
    # reload the page
    return redirect(url_for('itemsDB'))


@app.route('/itemdbcancel', methods=["POST"])
def itemDBCancel():
    return redirect(url_for('itemsDB'))

# -------------------------------------------------- #


# productsDB
# Requires: Login, Manager/Admin/Stocker permission #
@app.route('/productsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/productsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def productsDB(page):
    global error

    if is_manager(current_user) or is_stocker(current_user):
        pagination = Product.query.paginate(page, 16)
        return render_template("productsDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/productdb-delete', methods=["POST"])
@login_required
def productDBDeleteProduct():
    global error
    error = None
    
    inputDict = POS_display.get_product_row(request)

    # if the user didn't enter an item id to delete print error
    if (not inputDict["product-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["product-id"]) > POS_database.getMaxProductID(db)):
        error = "You entered a product ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("product")

    # always reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdb-add', methods=["POST"])
def productDBUpdateProduct():
    global error
    error = None
    # get the user input from the form submit
    inputDict = POS_display.get_product_row(request)

    # if the dictiionary doensn't have any items in it print error
    if ((not inputDict["product-id"]) and (not inputDict["product-name"]) and (not inputDict["supplier-id"]) and (not inputDict["min-inventory"]) and (not inputDict["shelf-life"]) and (not inputDict["standard-price"])):
        print("blah")
        error = "You didn't enter anything!"

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    elif (inputDict["product-id"]):
        POS_database.editProduct(db, inputDict["product-id"], inputDict["product-name"], inputDict["supplier-id"], inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addProduct(db, inputDict["product-name"], inputDict["supplier-id"],  inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])

    # reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdbcancel', methods=["POST"])
def productDBCancel():
    return redirect(url_for('productsDB'))

# -------------------------------------------------- #


# transactionsDB
# Requires: Login, Manager/Admin/Cashier permission #
@app.route('/transactionsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/transactionsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def transactionsDB(page):
    global error

    if is_manager(current_user) or is_cashier(current_user):
        pagination = Transaction.query.paginate(page, 16)
        return render_template("transactionsDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/transactiondb-delete', methods=["POST"])
@login_required
def transactionDBDeleteTransaction():
    global error
    error = None
    
    inputDict = POS_display.get_transaction_row(request)

    # if no transaction id was entered then print an error
    if (not inputDict["transaction-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["transaction-id"]) > POS_database.getMaxTransactionID(db)):
        error = "You entered a transaction ID that is out of bounds."

    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("transaction")

    # always reload the page
    return redirect(url_for('transactionsDB'))

@app.route('/transactiondb-add', methods=["POST"])
def transactionDBUpdateTransaction():
    global error
    error = None
    # get the user input from the form submit
    inputDict = POS_display.get_transaction_row(request)

    # if the dictiionary doensn't have any items in it print error
    if (not inputDict):
        error = "You didn't enter anything!"

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    #TODO add database support for editing a transaction
    elif (inputDict["transaction-id"]):
        POS_database.editTransaction(db, inputDict["transaction-id"], inputDict["customer-name"], inputDict["customer-contact"], inputDict["payment-type"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addTransaction(db, inputDict["customer-name"], inputDict["customer-contact"], inputDict["payment-type"])

    # reload the page
    return redirect(url_for('transactionsDB'))

@app.route('/transactiondbcancel', methods=["POST"])
def transactionDBCancel():
    return redirect(url_for('transactionsDB'))

# -------------------------------------------------- #


# itemssoldDB
# Requires: Login, Manager/Admin/Cashier permission #
@app.route('/itemssoldDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/itemssoldDB/<int:page>', methods=['GET', 'POST'])
@login_required
def itemssoldDB(page):
    global error

    if is_manager(current_user) or is_cashier(current_user):
        pagination = ItemSold.query.paginate(page, 16)
        return render_template("itemssoldDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/itemsolddb-delete', methods=["POST"])
@login_required
def itemsoldDBDeleteItemsold():
    global error
    error = None
    
    inputDict = POS_display.get_itemsold_row(request)

    # if no transaction id was entered then print an error
    if (not inputDict["itemsold_id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["itemsold_id"]) > POS_database.getMaxItemSoldID(db)):
        error = "You entered an Item Sold ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("itemsold")

    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddb-add', methods=["POST"])
def itemsoldDBUpdateItemsold():
    inputDict = POS_display.get_itemsold_row(request)
    #TODO database support for adding and modifying items sold
    if (inputDict["itemsold_id"]):
        POS_database.editItemSold(db, inputDict["itemsold_id"], inputDict["item-id"], inputDict["price-sold"], inputDict["transaction-id"])
    else:
        POS_database.addItemSold(db, inputDict["item-id"], inputDict["price-sold"], inputDict["transaction-id"])

    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddbcancel', methods=["POST"])
def itemsoldDBCancel():
    return redirect(url_for('itemssoldDB'))

# -------------------------------------------------- #


# discountsDB
# Requires: Login, Manager/Admin permission #
@app.route('/discountsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/discountsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def discountsDB(page):
    global error

    if is_manager(current_user):
        pagination = Discount.query.paginate(page, 16)
        return render_template("discountsDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/discountdb-delete', methods=["POST"])
@login_required
def discountDBDeleteDiscount():
    global error
    error = None
    
    inputDict = POS_display.get_discount_row(request)

    # if the user didn't enter a dicount id to delete print error
    if (not inputDict["discount-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["discount-id"]) > POS_database.getMaxDiscountID(db)):
        error = "You entered a discount ID that is out of bounds."
        
    # otherwise delete the row
    else: 
        # send it to the helper!
        deleteDBRow("discount")

    # always reload the page
    return redirect(url_for('discountsDB'))

@app.route('/discountdb-add', methods=["POST"])
def discountDBUpdateDiscount():
    # get the user input from the form submit
    inputDict = POS_display.get_discount_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["discount-id"]):
        POS_database.editDiscount(db, inputDict["discount-id"], inputDict["product-id"], inputDict["start-date"], inputDict["end-date"], inputDict["percent-off"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addDiscount(db, inputDict["product-id"], inputDict["percent-off"], inputDict["start-date"], inputDict["end-date"])

    print(inputDict["product-id"])
    print(inputDict["percent-off"])
    print(inputDict["start-date"])
    print(inputDict["end-date"])

    # reload the page
    return redirect(url_for('discountsDB'))

@app.route('/discountdbcancel', methods=["POST"])
def discountDBCancel():
    return redirect(url_for('discountsDB'))

# -------------------------------------------------- #


# supplierDB
# Requires: Login, Manager/Admin permission #
@app.route('/supplierDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/supplierDB/<int:page>', methods=['GET', 'POST'])
@login_required
def supplierDB(page):
    global error

    if is_manager(current_user):
        pagination = Supplier.query.paginate(page, 16)
        return render_template("suppliersDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/supplierdb-delete', methods=["POST"])
@login_required
def supplierDBDeleteSupplier():
    global error
    error = None
    
    inputDict = POS_display.get_supplier_row(request)

    # if the user didn't enter a supplier id to delete print error
    if (not inputDict["supplier-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["supplier-id"]) > POS_database.getMaxSupplierID(db)):
        error = "You entered a supplier ID that is out of bounds."

    # otherwise delete the row
    else:
        # send it to the helper!
        deleteDBRow("supplier")

    # always reload the page
    return redirect(url_for('supplierDB'))

@app.route('/supplierdb-add', methods=["POST"])
def supplierDBUpdateSupplier():
    # get the user input from the form submit
    inputDict = POS_display.get_supplier_row(request)



    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["supplier-id"]):
        POS_database.editSupplier(db, inputDict["supplier-id"], inputDict["supplier-name"], inputDict["supplier-email"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addSupplier(db, inputDict["supplier-name"], inputDict["supplier-email"])

    # reload the page
    return redirect(url_for('supplierDB'))

@app.route('/supplierdbcancel', methods=["POST"])
def supplierDBCancel():
    return redirect(url_for('supplierDB'))

# -------------------------------------------------- #


# userDB
# Requires: Login, Manager/Admin permission #
@app.route('/userDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/userDB/<int:page>', methods=['GET', 'POST'])
@login_required
def userDB(page):
    global error

    if is_manager(current_user):
        pagination = User.query.paginate(page, 16)
        return render_template("userDB.html", pagination=pagination, error=error)
    else:
        return redirect(url_for('login'))

@app.route('/userdb-delete', methods=["POST"])
@login_required
def userDBDeleteUser():
    global error
    error = None
    
    inputDict = POS_display.get_user_row(request)

    # if the user didn't enter an user id to delete print error
    if (not inputDict["user-id"]):
        error = "What are you trying to delete?"

    # if the id input is greater than the max id in the database, then print error
    elif (int(inputDict["user-id"]) > POS_database.getMaxUserID(db)):
        error = "You entered a user ID that is out of bounds."

    # otherwise delete the row
    else:
        # send it to the helper!
        deleteDBRow("user")

    # reload the page
    return redirect(url_for('userDB'))

@app.route('/userdb-add', methods=["POST"])
def userDBUpdateUser():
    # get the user input from the form submit
    inputDict = POS_display.get_user_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["user-id"]):
        POS_database.editUser(db, inputDict["user-id"], inputDict["username"], inputDict["password"], inputDict["permissions"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addUser(db, inputDict["username"], inputDict["password"], inputDict["permissions"])

    # reload the page
    return redirect(url_for('userDB'))

@app.route('/userdbcancel', methods=["POST"])
def userDBCancel():
    return redirect(url_for('userDB'))


def deleteDBRow(dbTableName):
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

    # delete the row  
    destroyRowFunc(db, inputDict[idFieldName])

# -------------------------------------------------- #


# Used for local debugging
# Turn debug=False on to run without getting errors back when running locally
# Turn debug=True on to run locally and get error reports in the browser
if __name__ == '__main__':
    app.run(debug=True)
