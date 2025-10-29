import pytest
import requests
import random
import string
from src.endpoints import AUTH_REGISTER as REGISTER, AUTH_LOGIN as LOGIN

def random_email():
    return "user_" + ''.join(random.choices(string.ascii_lowercase, k=6)) + "@example.com"

@pytest.fixture(scope="session")
def new_user():
    user_data = {
        "email": random_email(),
        "password": "password123",
        "name": "TestUser"
    }
    # регистрируем; 200 — ок, 403 — повторная регистрация того же e-mail тоже ок
    resp = requests.post(REGISTER, json=user_data)
    assert resp.status_code in (200, 403), f"Ошибка регистрации: {resp.status_code} {resp.text}"
    return user_data

@pytest.fixture(scope="session")
def user_token(new_user):
    resp = requests.post(LOGIN, json={
        "email": new_user["email"],
        "password": new_user["password"]
    })
    assert resp.status_code == 200, f"Ошибка авторизации: {resp.status_code} {resp.text}"
    token = resp.json().get("accessToken", "")
    # Нормализуем: если уже начинается с 'Bearer ', оставляем как есть,
    # иначе добавляем префикс.
    if not token.startswith("Bearer "):
        token = f"Bearer {token}"
    return token

@pytest.fixture
def auth_headers(user_token):
    # имя заголовка — 'Authorization'; заголовки регистронезависимы,
    # но это каноничное написание.
    return {"Authorization": user_token}