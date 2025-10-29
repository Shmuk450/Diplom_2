import pytest
import requests
from src.endpoints import INGREDIENTS, ORDERS


@pytest.fixture(scope="session")
def ingredient_ids():
    """Берём валидные id ингредиентов из публичного эндпоинта."""
    resp = requests.get(INGREDIENTS)
    assert resp.status_code == 200, f"/ingredients вернул {resp.status_code}: {resp.text}"
    data = resp.json()
    ids = [item.get("_id") for item in data.get("data", []) if item.get("_id")]
    assert len(ids) >= 2, "Сервис вернул недостаточно ингредиентов (ожидали >= 2)"
    return ids


class TestCreateOrder:
    def test_order_with_auth_and_ingredients(self, auth_headers, ingredient_ids):
        """
        Создание заказа с авторизацией и валидными ингредиентами → 200, success=True, есть номер заказа.
        """
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is True, f"success != True: {body}"
        # в ответе должен быть номер заказа
        assert body.get("order", {}).get("number") is not None, f"Нет номера заказа в ответе: {body}"

    def test_order_without_auth_with_ingredients(self, ingredient_ids):
        """
        Создание заказа без авторизации → 401 и сообщение про необходимость авторизации.
        """
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload)  # без headers
        assert resp.status_code == 401, f"Ожидали 401, получили {resp.status_code}: {resp.text}"
        msg = resp.json().get("message", "").lower()
        assert "authoris" in msg or "authent" in msg, f"Не нашли подсказку про авторизацию: {msg}"

    def test_order_with_no_ingredients(self, auth_headers):
        """
        Создание заказа без ингредиентов → 400 и сообщение, что нужны ids ингредиентов.
        """
        payload = {"ingredients": []}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 400, f"Ожидали 400, получили {resp.status_code}: {resp.text}"
        msg = resp.json().get("message", "").lower()
        assert ("ingredient" in msg and "must" in msg) or "ingredient ids" in msg, f"Сообщение: {msg}"

    def test_order_with_invalid_ingredient_hash(self, auth_headers):
        """
        Создание заказа с неверным хешем ингредиентов → обычно 500 по доке.
        Если бэкенд вернёт 400 — тоже примем как валидную реакцию клиента на невалидный инпут.
        """
        payload = {"ingredients": ["NOT_A_VALID_ID"]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code in (500, 400), f"Ожидали 500/400, получили {resp.status_code}: {resp.text}"

    def test_order_with_ingredients_explicit(self, auth_headers, ingredient_ids):
        """
        Доп. позитив: ещё раз проверим success=True при валидном заказе с авторизацией.
        """
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}: {resp.text}"
        assert resp.json().get("success") is True