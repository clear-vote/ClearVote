class Drafter:
    """
    This class is responsible for drafting the values for each candidate in a given district
    Every candidate gets a unique value assigned to them with consideration of the following constraints:
    1. Drafts are assigned in rounds (no candidate can have more than 1 draft than anyone else with a non-empty value set)
    2. Values for each candidate are drafted in order of their most highly rated to most lowly rated
    3. If >1 candidate in a round shares the same highest rated value, the candidate with the highest rating gets it drafted to them

    In doing this, we are consciously preventing specific valuesets from standing out
    1. logistic valuesets; which I believe represents polarizing candidates who only focus on short-term, hot-button issues
    2. flat valuesets; which I believe represents people who are just trying to appease as many voters as possible
    We are also elevating other valuesets that I believe represents more nuanced and balanced leadership
    3. logit valuesets; which I believe represents candidates who aknowledge a wide body of issuesm but stress a few particularily important ones
    4. linear valuesets; which I believe represent candidates with a clear heirarchy of what is important to them, but are thoughtful on lower priority topics

    """
    pass


    def _draft_values(candidate_set):
        """
        This is the drafting algorithm
        """
        drafted_values = {person['name']: [] for person in candidate_set}
        unassigned_values = set()

        for candidate in candidate_set:
            candidate['values'] = sorted(candidate['values'], key=lambda x: x[1], reverse=True)
            unassigned_values.update([value for value, _ in candidate['values']])

        while unassigned_values:
            # Find the people who have the least number of picks but still have preferences
            candidates = [candidate for candidate in candidate_set if candidate['values']]
            if not candidates:
                break

            min_picked = min(len(drafted_values[candidate['name']]) for candidate in candidates)
            next_pickers = [candidate for candidate in candidates if len(drafted_values[candidate['name']]) == min_picked]

            max_rating = -1
            next_value = None
            next_picker = None

            for candidate in next_pickers:
                top_value, top_rating = candidate['values'][0]
                if top_rating > max_rating:
                    max_rating = top_rating
                    next_value = top_value
                    next_picker = candidate

            drafted_values[next_picker['name']].append(next_value)
            unassigned_values.remove(next_value)

            for candidate in candidate_set:
                candidate['values'] = [(value, rating) for value, rating in candidate['values'] if value != next_value]

        return drafted_values

    def _filter_values(candidates, min_rating, max_index):
        """
        This function filters the values for each candidate based on the minimum rating and maximum index
        """
        for candidate in candidates:
            # Filter based on the minimum rating
            candidate['values'] = [(value, rating) for value, rating in candidate['values'] if rating >= min_rating]
            
            # Cut off based on the maximum index
            candidate['values'] = candidate['values'][:max_index]

    # TODO: this function should randomize the values a small amount, to prevent ties from occuring in the algorithm
    def _randomize_values(candidates):
        pass

    # TODO: This function should calibrate the data so that the sum of all values in the entire dataset is 256
    def _calibrate_values(candidates):
        pass

    # TODO: This function should automatically calculate how much of a valueset should be cutoff, given the number of candidates and number of values
    def _calculate_cutoffs(candidates):
        # This can be adjusted so that lower ranked issues in a value set are allowed to "pass"
        AVG_NUM_SHOWN_VALUES = 2
        # This can be adjusted so that lower rated issues in a value set are allowed to "pass"
        NUM_TOTAL_VALUE_POINTS = 10
        return NUM_TOTAL_VALUE_POINTS, AVG_NUM_SHOWN_VALUES

    def print_election_data(election_data):
        # Constants for filtering

        # Extract the data and apply the draft_values function to each district
        for election in election_data["elections"]:
            for contest in election["contests"]:
                for district in contest["districts"]:
                    candidates = district["candidates"]
                    
                    for candidate in candidates:
                        candidate['values'] = [(k, v) for k, v in candidate['values']]
                    
                    min_rating, max_index = Drafter._calculate_cutoffs(candidates)

                    # Apply the filters
                    Drafter._filter_values(candidates, (min_rating / len(candidates[0]['values'])), (len(candidates) * max_index))

                    # Apply the draft
                    result = Drafter._draft_values(candidates)
                    
                    print(contest['contest_type'], f"District {district['district_number']}")
                    for name, values in result.items():
                        print(f"  {name}:")
                        for value in values:
                            print(f"    - {value}")