#
#  util.py
#
import os
import json


def get_settings():
    if not os.path.isfile("settings.json"):
        initial_data = {
            "check_updates_on_start": True,
            "theme": "textual-dark",
            "theme_index": 0,
            "clock_enabled": True,
            "add_pronounciation_accents": True,
            "show_ipa": True,
            "formal_gorgus": False
        }
        with open("settings.json", "w") as file:
            json.dump(initial_data, file, indent=4)
        return initial_data
    else:
        with open("settings.json", "r") as file:
            return json.load(file)
        
def modify_json(file_path, key, value):
    # Open the file and load its current data
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Modify or add the key-value pair
    data[key] = value

    # Write the updated data back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)