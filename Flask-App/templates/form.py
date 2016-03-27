from flask_wtf import Form
from wtforms import TextField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(Form):
    username = TextField(
        'Username',
        validators=[DataRequired("Username required."), Length(min=3, max=16)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired("Password required."), Length(min=3, max=16)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(message="Password confirmation required."),
            EqualTo('password', message='Passwords do not match. Please try again.')
        ]
    )
    permission = IntegerField(
        'Permission Level',
        validators=[DataRequired(message="Input must be a number from 1 to 3. "),
                    NumberRange(min=1, max=3, message='1: Manager, 2: Cashier, 3:Stocker')]
    )
