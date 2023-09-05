import json
import datetime
from judging.drafter import Drafter

from mapping.mapper import Mapper

def get_values(file_path, contest_type):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    for value_set in data:
        if value_set['contest_type'] == contest_type:
            return value_set["values"]

if __name__ == '__main__':
    
    # TODO: STRETCH Address input validation -> (eg. confirm the address is in the municipality SEATTLE and the state WA)
    # Page 1
    user_input = str(input("Enter your address: "))

    # TODO: "Are you registered to vote at your current address?"
    # Page 2
    file_path = 'CustomData/Wa_Seattle_Elections.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # This will always pull the most recent election, subsequent elections added to back of the list
    election = data['elections'][0]
    print("There is an upcoming", election['election_type'], "election in your area")
    print("Register to vote by", datetime.datetime.fromtimestamp(election["registration_deadline"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("In person voting begins", datetime.datetime.fromtimestamp(election["voting_open"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("Ballots must be cast by", datetime.datetime.fromtimestamp(election["voting_close"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    
    # TODO: migrate json to firebase
    # TODO: Isolate specific datapoints per address and randomize them, hide api key, commit and push

    # Page 3
    precinct = Mapper.get_precinct(user_input)
    print("Voting information for", user_input, "\n", precinct, "\n")
    Drafter.print_contest_data(election, precinct)

    # TODO: This should prompt user for either their phone number or email or both and store their info in a DB
    # TODO: Setup election alerts
    # Page 4


    # TODO: Setup donations, contact info, "call to action" page
    # Page 5