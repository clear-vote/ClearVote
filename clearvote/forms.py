from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField)
from wtforms.validators import (DataRequired, ValidationError)

class AddressForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Enter")

class RegistrationPage(FlaskForm):
    is_registered = SubmitField("Yes")
    not_registered = SubmitField("No")