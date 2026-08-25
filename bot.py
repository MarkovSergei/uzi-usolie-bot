import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import database

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ------------------------- КЛАВИАТУРЫ -------------------------

def get_main_keyboard():
    """Главное меню."""
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

def get_back_keyboard():
    """Клавиатура с кнопкой Назад."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="← Назад")],
        ],
        resize_keyboard=True
    )

def get_back_main_keyboard():
    """Клавиатура Назад + Главное меню."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="← Назад")],
            [KeyboardButton(text="🏠 Главное меню")],
        ],
        resize_keyboard=True
    )

# ------------------------- ОБРАБОТЧИКИ -------------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка /start."""
    chat_id = str(message.chat.id)

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


# ------------------------- ВИДЫ УЗИ -------------------------

@dp.message(F.text == "🩺 Виды УЗИ и цены")
async def services_list(message: types.Message):
    """Список исследований."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price FROM services WHERE is_active = 1 ORDER BY name"
    )
    services = cursor.fetchall()
    conn.close()

    if not services:
        await message.answer("Список исследований пока пуст.", reply_markup=get_main_keyboard())
        return

    keyboard = []
    for service in services:
        keyboard.append([InlineKeyboardButton(
            text=service["name"],
            callback_data=f"service_{service['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])

    await message.answer(
        "Выберите исследование:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@dp.callback_query(F.data.startswith("service_"))
async def service_detail(callback: types.CallbackQuery):
    """Детали исследования."""
    service_id = int(callback.data.split("_")[1])

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, price, preparation FROM services WHERE id = ?",
        (service_id,)
    )
    service = cursor.fetchone()
    conn.close()

    if not service:
        await callback.answer("Исследование не найдено")
        return

    text = f"🩺 {service['name']}\n\n"
    text += f"💰 Цена: {service['price']}\n\n"

    if service["preparation"]:
        text += f"📋 Подготовка:\n{service['preparation']}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад к списку", callback_data="back_to_services")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery):
    """Возврат к списку исследований."""
    await callback.answer()
    await services_list(callback.message)


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню."""
    await callback.answer()
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())


# ------------------------- FAQ -------------------------

@dp.message(F.text == "❓ Вопросы и ответы")
async def faq_list(message: types.Message):
    """Список вопросов."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question FROM faq ORDER BY sort_order"
    )
    faqs = cursor.fetchall()
    conn.close()

    if not faqs:
        await message.answer("Вопросы пока не добавлены.", reply_markup=get_main_keyboard())
        return

    keyboard = []
    for faq in faqs:
        keyboard.append([InlineKeyboardButton(
            text=faq["question"],
            callback_data=f"faq_{faq['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])

    await message.answer(
        "Частые вопросы:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@dp.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: types.CallbackQuery):
    """Ответ на вопрос."""
    faq_id = int(callback.data.split("_")[1])

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM faq WHERE id = ?", (faq_id,))
    faq = cursor.fetchone()
    conn.close()

    if not faq:
        await callback.answer("Вопрос не найден")
        return

    text = f"❓ {faq['question']}\n\n{faq['answer']}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад к вопросам", callback_data="back_to_faq")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "back_to_faq")
async def back_to_faq(callback: types.CallbackQuery):
    """Возврат к списку вопросов."""
    await callback.answer()
    await faq_list(callback.message)


# ------------------------- ЗАПЛАНИРОВАТЬ ВИЗИТ -------------------------

class PlanVisit(StatesGroup):
    choosing_service = State()
    choosing_period = State()
    choosing_custom_date = State()


@dp.message(F.text == "📅 Запланировать визит")
async def plan_visit_start(message: types.Message, state: FSMContext):
    """Начало планирования."""
    await state.set_state(PlanVisit.choosing_service)

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM services WHERE is_active = 1 ORDER BY name"
    )
    services = cursor.fetchall()
    conn.close()

    if not services:
        await message.answer("Список исследований пока пуст.", reply_markup=get_main_keyboard())
        await state.clear()
        return

    keyboard = []
    for service in services:
        keyboard.append([InlineKeyboardButton(
            text=service["name"],
            callback_data=f"plan_service_{service['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="← Назад", callback_data="plan_back_to_main")])

    await message.answer(
        "Выберите исследование:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@dp.callback_query(F.data.startswith("plan_service_"))
async def plan_service_chosen(callback: types.CallbackQuery, state: FSMContext):
    """Исследование выбрано."""
    service_id = int(callback.data.split("_")[2])

    await state.update_data(service_id=service_id)
    await state.set_state(PlanVisit.choosing_period)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц", callback_data="period_1")],
        [InlineKeyboardButton(text="3 месяца", callback_data="period_3")],
        [InlineKeyboardButton(text="6 месяцев", callback_data="period_6")],
        [InlineKeyboardButton(text="12 месяцев", callback_data="period_12")],
        [InlineKeyboardButton(text="Своя дата", callback_data="period_custom")],
        [InlineKeyboardButton(text="← Назад", callback_data="plan_back_to_services")],
    ])

    await callback.message.answer("Через сколько напомнить?", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("period_"))
async def plan_period_chosen(callback: types.CallbackQuery, state: FSMContext):
    """Период выбран."""
    data = await state.get_data()
    service_id = data["service_id"]

    period = callback.data.split("_")[1]

    if period == "custom":
        await state.set_state(PlanVisit.choosing_custom_date)
        await callback.message.answer(
            "Введите дату в формате ДД.ММ.ГГГГ\nНапример: 25.02.2027"
        )
        await callback.answer()
        return

    months = int(period)
    remind_date = (datetime.now() + timedelta(days=months * 30)).strftime("%d.%m.%Y")

    await save_reminder(callback, state, service_id, remind_date)


@dp.message(PlanVisit.choosing_custom_date)
async def plan_custom_date(message: types.Message, state: FSMContext):
    """Своя дата."""
    try:
        date_obj = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        remind_date = date_obj.strftime("%d.%m.%Y")

        data = await state.get_data()
        service_id = data["service_id"]

        await save_reminder(message, state, service_id, remind_date)
    except ValueError:
        await message.answer(
            "Неверный формат даты. Попробуйте ещё раз:\nПример: 25.02.2027"
        )


async def save_reminder(event, state: FSMContext, service_id: int, remind_date: str):
    """Сохранение напоминания."""
    # Определяем chat_id и message для ответа
    if hasattr(event, 'message') and event.message is not None:
        chat_id = str(event.message.chat.id)
        message = event.message
    else:
        chat_id = str(event.chat.id)
        message = event

    # Проверяем, есть ли уже напоминание на это исследование
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT remind_date FROM reminders WHERE chat_id = ? AND service_id = ? AND is_sent = 0",
        (chat_id, service_id)
    )
    existing = cursor.fetchone()

    if existing:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да, обновить", callback_data=f"update_reminder_{service_id}_{remind_date}")],
            [InlineKeyboardButton(text="Отмена", callback_data="plan_back_to_main")],
        ])
        await message.answer(
            f"У вас уже запланировано это исследование на {existing['remind_date']}.\n\nОбновить дату?",
            reply_markup=keyboard
        )
        conn.close()
        await state.clear()
        return

    cursor.execute(
        "INSERT INTO reminders (chat_id, service_id, remind_date) VALUES (?, ?, ?)",
        (chat_id, service_id, remind_date)
    )
    conn.commit()

    # Получаем название исследования
    cursor.execute("SELECT name FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    conn.close()

    text = (
        "✅ Запланировано!\n\n"
        f"Исследование: {service['name']}\n"
        f"Напомню: {remind_date}\n\n"
        "За день до визита пришлю напоминание с подготовкой, графиком работы и адресом."
    )

    await message.answer(text, reply_markup=get_main_keyboard())
    await state.clear()


@dp.callback_query(F.data.startswith("update_reminder_"))
async def update_reminder(callback: types.CallbackQuery):
    """Обновление напоминания."""
    parts = callback.data.split("_")
    service_id = int(parts[2])
    remind_date = parts[3]

    chat_id = str(callback.message.chat.id)

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET remind_date = ? WHERE chat_id = ? AND service_id = ? AND is_sent = 0",
        (remind_date, chat_id, service_id)
    )
    conn.commit()
    conn.close()

    await callback.message.answer(
        f"✅ Дата обновлена!\n\nНапомню: {remind_date}",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "plan_back_to_services")
async def plan_back_to_services(callback: types.CallbackQuery, state: FSMContext):
    """Назад к списку исследований."""
    await state.set_state(PlanVisit.choosing_service)
    await callback.answer()
    await plan_visit_start(callback.message, state)


@dp.callback_query(F.data == "plan_back_to_main")
async def plan_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Назад в главное меню."""
    await state.clear()
    await callback.answer()
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())


