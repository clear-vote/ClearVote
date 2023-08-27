from clearvote import app
from flask import render_template, url_for, redirect
from clearvote.forms import AddressForm
from clearvote.utils.Mapping.mapper import Mapper
from clearvote.utils.Mapping.precinct import Precinct
from urllib.parse import unquote

@app.route("/")
def index():
    return "ClearVote!"

@app.route("/address",  methods=['GET', 'POST'])
def address_lookup():
    form = AddressForm()
    if form.validate_on_submit():
        return redirect(url_for("address_info", address=form.address.data))
    return render_template("address_lookup.html", form=form)

@app.route("/address/<address>")
def address_info(address):
    p = Mapper.get_precinct(address)
    return render_template("address_info.html", address=address, precinct=p)