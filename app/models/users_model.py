import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'users.json')

def load_users():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return users
    except FileNotFoundError:
        return []


def save_users(users):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

def add_user(user_id, name):
    users = load_users()
    users.append({"id": user_id, "name": name})
    save_users(users)

def get_user_by_id(user_id):
    users = load_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None
