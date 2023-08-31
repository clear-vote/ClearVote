import requests
import os
import openai

class Analyzer:
    def compile_statements():
        pass
    def get_value_metric_ratings():
        pass
    def get_candidate_statement():
        pass
    def fetch_pvms_from_statement(file_name, gpt_model, political_value_metric_set, candidate_statement):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
        model=gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": """Whatever the user gives you, you will numerically rate from 1 to 127 for each of the following categories: 
                    \n\n{political_value_metric_set}\n\nThe output should be in JSON format.\nThe 1st value should be “name”: “{the candidate’s name}”.
                    \nThe 2nd value should be \"website\": \"{the candidate's website, if found, otherwise blank}\"\nThe 3rd value should be “values”, 
                    and equal an array of tuples where for each tuple, index 0 contains the one-word category as a string and index 1 contains the rating 
                    for it. Consider both the positive and negative implications of the provided information when evaluating them, 
                    with special consideration of their background, education, and past actions."""
                },
                {
                    "role": "user",
                    "content": candidate_statement
                }
            ],
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        if response.status_code == 200:
            print('Successfully sent data to API.')
            print('API Response:', response.json())
        else:
            print(f'Failed to send data to API. Status code: {response.status_code}')
            print('API Response:', response.json())

    def load_election_metrics():
        pass