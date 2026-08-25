import asyncio
from datetime import datetime, timedelta

import database
from bot import bot
import config

IRKUTSK_TZ_OFFSET = 8  # UTC+8

def get_irkutsk_now():
    """Текущее время в Иркутске."""
    return datetime.utcnow() + timedelta(hours=IRKUTSK_TZ_OFFSET)

def is_working_day(date_obj):
    """Проверка: рабочий ли день (пн-пт)."""
    return date_obj.weekday() < 5  # 0=Пн, 4=Пт

def get_previous_working_day(date_obj):
    """Ближайший предыдущий рабочий день."""
    while not is_working_day(date_obj):
        date_obj -= timedelta(days=1)
    return date_obj

async def check_reminders():
    """Проверка и отправка напоминаний."""
    now = get_irkutsk_now()

    # Напоминания отправляем в 08:00 по Иркутску
    if now.hour != 8:
        return

    tomorrow = now.date() + timedelta(days=1)

    # Если завтра выходной — ищем ближайший рабочий день
    reminder_date = get_previous_working_day(tomorrow)

    conn = database.get_db()
    cursor = conn.cursor()

    # Ищем напоминания на завтра (или ближайший рабочий день)
    cursor.execute(
        """
        SELECT r.id, r.chat_id, r.service_id, s.name, s.preparation
        FROM reminders r
        JOIN services s ON r.service_id = s.id
        WHERE r.remind_date = ? AND r.is_sent = 0
        """,
        (reminder_date.strftime("%d.%m.%Y"),)
    )
    reminders = cursor.fetchall()

    for reminder in reminders:
        # Формируем текст
        text = (
            "🔔 Вы просили напомнить о плановом визите!\n\n"
            f"🩺 Исследование: {reminder['name']}\n\n"
        )

        if reminder["preparation"]:
            text += f"📋 Подготовка:\n{reminder['preparation']}\n\n"
        else:
            text += "📋 Подготовка: не требуется\n\n"

        text += (
            "🕒 График работы: пн–пт с 9:00 до 13:00\n\n"
            "📍 Адрес: проезд Фестивальный, 9; кабинет 312\n\n"
            "Ждём вас!"
        )

        try:
            await bot.send_message(chat_id=reminder["chat_id"], text=text)

            # Помечаем как отправленное
            cursor.execute(
                "UPDATE reminders SET is_sent = 1 WHERE id = ?",
                (reminder["id"],)
            )
            conn.commit()
        except Exception as e:
            print(f"Ошибка отправки напоминания {reminder['id']}: {e}")
            # Если ошибка (бот заблокирован) — удаляем напоминание
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder["id"],))
            conn.commit()

    conn.close()

async def run_scheduler():
    """Фоновый цикл планировщика."""
    while True:
        try:
            await check_reminders()
        except Exception as e:
            print(f"Ошибка планировщика: {e}")
        await asyncio.sleep(3600)  # Проверка раз в час
