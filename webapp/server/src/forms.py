from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional

class AddressForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Enter")

class RegistrationPage(FlaskForm):
    is_registered = SubmitField("Yes")
    not_registered = SubmitField("No")

class CandidatePage(FlaskForm):
    Next = StringField("Next")

class CreateUserForm(FlaskForm):
    name = StringField("Name")
    email = StringField("Email", validators=[Optional()])
    phone = StringField("Phone (optional, SMS carrier rates may apply)", validators=[Optional()])
    submit = SubmitField("Create User")