# ------------------------- МОИ НАПОМИНАНИЯ -------------------------

@dp.message(F.text == "🔔 Мои напоминания")
async def my_reminders(message: types.Message):
    """Список напоминаний."""
    chat_id = str(message.chat.id)

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.remind_date, s.name
        FROM reminders r
        JOIN services s ON r.service_id = s.id
        WHERE r.chat_id = ? AND r.is_sent = 0
        ORDER BY r.remind_date
        """,
        (chat_id,)
    )
    reminders = cursor.fetchall()
    conn.close()

    if not reminders:
        await message.answer("У вас нет активных напоминаний.", reply_markup=get_main_keyboard())
        return

    keyboard = []
    for reminder in reminders:
        keyboard.append([InlineKeyboardButton(
            text=f"{reminder['name']} — {reminder['remind_date']}",
            callback_data=f"myrem_{reminder['remind_date']}_{reminder['name']}"
        )])
    keyboard.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])

    await message.answer(
        "Ваши напоминания:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@dp.callback_query(F.data.startswith("myrem_"))
async def my_reminder_detail(callback: types.CallbackQuery):
    """Детали напоминания."""
    parts = callback.data.split("_")
    remind_date = parts[1]
    service_name = "_".join(parts[2:])

    text = (
        f"🔔 Напоминание\n\n"
        f"Исследование: {service_name}\n"
        f"Дата: {remind_date}\n\n"
        f"Бот пришлёт напоминание за 1 день."
    )

    await callback.message.answer(text)
    await callback.answer()


# ------------------------- КОНТАКТЫ -------------------------

@dp.message(F.text == "📍 Контакты и график")
async def contacts(message: types.Message):
    """Контакты и график."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings WHERE key IN ('address', 'work_hours', 'phone', 'map_link')")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть на карте", url=settings.get("map_link", ""))],
        InlineKeyboardButton(text="📲 Задать вопрос врачу", url="https://t.me/MarkovSerge")
    ])

    text = (
        f"📍 Адрес: {settings.get('address', '')}\n\n"
        f"🕒 Часы работы: {settings.get('work_hours', '')}\n\n"
        f"📞 Телефон: {settings.get('phone', '')}"
    )

    await message.answer(text, reply_markup=keyboard)


# ------------------------- ЗАПУСК -------------------------

async def run_bot():
    """Запуск polling."""
    await dp.start_polling(bot)
