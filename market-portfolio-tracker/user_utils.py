import json
import os
import bcrypt
import re

USERS_FILE = "users.json"

def is_secure_password(password):
    if len(password) < 6:
        return False
    if re.search(r'012|123|234|345|456|567|678|789|890|987|876|765|654|543|432|321', password):
        return False
    if re.search(r'(\d)\1\1', password):
        return False
    return True


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def register_user(username_or_email, password):
    users = load_users()
    if username_or_email in users:
        return "❌ Bu kullanıcı adı veya e-posta zaten kayıtlı."

    if not is_secure_password(password):
        return "❌ Şifre güvenli değil. En az 6 karakter olmalı ve basit diziler içermemeli."

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
    
    users[username_or_email] = {
        "password": hashed_pw,
        "budget": 10000.0,  #baslangıc bakiye
        "portfolio": {
            "USD": 0.0,
            "EUR": 0.0,
            "ALTIN": 0.0,
            "BTC": 0.0
        }
    }

    save_users(users)
    return "✅ Başarılı bir şekilde kayıt olundu!"


def login_user(username_or_email, password):
    users = load_users()
    if username_or_email not in users:
        return "❌ Kullanıcı bulunamadı."

    hashed = users[username_or_email]["password"].encode("utf-8")
    if not bcrypt.checkpw(password.encode(), hashed):
        return "❌ Şifre yanlış."

    return f"Hoş geldin, {username_or_email}!"


def get_user_data(username_or_email):
    users = load_users()
    return users.get(username_or_email)


def update_user_data(username_or_email, updated_data):
    users = load_users()
    if username_or_email in users:
        users[username_or_email].update(updated_data)
        save_users(users)
        return True
    return False
