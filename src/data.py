import random
import string


def generate_email() -> str:
    """Генерация уникального email для теста."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"autotest_{suffix}@example.com"


DEFAULT_PASSWORD = "password123"
DEFAULT_NAME = "TestUser"