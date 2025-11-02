BASE_URL = "https://stellarburgers.education-services.ru"

INGREDIENTS = f"{BASE_URL}/api/ingredients"

AUTH_REGISTER = f"{BASE_URL}/api/auth/register"
AUTH_LOGIN    = f"{BASE_URL}/api/auth/login"
AUTH_USER     = f"{BASE_URL}/api/auth/user"      # GET/PATCH/DELETE (с токеном)

ORDERS        = f"{BASE_URL}/api/orders"         # POST создание заказа
ORDERS_ALL    = f"{BASE_URL}/api/orders/all"     # GET лента всех заказов (если нужно)