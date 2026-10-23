import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# ID чата/группы, куда бот присылает новые заказы (узнать свой ID: @userinfobot)
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# Путь к базе. На Railway подключите Volume и укажите, например, /data/orders.db
DB_PATH = os.getenv("DB_PATH", "orders.db")

# Контакты магазина — поменяйте на свои через переменные окружения
SHOP_NAME = os.getenv("SHOP_NAME", "China Cars")
SHOP_PHONE = os.getenv("SHOP_PHONE", "+7 (700) 000-00-00")
SHOP_SITE = os.getenv("SHOP_SITE", "https://example.com")
SHOP_ADDRESS = os.getenv("SHOP_ADDRESS", "г. Алматы, ул. Примерная, 1")
SHOP_HOURS = os.getenv("SHOP_HOURS", "Пн–Сб 9:00–19:00, Вс — выходной")
