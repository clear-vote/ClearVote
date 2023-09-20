from copy import deepcopy
import json
import math
import os
import random
import logging
import numpy as np
import pandas as pd
import copy

class Drafter:
    """
    This class is responsible for drafting the issues for each candidate in a given district
    Every candidate gets a unique value assigned to them with consideration of the following constraints:
    1. Drafts are assigned in rounds (no candidate can have more than 1 draft than anyone else with a non-empty value set)
    2. issues for each candidate are drafted in order of their most highly rated to most lowly rated
    3. If >1 candidate in a round shares the same highest rated value, the candidate with the highest rating gets it drafted to them

    In doing this, we are consciously preventing specific issuesets from standing out
    1. logistic issuesets; which I believe represents polarizing candidates who only focus on short-term, hot-button issues
    2. flat issuesets; which I believe represents people who are just trying to appease as many voters as possible
    We are also elevating other issuesets that I believe represents more nuanced and balanced leadership
    3. logit issuesets; which I believe represents candidates who aknowledge a wide body of issues but stress a few particularily important ones
    4. linear issuesets; which I believe represent candidates with a clear heirarchy of what is important to them, but are thoughtful on lower priority topics

    """
    pass

    # def _filter_issues(candidates, min_rating, max_index):
    #     """
    #     This function filters the issues for each candidate based on the minimum rating and maximum index
    #     """
    #     for candidate in candidates:
    #         # Filter based on the minimum rating
    #         candidate['issues'] = [(value, rating) for value, rating in candidate['issues'] if rating >= min_rating]

    #         # Cut off based on the maximum index
    #         candidate['issues'] = candidate['issues'][:max_index]

    # # TODO: this function should randomize the issues a small amount, to prevent ties from occuring in the algorithm
    # def _randomize_value(value):
    #     pass

    # def _calibrate_issues(candidates):
    #     RATING_RANGE = 100
    #     for candidate in candidates:
    #         sum_ratings = 0
    #         for value in candidate['issues']:
    #             sum_ratings += value[1]
    #         scalar = RATING_RANGE / sum_ratings
    #         new_issues = []
    #         for value in candidate['issues']:
    #             new_issues.append((value[0], value[1] * scalar))
    #         candidate['issues'] = new_issues

    # def _calculate_cutoffs(candidates):
    #     RATING_RANGE = 100
    #     MAX_SCALAR = 4
    #     num_issues = len(candidates[0]['issues'])
    #     num_candidates = len(candidates)
    #     scalar = math.floor(num_issues / num_candidates)
    #     if scalar > MAX_SCALAR:
    #         scalar = MAX_SCALAR
    #     return RATING_RANGE / num_issues + 0.05, math.floor(scalar * num_candidates * 0.5)

    # used in Flask
    def filter_contest_data(precinct):
        
        # This format MUST be followed for the server to be able to read it!!
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'composite_election_datasets', 'wa_king', 'wa_seattle_elections.json')
        
        with open(file_path, 'r') as f:
            json_data = json.load(f)

        def extract_last_election_data(json_data, position_dict):
            new_array = []
            
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
                            new_array.append(new_contest_data)
                            
            return new_array
        
        def process_contest_types(precinct_data):
            drafted_data = copy.deepcopy(precinct_data)
            for contest in drafted_data:
                contest['candidates'] = draft_candidates(contest)
            return drafted_data
                
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

            # for candidate in drafted_issues:
            #     name = candidate['name']
            #     issues = candidate['issues']

            #     df = pd.DataFrame(issues, columns=['Issue', 'Score'])
            #     print(f"Data for {name}:")
            #     print(df.to_string(index=False))
            #     print()

            return drafted_issues

        position_dict = {
            "city_council": precinct.get_city_council_dist(),
            "port_commissioner": 5,
        }

        precinct_data = extract_last_election_data(json_data, position_dict)

        drafted_data = process_contest_types(precinct_data)
        return drafted_data