# File : app.py
# Date : 3/19/2016 (creation)
# Desc : This is the master file for the Flask application.


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
#app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
#app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

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

                    return redirect_after_login(current_user)  #from POS_helpers #
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
    if is_manager(current_user):
        return render_template("discounts.html", discountTable=POS_logic.discountTable)
    else:
        return redirect('/')

@app.route('/discountsadd', methods=["POST"])
def discountsAddRow():
    # get the information from the user
    inputDict = POS_display.getDiscountRow(request)
    # get the product name from the database
    productName = POS_database.getProductName(db, inputDict["productID"])
    POS_logic.addDiscountRow(productName, inputDict["productID"], inputDict["saleStart"], inputDict["saleEnd"], inputDict["salePrice"])
    return redirect(url_for('discounts'))
# -------------------------------------------------- #

# Reports Page
# Requires: Login, Manager/Admin permission #
@app.route('/reports')
@login_required
def reports():
    if is_manager(current_user):
        return render_template("reports.html")
    else:
        return redirect('/')


# -------------------------------------------------- #

# Transactions Page
# Requires: Login, Manager/Admin permission #
@app.route('/transactions')
@login_required
def transactions():
    if is_manager(current_user) or is_cashier(current_user):
        items = db.session.query(Item).all()
        return render_template("transactions.html", items=items, transactionTable=POS_logic.transactionTable)
    else:
        return redirect('/')

@app.route('/transactionadd', methods=["POST"])
def transactionsAddRow():
    # get the information from the user
    inputDict = POS_display.getTransactionRow(request)
    # get the product name and price from the database
    productName = POS_database.getProductName(db, inputDict["productID"])
    pricePerUnit = POS_database.getProductPrice(db, inputDict["productID"])
    # add the received information to the local receipt table
    POS_logic.addTransactionRow(productName, inputDict["productID"], inputDict["quantity"], pricePerUnit)
    return redirect(url_for('transactions'))

@app.route('/transactioncommit', methods=["POST"])
def finishTransaction():
    # TODO send all information from the local receipt table to the database for storage
    
    # clear the local receipt table out
    POS_logic.transactionTable.clearTable()
    return redirect(url_for('transactions'))

# -------------------------------------------------- #


# Inventory Page
# Requires: Login, Manager/Admin permission #
@app.route('/inventory')
@login_required
def inventory():
    if is_manager(current_user) or is_stocker(current_user):
        items = db.session.query(Item).all()
        return render_template("inventory.html", items=items, inventoryTable=POS_logic.inventoryTable)
    else:
        return redirect('/')

@app.route('/inventoryadd', methods=["POST"])
def inventoryAddRow():
    # get the information from the user
    inputDict   = POS_display.getInventoryRow(request)
    # get the product name from the database
    productName = POS_database.getProductName(db, inputDict['productID'])
    # add all of the information received to the local stocking table
    POS_logic.addInventoryRow(productName, inputDict['productID'], inputDict['quantity'], inputDict['exp-date'], inputDict['item-cost'])
    return redirect(url_for('inventory'))

@app.route('/inventorycommit', methods=["POST"])
def updateInventory():
    # send all information from the local stocking table to the database for storage
	POS_database.updateItemTable(db, POS_logic.inventoryTable.rowsList)
    # clear the local stocking table out
	POS_logic.inventoryTable.clearTable()
	return redirect(url_for('inventory'))
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



# Used for local debugging
# Turn debug=False on to run without getting errors back when running locally
# Turn debug=True on to run locally and get error reports in the browser
if __name__ == '__main__':
    app.run(debug=True)
