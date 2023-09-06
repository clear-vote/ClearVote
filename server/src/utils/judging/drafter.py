from copy import deepcopy
import json
import math
import os
import random
import logging

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

    def _draft_issues(candidate_set):
        """
        This is the drafting algorithm
        """
        drafted_issues = {person['name']: [] for person in candidate_set}
        unassigned_issues = set()

        for candidate in candidate_set:
            candidate['issues'] = sorted(candidate['issues'], key=lambda x: x[1], reverse=True)
            unassigned_issues.update([value for value, _ in candidate['issues']])

        while unassigned_issues:
            # Find the people who have the least number of picks but still have preferences
            candidates = [candidate for candidate in candidate_set if candidate['issues']]
            if not candidates:
                break

            min_picked = min(len(drafted_issues[candidate['name']]) for candidate in candidates)
            next_pickers = [candidate for candidate in candidates if len(drafted_issues[candidate['name']]) == min_picked]

            max_rating = -1
            next_value = None
            next_picker = None

            for candidate in next_pickers:
                top_value, top_rating = candidate['issues'][0]
                if top_rating > max_rating:
                    max_rating = top_rating
                    next_value = top_value
                    next_picker = candidate

            drafted_issues[next_picker['name']].append(next_value)
            unassigned_issues.remove(next_value)

            for candidate in candidate_set:
                candidate['issues'] = [(value, rating) for value, rating in candidate['issues'] if value != next_value]

        return drafted_issues

    def _filter_issues(candidates, min_rating, max_index):
        """
        This function filters the issues for each candidate based on the minimum rating and maximum index
        """
        for candidate in candidates:
            # Filter based on the minimum rating
            candidate['issues'] = [(value, rating) for value, rating in candidate['issues'] if rating >= min_rating]

            # Cut off based on the maximum index
            candidate['issues'] = candidate['issues'][:max_index]

    # TODO: this function should randomize the issues a small amount, to prevent ties from occuring in the algorithm
    def _randomize_value(value):
        pass

    def _calibrate_issues(candidates):
        RATING_RANGE = 100
        for candidate in candidates:
            sum_ratings = 0
            for value in candidate['issues']:
                sum_ratings += value[1]
            scalar = RATING_RANGE / sum_ratings
            new_issues = []
            for value in candidate['issues']:
                new_issues.append((value[0], value[1] * scalar))
            candidate['issues'] = new_issues

    def _calculate_cutoffs(candidates):
        RATING_RANGE = 100
        MAX_SCALAR = 4
        num_issues = len(candidates[0]['issues'])
        num_candidates = len(candidates)
        scalar = math.floor(num_issues / num_candidates)
        if scalar > MAX_SCALAR:
            scalar = MAX_SCALAR
        return RATING_RANGE / num_issues + 0.05, math.floor(scalar * num_candidates * 0.5)

    # used in Flask
    def filter_contest_data(precinct):
        # This format MUST be followed for the server to be able to read it!!
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '..', 'preprocessing', 'compiled_election_datasets', 'wa_king', 'wa_seattle_elections.json')

        with open(file_path, 'r') as f:
            election_data = json.load(f)
        last_index = len(election_data['elections']) - 1 # will retrieve the most recently posted election
        filtered_election = {
            "election_type": election_data['elections'][last_index]['election_type'],
            "registration_deadline": election_data['elections'][last_index]['registration_deadline'],
            "voting_open": election_data['elections'][last_index]['voting_open'],
            "voting_close": election_data['elections'][last_index]['voting_close'],
            "contests": []
        }
        for contest in election_data['elections'][last_index]["contests"]:
            for district in contest["districts"]:
                if contest["contest_type"] == "city_council" and precinct.city_council_dist == district['position_number'] or contest["contest_type"] == "port_commissioner":
                    candidates = district["candidates"]
                    
                    for candidate in candidates:
                        candidate['issues'] = [(k, v) for k, v in candidate['issues']]
                    
                    min_rating, num_issues_to_show = Drafter._calculate_cutoffs(candidates)

                    # Apply the filters
                    Drafter._calibrate_issues(candidates)
                    # Drafter._randomize_issues(candidates)
                    Drafter._filter_issues(candidates, min_rating, num_issues_to_show)
                    # Apply the draft
                    # result = Drafter._draft_issues(candidates)

                    filtered_election['contests'].append({
                        "contest_type": contest['contest_type'],
                        "districts": [
                            {
                                "position_number": district['position_number'],
                                "candidates": candidates
                            }
                        ]
                    })
        return filtered_election

    def get_entire_contest():
        # This format MUST be followed for the server to be able to read it!!
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '..', 'preprocessing', 'compiled_election_datasets', 'wa_king', 'wa_seattle_elections.json')

        with open(file_path, 'r') as f:
            election_data = json.load(f)
        last_index = len(election_data['elections']) - 1 # will retrieve the most recently posted election
        return election_data['elections'][last_index]
    
    # used in main
    def print_contest_data(election, precinct):
        # Extract the data and apply the draft_issues function to each district
        for contest in election["contests"]:
            for district in contest["districts"]:
                if contest["contest_type"] == "city_council" and precinct.city_council_dist == district['position_number'] or contest["contest_type"] == "port_commissioner":
                    candidates = district["candidates"]
                    
                    for candidate in candidates:
                        candidate['issues'] = [(k, v) for k, v in candidate['issues']]
                    
                    min_rating, num_issues_to_show = Drafter._calculate_cutoffs(candidates)

                    # Apply the filters
                    Drafter._calibrate_issues(candidates)
                    # Drafter._randomize_issues(candidates)
                    Drafter._filter_issues(candidates, min_rating, num_issues_to_show)

                    # Apply the draft
                    result = Drafter._draft_issues(candidates)
                    
                    print(contest['contest_type'], f"position {district['position_number']}")
                    for name, issues in result.items():
                        print(f"  {name}:")
                        for value in issues:
                            print(f"    - {value}")
                    print("\n")