import json
import os

USERS_FILE = "data/users.json"

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)


def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def login_user(username, password):
    users = load_users()
    return users.get(username) == password


def register_user(username, password):
    users = load_users()
    users[username] = password
    save_users(users)


def check_user_exists(username):
    users = load_users()
    return username in users
