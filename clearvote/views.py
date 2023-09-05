from clearvote import app
from flask import render_template, url_for, redirect
from clearvote.forms import AddressForm, RegistrationPage
from clearvote.utils.mapping.mapper import Mapper
from clearvote.utils.data.precinct import Precinct
from urllib.parse import unquote


@app.route("/")
def index():
    return redirect(url_for('address_lookup'))


# Address lookup route
@app.route("/address", methods=["GET", "POST"])
def address_lookup():
    form = AddressForm()
    if form.validate_on_submit():
        return redirect(url_for("registration", address=form.address.data))
    return render_template("address_lookup.html", form=form, title="ClearVote")

@app.route("/address/registration/<address>", methods=["GET", "POST"])
def registration(address):
    form = RegistrationPage()
    if form.validate_on_submit():
        if form.is_registered.data:
            return redirect(url_for("address_info", address=address))
        if form.not_registered.data:
            return redirect("https://voter.votewa.gov/WhereToVote.aspx")
    return render_template("registration_page.html", address=address, form=form)

@app.route("/address/<address>")
def address_info(address):
    mapper = Mapper()
    try:
        precinct = mapper.get_precinct(address)
    except ValueError:
        return f"{ address } is not in a known Seattle precinct."
    except RuntimeError:
        return f"Could not connect to MapBox, please try again later."
    return render_template("address_info.html", address=address, precinct=precinct)