from flask import current_app as app
from flask import render_template, url_for, redirect, request
from src.forms import AddressForm, CandidatePage, CreateUserForm, RegistrationPage
from src.utils.mapping.mapper import Mapper
from src.utils.data.precinct import Precinct
from src.utils.judging.drafter import Drafter
from urllib.parse import unquote
from random import Random, randint, shuffle

def init_app(app):
    iconMapping = {
        'Wellbeing': 'fa-heart',
        'Homelessness': 'fa-home',
        'Emergency': 'fa-ambulance',
        'Justice': 'fa-balance-scale',
        'Security': 'fa-shield-alt',
        'Transit': 'fa-bus',
        'Infrastructure': 'fa-road',
        'Economics': 'fa-chart-line',
        'Community': 'fa-users',
        'Environment': 'fa-leaf',
        'Development': 'fa-hammer',
        'Zoning': 'fa-map-signs',
        'Accountability': 'fa-check-circle',
        'Operations': 'fa-cogs',
        'Services': 'fa-concierge-bell',
        'Management': 'fa-briefcase',
        'Academics': 'fa-book',
        'Teachers': 'fa-chalkboard-teacher',
        'Quality': 'fa-star',
        'Funding': 'fa-dollar-sign',
        'Equity': 'fa-equals',
        'Safety': 'fa-hard-hat',
        'Opportunity': 'fa-lightbulb',
        'Extracurricular': 'fa-football-ball',
        'Policy': 'fa-gavel'
    }

    @app.context_processor
    def utility_processor():
        def get_icon_for_word(word):
            return iconMapping.get(word, 'fa-question')
        return dict(getIconForWord=get_icon_for_word)
    
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
            # Define a seed value
            seed = randint(0, 10**6)
            precinct = mapper.get_precinct(address)
            # Shuffle candidates for highlights_election
            highlights_election = Drafter.draft(precinct=precinct)
            rand_instance1 = Random(seed)  # Create a new Random instance with the seed
            for contest in highlights_election:
                shuffle(contest['candidates'], random=rand_instance1.random)
            # Shuffle candidates for total_election
            total_election = Drafter.get_contest_data(precinct)
            rand_instance2 = Random(seed)  # Create another new Random instance with the same seed
            for contest in total_election:
                shuffle(contest['candidates'], random=rand_instance2.random)
            for contest in total_election:
                max_value = max([max([issue[1] for issue in candidate['issues']]) for candidate in contest['candidates']])
                min_value = min([min([issue[1] for issue in candidate['issues']]) for candidate in contest['candidates']])
                
                contest['max_issue_value'] = max_value
                contest['min_issue_value'] = min_value

        except ValueError:
            return f"{ address } is not in a known Seattle precinct."
        except RuntimeError:
            return f"Could not connect to MapBox, please try again later."
        if form.validate_on_submit():
            if form.Next:
                return redirect(url_for("create_user"))
        return render_template("candidate_info.html", address=address, precinct=precinct, highlights_election=highlights_election, total_election=total_election)

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
