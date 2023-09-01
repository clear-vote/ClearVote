import re
import warnings
import os
import openai
import json

'''
gpt-3.5 turbo (not good enough): $0.18 per run for about 3 minutes, sometimes it just makes shit up
gpt-4: $0.40 for about 9 minutes
TODO: test for bad datasets and implement the ability to manually recorrect
'''
class Analyzer:
    @staticmethod
    def fetch_pvms_from_statement(gpt_model, political_value_metric_set, candidate_statement):
        
        political_value_metric_string = ""
        for pvm in political_value_metric_set:
            political_value_metric_string += pvm[0] + ": " + pvm[1] + "\n"
        
        system_prompt = "The following is a list of categories you will judge the user input on:\n\n"
        system_prompt += political_value_metric_string
        system_prompt += '''\n\nThe output should be an array of tuples in JSON format.
        For each tuple, index[0] contains the one-word category as a string, and index[1] should be your rating of how well 
        the user input addresses that category. This rating can be from 0 to 100, but DO NOT ASSIGN TWO NON-ZERO CATAGORIES TO THE SAME RATING. 
        Consider both the positive and negative implications of the provided information when evaluating them, 
        with special consideration of their background, education, and past actions.'''

        openai.api_key = os.environ.get("OPENAI_API_KEY")

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
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
        
        return json.loads(response['choices'][0]['message']['content'])
    
    @staticmethod
    def generate_political_value_metrics(source, gpt_model):
        result = []
        for contest in sorted(os.listdir(source)):
            contest_type = Analyzer._get_contest_type(contest)
            political_value_metric_set = Analyzer._get_political_value_metric_set(contest_type)
            print("contest type:", contest_type)
            result.append({"contest_type": contest_type, "districts": []})
            contest_path = os.path.join(source, contest)
            for district in sorted(os.listdir(contest_path)):
                current_contest = len(result) - 1
                position_number = Analyzer._get_position_number(district)
                print(f"  position number:", position_number)
                result[current_contest]["districts"].append({"position_number": position_number, "candidates": []})
                district_path = os.path.join(contest_path, district)
                for candidate in sorted(os.listdir(district_path)):
                    current_district = len(result[current_contest]["districts"]) - 1
                    candidate_path = os.path.join(district_path, candidate)
                    with open(candidate_path, 'r') as f:
                        candidate_statement = f.read()
                    print(f"    fetching political value metrics for", candidate)
                    values = Analyzer.fetch_pvms_from_statement(gpt_model, political_value_metric_set, candidate_statement)
                    candidate_name = os.path.splitext(candidate)[0]
                    result[current_contest]["districts"][current_district]["candidates"].append({"name": candidate_name, "values": values})
        return result
    
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

    @staticmethod
    def _get_position_number(district):
        numbers = re.findall(r'\d+', district)
        
        # If no numbers are found, return None
        if not numbers:
            warnings.warn("No number found in the input string")
            return None
        
        # Return the last number found in the string
        return int(numbers[-1])
    
    @staticmethod
    def _get_political_value_metric_set(contest_type):
        with open('CustomData/PoliticalValueMetrics.json', 'r') as f:
            pvm_data = json.load(f)
        for pvm_set in pvm_data:
            if pvm_set['contest_type'] == contest_type:
                return pvm_set['values']
        warnings.warn(f"No values found for contest_type: {contest_type}")
        return None
    
    # TODO: if new_file_name already exists, this should append to it, NOT overwrite it
    # TODO: this should be customizable in the future to handle any given municipality or county
    @staticmethod
    def generate_new_municipality(new_file_name="CustomData/Wa_Seattle_Elections.json",
                                  gpt_model='gpt-4',
                                  source="voter_pamphlet_data/stage4/"):
        source_json = Analyzer.generate_political_value_metrics(source, gpt_model)
        result = { "municipality": "Seattle", "state": "WA", "elections": [
                    { "election_type": "Primary", "registration_deadline": 1690243199, "voting_open": 1690588800, "voting_close": 1690945200, "contests": source_json}]}
        with open(new_file_name, 'w') as f:
            json.dump(result, f, indent=4)