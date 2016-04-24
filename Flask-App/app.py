"""
File: app.py
Author: Jacob Campbell; Ethan Morisette
Created: 3/11/2016
Purpose: This is the master file for the Flask application.
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


#############################
# Route Declarations
#############################


# Home Route (login page) #
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
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
    POS_logic.report_table.make_table([1,3,4],[4,3,4],[4,4,4])
    if is_manager(current_user):
        return render_template("reports.html", reportTable=POS_logic.report_table)
    else:
        return redirect('/')

@app.route('/download', methods=["POST"])
def downloadReport():
    dropDownItem = request.form["report-dropdown"]
    startDate = POS_display.convert_string_to_date(request.form["report-start-date"])
    endDate = POS_display.convert_string_to_date(request.form["report-end-date"])

    # if the report type is inventory worth report, do special download

    # if the report type is revenue audit report, do special download

    # if the report type is purchase order report, do special download

    # otherwise do a database table report download
    POS_database.toCSV(db, dropDownItem)

    return redirect(url_for("reports"))

# -------------------------------------------------- #

# Cashier Page
# Requires: Login, Cashier/Manager permission #
@app.route('/cashier')
@login_required
def cashier():
    if is_manager(current_user) or is_cashier(current_user):
        return render_template("cashier.html", cashierTable=POS_logic.cashier_table)
    else:
        return redirect('/')


@app.route('/cashieradd', methods=["POST"])
def cashierAddRow():

    # get the information from the user
    inputDict = POS_display.get_cashier_row(request)
    
    if (inputDict["row_number"]):
        #TODO add edit functionality for cashier
        pass
    else:
        #add 
        productID = POS_database.getItemProduct(db, inputDict["item_id"])
        productName = POS_database.getProductName(db, productID)
        pricePerUnit = POS_database.getProductPrice(db, productID)
        # add the received information to the local receipt table
        POS_logic.cashier_table.add_row(inputDict["item_id"], productName, pricePerUnit)
        # get the product name and price from the database

    # reload page
    return redirect(url_for('cashier'))

@app.route('/cashierdelete', methods=["POST"])
def cashierDeleteRow():
    inputDict = POS_display.get_cashier_row(request)
    POS_logic.cashier_table.delete_row(int(inputDict["row_number"]))
    return redirect(url_for('cashier'))

@app.route('/cashiercommit', methods=["POST"])
def finishTransaction():
    # TODO send all information from the local receipt table to the database for storage
    POS_database.updateCashierTable(db, POS_logic.cashier_table.rowsList)
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
    if is_manager(current_user) or is_stocker(current_user):
        return render_template("stocker.html", stockerTable=POS_logic.stocker_table)
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
        POS_logic.stocker_table.edit_row(int(inputDict["row_number"]), productID, productName, int(inputDict["quantity"]), inputDict["inventory_cost"])
    else:
        # add all of the information received to the local stocking table
        POS_logic.stocker_table.add_row(productID, productName, int(inputDict['quantity']), inputDict['inventory_cost'])
    
    return redirect(url_for('stocker'))

@app.route('/stockerdelete', methods=["POST"])
def stockerDeleteRow():
    inputDict = POS_display.get_stocker_row(request)
    POS_logic.stocker_table.delete_row(int(inputDict["row_number"]))
    return redirect(url_for('stocker'))

@app.route('/stockercommit', methods=["POST"])
def updateInventory():
    # send all information from the local stocking table to the database for storage
    POS_database.updateItemTable(db, POS_logic.stocker_table.rowsList)
    # clear the local stocking table out
    POS_logic.stocker_table.clear_table()
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
# Requires: Login, Manager/Admin/Stocker permission #
@app.route('/itemsDB',defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/itemsDB/<int:page>', methods=['GET', 'POST'])
@login_required
def itemsDB(page):
    if is_manager(current_user) or is_cashier(current_user):
        pagination = Item.query.paginate(page, 16)
        return render_template("itemsDB.html", pagination=pagination)
    else:
        return redirect(url_for('login'))

@app.route('/itemdb-delete', methods=["POST"])
@login_required
def itemDBDeleteItem():
    # send it to the helper!
    deleteDBRow("item")
    # reload the page
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
@app.route('/productsDB', methods=['GET', 'POST'])
@login_required
def productsDB():
    result = db.session.query(Product).all()
    return render_template("productsDB.html", productsDBTable=result)

@app.route('/productdb-delete', methods=["POST"])
@login_required
def productDBDeleteProduct():
    # send it to the helper!
    deleteDBRow("product")
    # reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdb-add', methods=["POST"])
def productDBUpdateProduct():
    # get the user input from the form submit
    inputDict = POS_display.get_product_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    if (inputDict["product-id"]):
        POS_database.editProduct(db, inputDict["product-id"], inputDict["product-name"], inputDict["supplier-id"], inputDict["inventory-count"], inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])

    # else if the user did not enter an id, add a new user
    else:
        POS_database.addProduct(db, inputDict["product-name"], inputDict["supplier-id"],  inputDict["inventory-count"], inputDict["min-inventory"], inputDict["shelf-life"], inputDict["standard-price"])

    # reload the page
    return redirect(url_for('productsDB'))

@app.route('/productdbcancel', methods=["POST"])
def productDBCancel():
    return redirect(url_for('productsDB'))

# -------------------------------------------------- #


# transactionsDB
# Requires: Login, Manager/Admin/Cashier permission #
@app.route('/transactionsDB', methods=['GET', 'POST'])
@login_required
def transactionsDB():
    result = db.session.query(Transaction).all()
    return render_template("transactionsDB.html", transactionsDBTable=result)

@app.route('/transactiondb-delete', methods=["POST"])
@login_required
def transactionDBDeleteTransaction():
    # send it to the helper!
    deleteDBRow("transaction")
    # reload the page
    return redirect(url_for('transactionsDB'))

@app.route('/transactiondb-add', methods=["POST"])
def transactionDBUpdateTransaction():
    # get the user input from the form submit
    inputDict = POS_display.get_transaction_row(request)

    #  if the user did enter an id number, check if its valid and modify user if it is
    #TODO check if the entered id number is valid
    #TODO add database support for editing a transaction
    if (inputDict["transaction-id"]):
        pass

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
@app.route('/itemssoldDB', methods=['GET', 'POST'])
@login_required
def itemssoldDB():
    result = db.session.query(ItemSold).all()
    return render_template("itemssoldDB.html", itemsSoldDBTable=result)

@app.route('/itemsolddb-delete', methods=["POST"])
@login_required
def itemsoldDBDeleteItemsold():
    #TODO database support for deleting itemssold

    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddb-add', methods=["POST"])
def itemsoldDBUpdateItemsold():
    #TODO database support for adding and modifying items sold
    
    # reload the page
    return redirect(url_for('itemssoldDB'))

@app.route('/itemsolddbcancel', methods=["POST"])
def itemsoldDBCancel():
    return redirect(url_for('itemssoldDB'))

# -------------------------------------------------- #


# discountsDB
# Requires: Login, Manager/Admin permission #
@app.route('/discountsDB', methods=['GET', 'POST'])
@login_required
def discountsDB():
    result = db.session.query(Discount).all()
    return render_template("discountsDB.html", discountsDBTable=result)

@app.route('/discountdb-delete', methods=["POST"])
@login_required
def discountDBDeleteDiscount():
    # send it to the helper!
    deleteDBRow("discount")
    # reload the page
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
@app.route('/supplierDB', methods=['GET', 'POST'])
@login_required
def supplierDB():
    result = db.session.query(Supplier).all()
    return render_template("suppliersDB.html", suppliersDBTable=result)

@app.route('/supplierdb-delete', methods=["POST"])
@login_required
def supplierDBDeleteSupplier():
    # send it to the helper!
    deleteDBRow("supplier")

    # reload the page
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
@app.route('/userDB', methods=['GET', 'POST'])
@login_required
def userDB():
    result = db.session.query(User).all()
    return render_template("userDB.html", usersDBTable=result)

@app.route('/userdb-delete', methods=["POST"])
@login_required
def userDBDeleteUser():
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
