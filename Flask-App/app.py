from flask import *
from functools import wraps

app = Flask(__name__)
app.secret_key = "my precious"


# Function Requiring a user to be logged in to access a page #
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Use admin | admin to get in the site.'
        else:
            session['logged_in'] = True
            flash('You have been logged in.')
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/welcome')
@login_required
def welcome():
    return render_template("welcome.html")


if __name__ == '__main__':
    app.run(debug=True)
