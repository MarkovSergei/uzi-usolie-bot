import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import config
import database

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    """Клавиатура главного меню."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🩺 Виды УЗИ и цены")],
            [KeyboardButton(text="❓ Вопросы и ответы")],
            [KeyboardButton(text="📅 Запланировать визит")],
            [KeyboardButton(text="🔔 Мои напоминания")],
            [KeyboardButton(text="📍 Контакты и график")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start."""
    chat_id = str(message.chat.id)

    # Регистрируем пользователя
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
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text == "🩺 Виды УЗИ и цены")
async def services_list(message: types.Message):
    await message.answer("Здесь будет список исследований.")

@dp.message(F.text == "❓ Вопросы и ответы")
async def faq_list(message: types.Message):
    await message.answer("Здесь будут вопросы и ответы.")

@dp.message(F.text == "📅 Запланировать визит")
async def plan_visit(message: types.Message):
    await message.answer("Здесь будет планировщик.")

@dp.message(F.text == "🔔 Мои напоминания")
async def my_reminders(message: types.Message):
    await message.answer("Здесь будут ваши напоминания.")

@dp.message(F.text == "📍 Контакты и график")
async def contacts(message: types.Message):
    await message.answer("Здесь будут контакты.")

async def run_bot():
    """Запуск polling."""
    await dp.start_polling(bot)
