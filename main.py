import json
import datetime

class Candidate:
    def __init__(self, first_name, last_name, sentiments):
        self.first_name = first_name
        self.last_name = last_name
        self.sentiments = sentiments

class District:
    def __init__(self, jurisdiction_name, jurisdiction, candidates):
        self.jurisdiction_name = jurisdiction_name
        self.jurisdiction = jurisdiction
        self.candidates = candidates

class Election:
    def __init__(self, election_type, registration_deadline, voting_open, voting_close, districts):
        self.election_type = election_type
        self.registration_deadline = registration_deadline
        self.voting_open = voting_open
        self.voting_close = voting_close
        self.districts = districts

class Zone:
    def __init__(self, id, elections):
        self.id = id
        self.elections = elections

def load_zones_from_json(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    zones = []
    for zone_data in data:
        elections = []
        for election_data in zone_data["elections"]:
            districts = [District(d["jurisdiction_name"], d["jurisdiction"],
                                 [Candidate(c["first_name"], c["last_name"], c["sentiments"]) for c in d["candidates"]])
                         for d in election_data["districts"]]
            elections.append(Election(election_data["election_type"], election_data["registration_deadline"],
                                      election_data["voting_open"], election_data["voting_close"], districts))
        zones.append(Zone(zone_data["id"], elections))
    return zones

if __name__ == '__main__':
    zones = load_zones_from_json('zones.json')
    election = zones[0].elections[0]

    # Print the date in a full format (for example, "Monday, 20 August 2023, 12:00 PM")
    print("Voting information for zone", zones[0].id)
    print("This is a", election.election_type, "election")
    print("Register to vote by", datetime.datetime.fromtimestamp(election.registration_deadline).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("In person voting begins", datetime.datetime.fromtimestamp(election.voting_open).strftime('%A, %d %B %Y, at %I:%M %p'))
    print("Ballots must be cast by", datetime.datetime.fromtimestamp(election.voting_close).strftime('%A, %d %B %Y, at %I:%M %p'))

    # Display sentiments for all candidates in the first zone and its first election as an example
    for district in zones[0].elections[0].districts:
        print(f"{'    '}", district.jurisdiction_name)
        for candidate in district.candidates:
            print(f"{'         '}", candidate.first_name, candidate.last_name)
            for sentiment, rank in candidate.sentiments.items():
                if rank == 1:
                    print(f"{'              '}", sentiment)

'''
def get_random_addresses(file_path, postcode, sample_size=3):
    # Store elements that match the desired postcode
    matching_addresses = []

    # Read the file line by line and parse the JSON
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            if data["properties"]["postcode"] == postcode:
                matching_addresses.append(data)

    # If there are fewer matching addresses than sample_size, adjust the sample_size
    sample_size = min(sample_size, len(matching_addresses))

    # Get a random sample from the list of matching addresses
    return random.sample(matching_addresses, sample_size)

    
addresses = get_random_addresses('source.geojson', '98105', 3)
    for address in addresses:
        print(address)

        
1. Calculate the most popular districts in 3 zips to create a composite zone. *Record how this is done*
3. Hardcode the candidates belonging to the zone’s district_id. *Record how the candidates are found*
4. Determine the [[political value metrics]] that will be used in sentiment analysis for the following district_types
5. Hardcode a ranked, ChatGPT-determined sentiment analysis. *Record how this analysis is performed*
6. For each candidate, have it calculate their top three *unique* political stances and *record how this calculation is performed*
7. Option to continue on to the next page
'''