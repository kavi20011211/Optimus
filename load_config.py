import json


def load_json_data():
    try:
        with open('setup.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Error: The file 'data.json' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from the file. Details: {e}")
