import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
PORT = int(os.getenv("PORT", 8000))
IRKUTSK_TZ_OFFSET = 8  # UTC+8

# Периоды напоминаний в месяцах
REMINDER_PERIODS = [1, 3, 6, 12]
