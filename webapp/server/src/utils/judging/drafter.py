import json
import os
import random
import numpy as np
import copy

class Drafter:
    """
    This class is responsible for drafting the issues for each candidate in a given district
    """
    pass

    CUTOFF = 0.01

    # This function extracts the last election data and recompiles only what is relevant for the user
    @staticmethod
    def _extract_election_data_for_precinct(json_data, position_dict):
        rearranged_data = []
        
        # Get the last election
        last_election = json_data['elections'][-1]
        
        # Loop through contests
        for contest in last_election['contests']:
            contest_type = contest['contest_type']
            
            # Check if this contest type is in the position_dict
            if contest_type in position_dict:
                target_position_number = position_dict[contest_type]
                
                # Loop through districts
                for district in contest['districts']:
                    pos_num = district['position_number']
                    
                    # Check if position number matches
                    if pos_num == target_position_number:
                        new_contest_data = {
                            "contest_type": contest_type,
                            "position_number": pos_num,
                            "candidates": district['candidates']
                        }
                        rearranged_data.append(new_contest_data)
              
        return rearranged_data

    # This is the drafting function. Definetly needs to be cleaned up
    @staticmethod
    def draft(precinct, json_data):
        city = precinct['city_name']
        if city != 'Seattle':
            raise AttributeError(f"Precinct { precinct } is not in Seattle")
                
        position_dict = {
            "city_council": int(precinct['seattle_city_council_districts_name'][-1]),
            "school_district_director": int(precinct['seattle_school_board_director_districts_name'][-1]),
            "port_commissioner": 5,
        }

        precinct_data = Drafter._extract_election_data_for_precinct(json_data, position_dict)
        
        # The dataset into contests for easier processing by the drafting algo
        def process_contest_types(precinct_data):
            drafted_data = copy.deepcopy(precinct_data)
            for contest in drafted_data:
                contest['candidates'] = draft_candidates(contest)
            return drafted_data
        
        # This is the drafting algo
        def draft_candidates(contest):
            issues_and_scores = copy.deepcopy(contest['candidates'])
            drafted_issues = [{**candidate, 'issues': [], 'num_issues': 0} for candidate in contest['candidates']]

            while len(issues_and_scores[0]['issues']) > 0:
                highest_rating = 0
                highest_issue_candidate = None
                highest_issue_name = None
                
                # Find the minimum number of issues that have been assigned to a candidate so far
                min_issues_assigned = min(candidate['num_issues'] for candidate in drafted_issues)

                for candidate in issues_and_scores:
                    if candidate['issues']:  # Only consider candidates that have issues left
                        draft_candidate = next(dc for dc in drafted_issues if dc['name'] == candidate['name'])
                        # Skip this candidate if they already have more issues than the current minimum
                        if draft_candidate['num_issues'] > min_issues_assigned:
                            continue

                        max_issue_rating = max(candidate['issues'], key=lambda x: x[1])[1]
                        if max_issue_rating > highest_rating:
                            highest_rating = max_issue_rating
                            highest_issue_candidate = candidate
                            highest_issue_name = [issue[0] for issue in candidate['issues'] if issue[1] == highest_rating]

                if highest_issue_candidate is None:  # No eligible candidates
                    break

                selected_issue = random.choice(highest_issue_name)

                for draft_candidate in drafted_issues:
                    if draft_candidate['name'] == highest_issue_candidate['name']:
                        draft_candidate['issues'].append([selected_issue, highest_rating])
                        draft_candidate['num_issues'] += 1  # Increment the number of issues for this candidate
                        break

                for candidate in issues_and_scores:
                    candidate['issues'] = [issue for issue in candidate['issues'] if issue[0] != selected_issue]

            return drafted_issues

        drafted_data = process_contest_types(precinct_data)
        return drafted_data
    
    # This function just sorts all the
    @staticmethod
    def get_contest_data(precinct, json_data):
        
        position_dict = {
            "city_council": int(precinct['seattle_city_council_districts_name'][-1]),
            "school_district_director": int(precinct['seattle_school_board_director_districts_name'][-1]),
            "port_commissioner": 5,
        }

        precinct_data = Drafter._extract_election_data_for_precinct(json_data, position_dict)
        for contest in precinct_data:
            for candidate in contest['candidates']:
                candidate['issues'] = sorted(candidate['issues'], key=lambda x: x[1], reverse=True)
                candidate['issues'] = [(issue_name, issue_value) for issue_name, issue_value in candidate['issues'] if issue_value >= Drafter.CUTOFF]

        return precinct_data