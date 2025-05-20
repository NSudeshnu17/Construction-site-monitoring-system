import gspread
from google.oauth2.service_account import Credentials
import bcrypt
import streamlit as st

# Google Sheets configuration
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1FPY91ugpezC2fwyzPQJUOdSTOow5NAFHHOFwgX9ap6A"  # Your actual sheet ID

def get_worksheet():
    # ✅ Load credentials from Streamlit secrets
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet("users")

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password):
    worksheet = get_worksheet()
    usernames = worksheet.col_values(1)

    if username in usernames:
        return False  # User already exists

    hashed_password = hash_password(password)
    worksheet.append_row([username, hashed_password])
    return True

def login_user(username, password):
    worksheet = get_worksheet()
    users = worksheet.get_all_records()

    for user in users:
        if user["username"] == username:
            stored_password = user["password"]
            if verify_password(password, stored_password):
                return True
    return False

def check_user_exists(username):
    worksheet = get_worksheet()
    usernames = worksheet.col_values(1)
    return username in usernames
