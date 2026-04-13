import json
import os


def load_json_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'setup.json')

        with open(config_path, 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"setup.json not found at {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in setup.json: {e}")
