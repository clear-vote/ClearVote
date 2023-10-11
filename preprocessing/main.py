import os
from gpt_prompting import GPT


def get_user_input():
    # Define the path to the directory
    directory_path = "preprocessing/candidate_data/wa/seattle"

    # List the contents of the directory
    directory_contents = [item for item in os.listdir(directory_path) if not item.startswith('.DS_Store')]

    # Print the contents
    for index, item in enumerate(directory_contents):
        print(f"{index + 1}. {item}")

    # Ask the user for their selection
    try:
        selection = int(input("What candidate dataset would you like to select?: "))

        # Check if the selection is valid
        if 1 <= selection <= len(directory_contents):
            candidate_data_set = directory_path + "/" + directory_contents[selection - 1]
            print(f"You selected: {candidate_data_set}")
        else:
            print("Invalid selection. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

    user_input = input("Would you like to generate the Ranking and Rating JSON files separately? (for quality control): ").strip().lower()
    generate_ranking_and_score_files = True if user_input in ["y", "yes", "true"] else False

    return candidate_data_set, generate_ranking_and_score_files


if __name__ == '__main__':
    # candidate_data_set, generate_ranking_and_score_files = get_user_input()
    # GPT.generate_new_pvm_dataset(candidate_data_set, generate_ranking_and_score_files)

    