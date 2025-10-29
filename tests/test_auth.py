import pytest
import requests
from src.endpoints import AUTH_REGISTER as REGISTER, AUTH_LOGIN as LOGIN


class TestRegister:
    def test_register_unique_user(self, new_user):
        """
        Создать уникального пользователя.
        Примечание: фикстура new_user уже отправила POST /auth/register.
        Здесь повторно регистрировать не нужно — просто проверим,
        что если попробовать ещё раз, придёт 403 (уже существует).
        """
        resp = requests.post(REGISTER, json=new_user)
        assert resp.status_code == 403, f"Ожидали 403 при повторной регистрации, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "already" in body.get("message", "").lower()

    def test_register_existing_user(self, new_user):
        """
        Создать пользователя, который уже зарегистрирован.
        """
        resp = requests.post(REGISTER, json=new_user)
        assert resp.status_code == 403, f"Ожидали 403 при повторной регистрации, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "already" in body.get("message", "").lower()

    @pytest.mark.parametrize("missing", ["email", "password", "name"])
    def test_register_missing_required_field(self, missing):
        """
        Создать пользователя, не заполнив одно из обязательных полей.
        Ожидаем 403 и сообщение о required полях.
        """
        payload = {"email": "some@example.com", "password": "password123", "name": "TestUser"}
        payload.pop(missing)
        resp = requests.post(REGISTER, json=payload)
        assert resp.status_code == 403, f"Ожидали 403 при пропуске поля {missing}, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "required" in body.get("message", "").lower()


class TestLogin:
    def test_login_existing_user(self, new_user):
        """
        Вход под существующим пользователем.
        """
        resp = requests.post(LOGIN, json={"email": new_user["email"], "password": new_user["password"]})
        assert resp.status_code == 200, f"Ожидали 200 при логине, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is True
        # accessToken в доке приходит со словом Bearer
        assert "accessToken" in body and isinstance(body["accessToken"], str) and "Bearer" in body["accessToken"]

    @pytest.mark.parametrize(
        "email,password",
        [
            ("not_exists@example.com", "password123"),  # неверный логин
            ("someone@example.com", "wrongpass"),       # неверный пароль
        ],
    )
    def test_login_wrong_email_or_password(self, email, password):
        """
        Вход с неверным логином и/или паролем.
        Ожидаем 401 и сообщение про некорректные данные.
        """
        resp = requests.post(LOGIN, json={"email": email, "password": password})
        assert resp.status_code == 401, f"Ожидали 401 при неверных данных, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is False
        assert "incorrect" in body.get("message", "").lower() or "invalid" in body.get("message", "").lower()