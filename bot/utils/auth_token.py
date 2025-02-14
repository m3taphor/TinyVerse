import json
import os
from datetime import datetime
from bot.utils import TOKENS_PATH

def append_token(name, auth):
    if not os.path.exists(TOKENS_PATH):
        with open(TOKENS_PATH, 'w') as f:
            json.dump([], f)

    with open(TOKENS_PATH, 'r') as f:
        try:
            tokens_data = json.load(f)
        except json.JSONDecodeError:
            tokens_data = []

    name_exists = False

    for entry in tokens_data:
        if 'name' in entry and entry['name'] == name:
            entry['token'] = auth
            entry['createdOn'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            name_exists = True
            break

    if not name_exists:
        new_entry = {
            "name": name,
            "token": auth,
            "createdOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tokens_data.append(new_entry)

    with open(TOKENS_PATH, 'w') as f:
        json.dump(tokens_data, f, indent=4)

    return True

def get_token(name):
    if not os.path.exists(TOKENS_PATH):
        with open(TOKENS_PATH, 'w') as f:
            json.dump([], f)
        return None
    
    with open(TOKENS_PATH, 'r') as f:
        try:
            tokens_data = json.load(f)
        except json.JSONDecodeError:
            return None
    
    for entry in tokens_data:
        if 'name' in entry and entry['name'] == name:
            if 'token' in entry and entry['token'] != "":
                return entry['token']
            
    return None