import pytest
import requests
from src.data import random_email
from src.endpoints import AUTH_REGISTER as REGISTER, AUTH_LOGIN as LOGIN, AUTH_USER, INGREDIENTS


@pytest.fixture(scope="function")
def new_user():
    """Создание и удаление пользователя для тестов"""
    user_data = {
        "email": random_email(),
        "password": "password123",
        "name": "TestUser"
    }

    # Регистрируем пользователя
    response = requests.post(REGISTER, json=user_data)
    assert response.status_code in (200, 403), (
        f"Ошибка регистрации: {response.status_code} {response.text}"
    )

    # Логинимся
    login_response = requests.post(LOGIN, json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200, (
        f"Ошибка авторизации: {login_response.status_code} {login_response.text}"
    )

    token = login_response.json().get("accessToken", "")
    if not token.startswith("Bearer "):
        token = f"Bearer {token}"

    # Передаём данные тесту
    yield user_data, token

    # После теста — удаляем пользователя
    try:
        requests.delete(AUTH_USER, headers={"Authorization": token})
    except Exception:
        pass


@pytest.fixture
def auth_headers(new_user):
    """Заголовок с токеном авторизации"""
    _, token = new_user
    return {"Authorization": token}


@pytest.fixture(scope="session")
def ingredient_ids():
    """Берём валидные id ингредиентов из публичного эндпоинта."""
    resp = requests.get(INGREDIENTS)
    assert resp.status_code == 200, f"/ingredients вернул {resp.status_code}: {resp.text}"
    data = resp.json()
    ids = [item.get("_id") for item in data.get("data", []) if item.get("_id")]
    assert len(ids) >= 2, "Сервис вернул недостаточно ингредиентов (ожидали >= 2)"
    return ids