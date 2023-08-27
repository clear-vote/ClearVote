from clearvote import app
from flask import render_template, url_for
from clearvote.forms import AddressForm

@app.route("/")
def index():
    print("HEWWO")
    return "ClearVote!"

@app.route("/address",  methods=['GET', 'POST'])
def address():
    form = AddressForm()
    if form.validate_on_submit():
        return f"Address: {form.address.data}"
    return render_template("address_lookup.html", form=form)