import pytest
import requests
import allure
from src.endpoints import ORDERS


class TestCreateOrder:

    @allure.title("Создание заказа с авторизацией и валидными ингредиентами")
    def test_order_with_auth_and_ingredients(self, auth_headers, ingredient_ids):
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body.get("success") is True, f"success != True: {body}"
        assert body.get("order", {}).get("number") is not None, f"Нет номера заказа в ответе: {body}"

    @allure.title("Создание заказа без авторизации")
    def test_order_without_auth_with_ingredients(self, ingredient_ids):
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload)
        assert resp.status_code == 401, f"Ожидали 401, получили {resp.status_code}: {resp.text}"
        msg = resp.json().get("message", "").lower()
        assert "authoris" in msg or "authent" in msg, f"Не нашли подсказку про авторизацию: {msg}"

    @allure.title("Создание заказа без ингредиентов")
    def test_order_with_no_ingredients(self, auth_headers):
        payload = {"ingredients": []}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 400, f"Ожидали 400, получили {resp.status_code}: {resp.text}"
        msg = resp.json().get("message", "").lower()
        assert ("ingredient" in msg and "must" in msg) or "ingredient ids" in msg, f"Сообщение: {msg}"

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    def test_order_with_invalid_ingredient_hash(self, auth_headers):
        payload = {"ingredients": ["NOT_A_VALID_ID"]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code in (500, 400), f"Ожидали 500/400, получили {resp.status_code}: {resp.text}"

    @allure.title("Создание валидного заказа (дополнительная позитивная проверка)")
    def test_order_with_ingredients_explicit(self, auth_headers, ingredient_ids):
        payload = {"ingredients": ingredient_ids[:2]}
        resp = requests.post(ORDERS, json=payload, headers=auth_headers)
        assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}: {resp.text}"
        assert resp.json().get("success") is True