import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'votes.json')

def get_all_votes():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_votes(votes):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=4)

def add_vote(user_id, country_id, vote_value):
    votes = get_all_votes()

    # Cherche si ce vote existe déjà pour user + pays
    for v in votes:
        if v["user_id"] == user_id and v["country_id"] == country_id:
            v["vote"] = vote_value
            break
    else:
        votes.append({
            "user_id": user_id,
            "country_id": country_id,
            "vote": vote_value
        })

    save_votes(votes)

def get_one_vote(user_id, country_id):
    votes = get_all_votes()
    for v in votes:
        if v["user_id"] == user_id and v["country_id"] == country_id:
            return v
    return None
