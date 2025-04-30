import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'countries.json')

current_voting_country_id = None

def load_countries():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            countries = json.load(f)
            return countries
    except FileNotFoundError:
        return []

def get_country_by_id(country_id):
    countries = load_countries()
    for country in countries:
        if country["id"] == country_id:
            return country
    return None

def set_current_voting_country(country_id):
    global current_voting_country_id
    if get_country_by_id(country_id):
        current_voting_country_id = country_id
        return True
    return False

def get_current_voting_country():
    return get_country_by_id(current_voting_country_id) if current_voting_country_id else None
