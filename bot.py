import asyncio
import requests
from datetime import datetime, timedelta

import config
import database

def send_message(chat_id, text, keyboard=None):
    """Отправка сообщения в Макс."""
    url = f"https://api.max.ru/bot/{config.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if keyboard:
        payload["keyboard"] = keyboard
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return None

def get_main_keyboard():
    """Клавиатура главного меню."""
    return {
        "buttons": [
            [{"text": "🩺 Виды УЗИ и цены"}],
            [{"text": "❓ Вопросы и ответы"}],
            [{"text": "📅 Запланировать визит"}],
            [{"text": "🔔 Мои напоминания"}],
            [{"text": "📍 Контакты и график"}],
        ]
    }

def handle_start(chat_id):
    """Обработка команды /start."""
    # Регистрация пользователя
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (chat_id) VALUES (?)",
        (chat_id,)
    )
    conn.commit()
    conn.close()

    text = (
        "Здравствуйте!\n\n"
        "Я бот кабинета УЗИ Маркова Сергея Борисовича.\n"
        "Помогу узнать цены, подготовку к исследованиям и напомню о плановом визите.\n\n"
        "Выберите действие в меню:"
    )
    send_message(chat_id, text, get_main_keyboard())

def handle_message(chat_id, text):
    """Обработка входящих сообщений."""
    if text == "/start":
        handle_start(chat_id)
    elif text == "🩺 Виды УЗИ и цены":
        # Заглушка, будет позже
        send_message(chat_id, "Здесь будет список исследований.")
    elif text == "❓ Вопросы и ответы":
        send_message(chat_id, "Здесь будет FAQ.")
    elif text == "📅 Запланировать визит":
        send_message(chat_id, "Здесь будет планировщик.")
    elif text == "🔔 Мои напоминания":
        send_message(chat_id, "Здесь будут ваши напоминания.")
    elif text == "📍 Контакты и график":
        send_message(chat_id, "Здесь будут контакты.")
    else:
        send_message(chat_id, "Используйте кнопки меню.", get_main_keyboard())

async def run_polling():
    """Опрос сервера Макс."""
    while True:
        # Здесь будет запрос getUpdates
        await asyncio.sleep(2)
