import json
import datetime

def unix_convert(unix: int):
    date_time = datetime.datetime.fromtimestamp(unix)

    return date_time.strftime('%b %d, %Y')

def stars_count(current_dust, current_stars):
    per_star = current_stars / 70
    calc_stars = int(current_dust / per_star)
    return calc_stars - (calc_stars % 10)

def load_data(filePath):
    with open(filePath, 'r', encoding='utf8') as file:
        return json.load(file)

def save_data(filePath, data):
    with open(filePath, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=4)

def getGiftCode(username):
    data = load_data('gift-codes.json')
    return [entry['code'] for entry in data[0]['generatedCodes'] if entry['forUser'] == username]
    
def newGiftCode(code, username, amount):
    try:
        data = load_data('gift-codes.json')
        new_entry = {
            "code": code,
            "amount": amount,
            "forUser": username,
            "link": "https://t.me/tverse?startapp=gift-" + code
        }
        data[0]['generatedCodes'].append(new_entry)
        save_data('gift-codes.json', data)
        return True
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    
def errorGiftCode(code, type_):
    data = load_data('gift-codes.json')
    for i, entry in enumerate(data[0]['generatedCodes']):
        if entry['code'] == code:
            if type_ == "incorrect":
                data[0]['incorrectCodes'].append(entry)
            elif type_ == "used":
                data[0]['usedCodes'].append(entry)
            else:
                return None
            
            del data[0]['generatedCodes'][i]
            break
    else:
        return None
    
    save_data('gift-codes.json', data)