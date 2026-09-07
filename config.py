import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# MAX
MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "")

# Общие
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
PORT = int(os.getenv("PORT", 8000))

# Периоды напоминаний (месяцы)
REMINDER_PERIODS = [1, 3, 6, 12]
