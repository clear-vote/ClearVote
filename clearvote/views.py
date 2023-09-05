from clearvote import app
from flask import render_template, url_for, redirect, request
from clearvote.forms import AddressForm, CandidatePage, CreateUserForm, RegistrationPage
from clearvote.utils.mapping.mapper import Mapper
from clearvote.utils.data.precinct import Precinct
from clearvote.utils.judging.drafter import Drafter
from urllib.parse import unquote
import json


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

@app.route("/registration/<address>", methods=["GET", "POST"])
def registration(address):
    form = RegistrationPage()
    if form.validate_on_submit():
        if form.is_registered.data:
            return redirect(url_for("candidate_info", address=address))
        if form.not_registered.data:
            return redirect("https://voter.votewa.gov/WhereToVote.aspx")
    return render_template("registration_page.html", address=address, form=form)

@app.route("/address/<address>")
def candidate_info(address):
    form = CandidatePage()
    mapper = Mapper()
    try:
        precinct = mapper.get_precinct(address)
        election = Drafter.filter_contest_data(precinct=precinct)
    except ValueError:
        return f"{ address } is not in a known Seattle precinct."
    except RuntimeError:
        return f"Could not connect to MapBox, please try again later."
    if form.validate_on_submit():
        if form.Next:
            return redirect(url_for("create_user"))
    return render_template("candidate_info.html", address=address, precinct=precinct, election=election)

@app.route("/create_user/", methods=["GET", "POST"])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data if form.email.data else None  # None if not provided
        phone = form.phone.data if form.phone.data else None

        if not email and not phone:
            return "You must provide either an email or a phone number."

        return redirect(url_for("thank_you", name=name, email=email, phone=phone))

    return render_template("create_user.html", form=form)

@app.route("/thank_you")
def thank_you():
    name = request.args.get('name')
    phone = request.args.get('phone')
    email = request.args.get('email')
    return render_template("thank_you.html", name=name, email=email, phone=phone)
