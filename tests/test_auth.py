import pytest
import requests
import allure
from src.endpoints import AUTH_REGISTER as REGISTER, AUTH_LOGIN as LOGIN


@allure.feature("Регистрация пользователей")
class TestRegister:

    @allure.title("Создание уникального пользователя")
    def test_register_unique_user(self, new_user):
        user_data, _ = new_user
        resp = requests.post(REGISTER, json=user_data)
        assert resp.status_code == 403, f"Ожидали 403 при повторной регистрации, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "already" in body.get("message", "").lower()

    @allure.title("Регистрация пользователя, который уже существует")
    def test_register_existing_user(self, new_user):
        user_data, _ = new_user
        resp = requests.post(REGISTER, json=user_data)
        assert resp.status_code == 403, f"Ожидали 403 при повторной регистрации, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "already" in body.get("message", "").lower()

    @allure.title("Регистрация без обязательного поля (email, password, name)")
    @pytest.mark.parametrize("missing", ["email", "password", "name"])
    def test_register_missing_required_field(self, missing):
        payload = {"email": "some@example.com", "password": "password123", "name": "TestUser"}
        payload.pop(missing)
        resp = requests.post(REGISTER, json=payload)
        assert resp.status_code == 403, f"Ожидали 403 при пропуске поля {missing}, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "required" in body.get("message", "").lower()


@allure.feature("Авторизация пользователей")
class TestLogin:

    @allure.title("Успешный логин под существующим пользователем")
    def test_login_existing_user(self, new_user):
        user_data, _ = new_user
        resp = requests.post(LOGIN, json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert resp.status_code == 200, f"Ожидали 200 при логине, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is True
        assert "accessToken" in body and isinstance(body["accessToken"], str) and "Bearer" in body["accessToken"]

    @allure.title("Логин с неверным логином или паролем")
    @pytest.mark.parametrize(
        "email,password",
        [
            ("not_exists@example.com", "password123"),
            ("someone@example.com", "wrongpass"),
        ],
    )
    def test_login_wrong_email_or_password(self, email, password):
        resp = requests.post(LOGIN, json={"email": email, "password": password})
        assert resp.status_code == 401, f"Ожидали 401 при неверных данных, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "incorrect" in body.get("message", "").lower() or "invalid" in body.get("message", "").lower()