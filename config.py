import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
PORT = int(os.getenv("PORT", 8000))

# Периоды напоминаний (месяцы)
REMINDER_PERIODS = [1, 3, 6, 12]
