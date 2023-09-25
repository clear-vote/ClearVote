import re
import warnings
import os
import openai
import json
import time
from datetime import datetime

'''
gpt-3.5 turbo (not good enough): $0.18 per run for about 3 minutes, sometimes it just makes shit up
gpt-4: $0.40 for about 9 minutes
TODO: test for bad datasets and implement the ability to manually recorrect
'''
class GPT:
    # this will assign the candidate a pvm rating in json format
    # given the correct pvm set and the candidates statement
    @staticmethod
    def fetch_rating_for_candidate(candidate_statement, gpt_model, political_value_metric_set, rating_type):
        start_time = time.time()  # Start timer
        
        political_value_metric_string = ""
        for pvm in political_value_metric_set:
            political_value_metric_string += pvm[0] + ": " + pvm[1] + "\n"
        
        system_prompt = "The following is a list of categories you will judge the user input on:\n\n"
        system_prompt += political_value_metric_string
        if rating_type == "score":
            system_prompt += '''\n\nThe output should be an array of tuples in JSON format.
            For each tuple, index[0] contains the category as a string, and index[1] should be your score of how well 
            the user input addresses that category. This score can be from 0 to 100 
            Consider both the positive and negative implications of the provided information when evaluating them, 
            with special consideration of their background, education, and past actions.'''
        elif rating_type == "ranking":
            system_prompt += '''\n\nThe output should be an array of tuples in JSON format. 
            For each tuple, index[0] contains the category as a string, and index[1] should be your ranking of it
            from 1 (best) to n (worst), of how well the user input addresses that category.
            Consider both the positive and negative implications of the provided information when evaluating them, 
            with special consideration of their background, education, and past actions.'''
        else:
            print("Invalid rating type. Neither 'score' or 'ranking'")
            return None

        openai.api_key = os.environ.get("OPENAI_API_KEY")

        while True:  # Add a loop to keep trying the API call until it succeeds
            try:
                print("...")
                response = openai.ChatCompletion.create(
                    model=gpt_model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": candidate_statement
                        }
                    ],
                    temperature=0,
                    max_tokens=500,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                break  # If the API call is successful, break out of the loop
            except openai.error.RateLimitError:  # Catch the rate limit error
                print(f"        Rate limit reached. Waiting for 30 seconds before retrying...")
                time.sleep(30)  # Wait for 30 seconds
        
        end_time = time.time()  # End timer
        duration_seconds = end_time - start_time
        print(f"        duration seconds: {duration_seconds}")
        
        # this isolates the bit we want, openAI sends back a bunch of useless stuff
        return json.loads(response['choices'][0]['message']['content'])
    
    @staticmethod
    def iterate_contests_and_candidates(candidate_data_set, gpt_model, political_value_metric_set, rating_type):
        result = []
        for contest in sorted(os.listdir(candidate_data_set)):
            if '.DS_Store' in contest:
                print(contest, "contest failed")
                continue
            contest_type = GPT._get_contest_type(contest)
            political_value_metric_set = GPT._get_political_value_metric_set(contest_type)
            print("contest type:", contest_type)
            result.append({"contest_type": contest_type, "districts": []})
            contest_path = os.path.join(candidate_data_set, contest)
            
            for district in sorted(os.listdir(contest_path)):
                if '.DS_Store' in district:
                    print("district failed")
                    continue
                current_contest = len(result) - 1
                position_number = GPT._get_position_number(district)
                print(f"  position number:", position_number)
                result[current_contest]["districts"].append({"position_number": position_number, "candidates": []})
                district_path = os.path.join(contest_path, district)
                
                for candidate in sorted(os.listdir(district_path)):
                    if '.DS_Store' in candidate:  # Only process .json files
                        print("candidate failed")
                        continue
                    
                    current_district = len(result[current_contest]["districts"]) - 1
                    candidate_path = os.path.join(district_path, candidate)
                    with open(candidate_path, 'r') as f:
                        candidate_statement = f.read()
                    print(f"    fetching political value metrics for", candidate)
                    
                    # Sometimes it doesn't work, so we give it 3 attempts
                    attempt = 0
                    while attempt < 3:
                        try:
                            issues = GPT.fetch_rating_for_candidate(candidate_statement, gpt_model, political_value_metric_set, rating_type)
                            candidate_name = os.path.splitext(candidate)[0]
                            result[current_contest]["districts"][current_district]["candidates"].append({"name": candidate_name, "issues": issues})
                            break
                        except json.JSONDecodeError:
                            print(f"    Failed to decode JSON for", candidate)
                            attempt += 1
        
        return result


    # Tries to find the contest type from the subdirectory's name
    @staticmethod
    def _get_contest_type(contest):
        if "city" in contest.lower():
            return "city_council"
        elif "port" in contest.lower():
            return "port_commissioner"
        elif "school" in contest.lower():
            return "school_district_director"
        else:
            warnings.warn("Keyword not found, returning 'position_not_found'")
            return "position_not_found"


    # Tries to get the position number from the subdirectories number
    @staticmethod
    def _get_position_number(district):
        numbers = re.findall(r'\d+', district)
        
        # If no numbers are found, return None
        if not numbers:
            warnings.warn("No number found in the input string")
            return None
        
        # Return the last number found in the string
        return int(numbers[-1])
    

    # Given a contest type, this returns the matching political value metric set 
    @staticmethod
    def _get_political_value_metric_set(contest_type):
        with open('preprocessing/political_value_metric_sets/political_value_metrics_1.0.json', 'r') as f:
            pvm_data = json.load(f)
        for pvm_set in pvm_data:
            if pvm_set['contest_type'] == contest_type:
                return pvm_set['issues']
        warnings.warn(f"No issues found for contest_type: {contest_type}")
        return None
    

    # This will generate a composite json file wit math
    @staticmethod
    def generate_composite_json(scores, rankings):
        # Ensure both JSONs have the same structure (you can add more validations)
        assert scores["municipality"] == rankings["municipality"]
        assert scores["state"] == rankings["state"]
        assert len(scores["elections"]) == len(rankings["elections"])

        result = {
            "municipality": scores["municipality"],
            "state": scores["state"],
            "elections": []
        }

        for score_election, rank_election in zip(scores["elections"], rankings["elections"]):
            combined_election = {
                "election_type": score_election["election_type"],
                "registration_deadline": score_election["registration_deadline"],
                "voting_open": score_election["voting_open"],
                "voting_close": score_election["voting_close"],
                "contests": []
            }

            for score_contest, rank_contest in zip(score_election["contests"], rank_election["contests"]):
                combined_contest = {
                    "contest_type": score_contest["contest_type"],
                    "districts": []
                }

                for score_district, rank_district in zip(score_contest["districts"], rank_contest["districts"]):
                    combined_district = {
                        "position_number": score_district["position_number"],
                        "candidates": []
                    }

                    for score_candidate, rank_candidate in zip(score_district["candidates"], rank_district["candidates"]):
                        combined_candidate = {
                            "name": score_candidate["name"],
                            "issues": {}
                        }

                        score_issues_dict = dict(score_candidate["issues"])
                        rank_issues_dict = dict(rank_candidate["issues"])

                        issues = GPT.calculate_composites(score_issues_dict, rank_issues_dict)
                        total_sum = sum(issues.values())
                        scaled_issues = {key: round((value / total_sum) * 100, 2) for key, value in issues.items()}

                        combined_candidate["issues"] = scaled_issues
                        combined_district["candidates"].append(combined_candidate)

                    combined_contest["districts"].append(combined_district)

                combined_election["contests"].append(combined_contest)

            result["elections"].append(combined_election)

        return result


    def calculate_composites(score_issues_dict, rank_issues_dict):
        # Sort based on rank
        rank_low_to_high = sorted(rank_issues_dict.items(), key=lambda x: x[1])
        new_rank_issues_dict = {k: i+1 for i, (k, v) in enumerate(rank_low_to_high)}
        
        return GPT.calculate_composites_recurse(score_issues_dict, new_rank_issues_dict, {})


    def calculate_composites_recurse(score_issues_dict, rank_issues_dict, composite_dict):
        # Base case: if rank_issues_dict is empty, we're done
        if not rank_issues_dict:
            return composite_dict
        
        # Get the next issue to process (the one with the lowest rank)
        issue, rank = min(rank_issues_dict.items(), key=lambda x: x[1])
        
        # Calculate its composite score
        composite_score = score_issues_dict[issue]
        last_issue, last_composite_score = None, None
        
        # If there are already processed issues in composite_dict, get the last one
        if composite_dict:
            last_issue = max(composite_dict, key=composite_dict.get)
            last_composite_score = composite_dict[last_issue]
        
        # If the current composite score is lower than the previous, adjust them
        if last_issue and composite_score < last_composite_score:
            avg = (composite_score + last_composite_score) / 2
            composite_dict[issue] = avg + 0.5
            composite_dict[last_issue] = avg - 0.5
        else:
            composite_dict[issue] = composite_score
        
        # Remove the current issue from rank_issues_dict as it's processed
        del rank_issues_dict[issue]
        
        return GPT.calculate_composites_recurse(score_issues_dict, rank_issues_dict, composite_dict)


    # This calls the political value metric set
    @staticmethod
    def generate_new_pvm_dataset(candidate_data_set, generate_ranking_and_score_files, political_value_metric_set="/preprocessing/poltical_value_metric_sets/political_value_metrics_1.0.json",
                                 municipality="Seattle", state="WA", election_type="Primary", registration_deadline="1690243199", voting_open="1690588800",
                                 voting_close="1690945200", gpt_model="gpt-4"):
        # rankings_json = GPT.iterate_contests_and_candidates(candidate_data_set,
        #                                                     gpt_model,
        #                                                     political_value_metric_set,
        #                                                     "ranking")
        
        # rankings = { "municipality": municipality, 
        #              "state": state,
        #              "elections": [
        #                 { "election_type": election_type,
        #                   "registration_deadline": registration_deadline,
        #                   "voting_open": voting_open,
        #                   "voting_close": voting_close,
        #                   "contests": rankings_json }]}
        
        date_obj = datetime.fromtimestamp(int(voting_open))
        # if generate_ranking_and_score_files:
        #     ranking_file_name = os.path.join('preprocessing', 'election_datasets', 'ranked', date_obj.strftime("%m-%d-%y") + '_rankings.json')
        #     with open(ranking_file_name, 'w') as f:
        #         json.dump(rankings, f, indent=4)
        
        scores_json = GPT.iterate_contests_and_candidates(candidate_data_set,
                                                          gpt_model,
                                                          political_value_metric_set,
                                                          "score")
        scores = { "municipality": municipality, 
                   "state": state,
                   "elections": [
                        { "election_type": election_type,
                          "registration_deadline": registration_deadline,
                          "voting_open": voting_open,
                          "voting_close": voting_close,
                          "contests": scores_json}]}
       
        if generate_ranking_and_score_files:
            score_file_name = os.path.join('preprocessing', 'election_datasets', 'scored', date_obj.strftime("%m-%d-%y") + '_scores.json')
            with open(score_file_name, 'w') as f:
                json.dump(scores, f, indent=4)

        # composite_json = GPT.generate_composite_json(scores, rankings)
        
        # composite_file_name = os.path.join('preprocessing', 'election_datasets', 'composite', 'wa_seattle_composite.json')
        # with open(composite_file_name, 'w') as f:
        #     json.dump(composite_json, f, indent=4)