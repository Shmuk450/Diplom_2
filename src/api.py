import requests
from src.endpoints import REGISTER, LOGIN, USER, ORDERS
from src.data import generate_email, DEFAULT_PASSWORD, DEFAULT_NAME


class StellarApi:
    """Класс для взаимодействия с API Stellar Burgers."""

    def _init_(self):
        # Создаём сессию для выполнения запросов и инициализируем токен авторизации
        self.session = requests.Session()
        self.token = None

    def register(self, email=None, password=None, name=None):
        """Регистрация нового пользователя."""
        if not email:
            email = generate_email()
        if not password:
            password = DEFAULT_PASSWORD
        if not name:
            name = DEFAULT_NAME

        payload = {"email": email, "password": password, "name": name}
        response = self.session.post(REGISTER, json=payload)

        # Если регистрация успешна — сохраняем токен авторизации
        if response.status_code == 200 and "accessToken" in response.json():
            self.token = response.json()["accessToken"]
        return response

    def login(self, email, password):
        """Авторизация пользователя по email и паролю."""
        payload = {"email": email, "password": password}
        response = self.session.post(LOGIN, json=payload)

        # Если авторизация успешна — сохраняем токен
        if response.status_code == 200 and "accessToken" in response.json():
            self.token = response.json()["accessToken"]
        return response

    def get_user(self):
        """Получение данных текущего авторизованного пользователя."""
        headers = {"Authorization": self.token} if self.token else {}
        return self.session.get(USER, headers=headers)

    def create_order(self, ingredients):
        """Создание нового заказа."""
        headers = {"Authorization": self.token} if self.token else {}
        payload = {"ingredients": ingredients}
        return self.session.post(ORDERS, headers=headers, json=payload)