import json
import datetime
from bot.config import settings

min_value, max_value, vmax = 100, 10000, 1000
multipliers = {400: 0.1, 500: 0.15, 550: 0.2, 600: 0.25, 650: 0.35, 700: 0.45, 750: 0.55, 800: 0.65, 1000: 1}

def calculate_amount(value):
    multiplier = next((m for t, m in sorted(multipliers.items()) if value <= t), 1)
    return round(min_value + (max_value - min_value) * multiplier * (value / vmax))

def slider_amount(amount):
    closest_amount, previous_amount, min_diff = calculate_amount(0), None, float('inf')
    for value in range(vmax + 1):
        calculated_amount = calculate_amount(value)
        diff = abs(amount - calculated_amount)
        if diff < min_diff:
            previous_amount, min_diff, closest_amount = closest_amount, diff, calculated_amount
    return previous_amount

def stars_count(current_dust, current_stars):
    per_star = current_stars / 70
    calc_stars = int(current_dust / per_star)
    
    if settings.SLIDER_STARS_VALUE:
        pre = slider_amount(calc_stars)
        if pre >= 100:
            return pre
        
    return calc_stars

def unix_convert(unix: int):
    date_time = datetime.datetime.fromtimestamp(unix)

    return date_time.strftime('%b %d, %Y')

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