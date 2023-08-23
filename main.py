import json
import datetime

from Mapping.mapper import Mapper

if __name__ == '__main__':
    
    # TODO: Create a basic front-end for all of this
    # TODO: Address input validation -> (eg. confirm the address is in the municipality SEATTLE and the state WA)
    # Page 1
    user_input = str(input("Enter your address: "))

    # TODO: "Are you registered to vote at your current address?"
    # Page 2
    file_path = 'CustomData/Wa_Seattle_Elections.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    election = data['elections'][0]
    print("There is an upcoming", election['election_type'], "election in your area")
    print("Register to vote by", datetime.datetime.fromtimestamp(election["registration_deadline"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("In person voting begins", datetime.datetime.fromtimestamp(election["voting_open"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("Ballots must be cast by", datetime.datetime.fromtimestamp(election["voting_close"]).strftime('%A, %d %B %Y, at %I:%M %p'))
    
    # TODO: Create a valueset to pull from so each candidate is drafted unique values
    # TODO: Add support for city council districts 1, 3, 5, 6, 7
    # TODO: Add support for Port Commisioner and School District Director
    # Page 3
    print("Voting information for", user_input)
    precinct = Mapper.get_precinct(user_input)
    council_number = int(precinct.get_seattle_council_dist())
    for contest in election['contests']:
        if contest['contest_type'] == "City Council":
            for district in contest['districts']:
                if district['district_number'] == council_number:
                    for candidate in district['candidates']:
                        print(f"{'    '}", candidate['first_name'], candidate['last_name'])
                        for value in candidate['values'][:3]:
                            print(f"{'       - '}", value['value'], ":", value['rating'])

    # TODO: This should prompt user for either their phone number or email or both and store their info in a DB
    # TODO: Setup election alerts
    # Page 4

    # TODO: Setup donations, contact info, "call to action" page
    # Page 5