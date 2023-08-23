import json
import datetime

from Mapping.mapper import Mapper

class Candidate:
    def __init__(self,
                 first_name,
                 last_name,
                 values):
        self.first_name = first_name
        self.last_name = last_name
        self.values = values

class District:
    def __init__(self,
                 district_number,
                 candidates):
        self.district_number = district_number
        self.candidates = candidates

class Contest:
    def __init__(self,
                 contest_type,
                 districts):
        self.contest_type = contest_type
        self.districts = districts

class Election:
    def __init__(self,
                 election_type,
                 registration_deadline,
                 voting_open,
                 voting_close,
                 contests):
        self.election_type = election_type
        self.registration_deadline = registration_deadline
        self.voting_open = voting_open
        self.voting_close = voting_close
        self.contests = contests

class Jurisdiction:
    def __init__(self,
                 municipality,
                 state,
                 elections):
        self.municipality = municipality
        self.state = state
        self.elections = elections

def load_json(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    elections = []
    for election in data['elections']:
        contests = []
        for contest in election["contests"]:
            districts = []
            for district in contest["districts"]:
                candidates = []
                for candidate in district["candidates"]:
                    candidates.append(Candidate(candidate["first_name"], candidate["last_name"], candidate["values"]))
                districts.append(District(district["district_number"], candidates))
            contests.append(Contest(contest["contest_type"], districts))
        elections.append(Election(election["election_type"], election["registration_deadline"], election["voting_open"], election["voting_close"], contests))
    return Jurisdiction(data["municipality"], data["state"], elections)

if __name__ == '__main__':
    
    # "University of Washington" (district 4)
    # "3801 Beacon Ave S, Seattle" (district 2)
    user_input = str(input("Enter your address: "))
    
    elections_data = load_json('Data/SeattleWA_Elections.json')
    print("Voting information for", user_input)

    election = elections_data.elections[0]
    print("This is a", election.election_type, "election")
    print("Register to vote by", datetime.datetime.fromtimestamp(election.registration_deadline).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("In person voting begins", datetime.datetime.fromtimestamp(election.voting_open).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("Ballots must be cast by", datetime.datetime.fromtimestamp(election.voting_close).strftime('%A, %d %B %Y, at %I:%M %p'))

    precinct = Mapper.get_precinct(user_input)
    council_number = int(precinct.get_seattle_council_dist())

    # Displays all the city council candidates under the given address
    for contest in election.contests:
        if contest.contest_type == "City Council":
            for district in contest.districts:
                if district.district_number == council_number:
                    for candidate in district.candidates:
                        print(f"{'     '}", candidate.first_name, candidate.last_name)
                        for v in candidate.values[:3]:
                            print(f"{'          '}", v['value'])
