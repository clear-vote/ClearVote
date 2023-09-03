import json
import datetime
from clearvote.utils.Judging.drafter import Drafter
from clearvote.utils.mapping.mapper import Mapper

def get_values(file_path, contest_type):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    for value_set in data:
        if value_set['contest_type'] == contest_type:
            return value_set["values"]

if __name__ == '__main__':
    

    # TODO: Create a basic front-end for all of this
    # TODO: Address input validation -> (eg. confirm the address is in the municipality SEATTLE and the state WA)
    # Page 1
    user_input = str(input("Enter your address: "))


    # TODO: "Are you registered to vote at your current address?"
    # Page 2
    file_path = 'clearvote/static/Data/CustomData/Wa_Seattle_Elections.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    election = data['elections'][0]
    print("There is an upcoming", election['election_type'], "election in your area")
    print("Register to vote by", datetime.datetime.fromtimestamp(election["registration_deadline"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("In person voting begins", datetime.datetime.fromtimestamp(election["voting_open"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("Ballots must be cast by", datetime.datetime.fromtimestamp(election["voting_close"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    
    # TODO: Add support for every candidate in every district in Seattle
    # Page 3
    print("Voting information for", user_input)
    Drafter.print_election_data(data)


    # TODO: This should prompt user for either their phone number or email or both and store their info in a DB
    # TODO: Setup election alerts
    # Page 4


    # TODO: Setup donations, contact info, "call to action" page
    # Page 5
