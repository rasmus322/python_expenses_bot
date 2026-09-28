import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найдет BOT_TOKEN бота. Создайте .env и добавьте туда свой токен.")

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///expense_database.db")