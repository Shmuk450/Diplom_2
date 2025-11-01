import random
import string


def random_email() -> str:
    """Генерация уникального email для теста."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"autotest_{suffix}@example.com"


# Дефолтные данные для тестовых пользователей
DEFAULT_PASSWORD = "password123"
DEFAULT_NAME = "TestUser"