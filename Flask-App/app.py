# File : app.py
# Date : 3/19/2016 (creation)
# Desc : This is the master file for the Flask application.


# Import statements #
from flask import *
from functools import wraps
from templates.form import LoginForm

# -------------------------------------------------- #


# Grabs the domain name the app is running on #
app = Flask(__name__)
# -------------------------------------------------- #


# Secret Key generated randomly to persist through sessions #
app.secret_key = "\xc7\xd5\x10C\x19\x82q\x13\xb03\xe6>\xeb\xcdEK\xc1I\x1a\xc6\xaa\x08\xd1\t"
# -------------------------------------------------- #


#############################
# Function Declarations
#############################


# Require a user to be logged in to access a page #
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login to view this page.')
            return redirect(url_for('login'))

    return wrap
# -------------------------------------------------- #


#############################
# Route Declarations
#############################


# Home Route (login page) #
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            if request.form['username'] != 'admin':
                if request.form['password'] != 'admin':
                    error = "Invalid username and password. Please try again"
                    render_template('login.html', form=form, error=error)
                else:
                    error = "Invalid username. Please try again"
                    render_template('login.html', form=form, error=error)
            else:
                if request.form['password'] != 'admin':
                    error = "Username found, but invalid password. Please try again"
                    render_template('login.html', form=form, error=error)
                else:
                    session['logged_in'] = True
                    flash('You have been successfully logged in.')
                    return redirect(url_for('welcome'))
        else:
            render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form, error=error)
# -------------------------------------------------- #


# Logout Route(has no page, merely a function) #
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You have been successfully logged out.')
    return redirect(url_for('login'))
# -------------------------------------------------- #


# Welcome Page (Requires user to be logged in to see) #
@app.route('/welcome')
@login_required
def welcome():
    return render_template("welcome.html")
# -------------------------------------------------- #


# Used for local debugging
# Turn debug=False on to run without getting errors back when running locally
# Turn debug=True on to run locally and get error reports in the browser
if __name__ == '__main__':
    app.run(debug=True)
