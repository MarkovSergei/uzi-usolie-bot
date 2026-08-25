import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import database

router = APIRouter()

# Простая проверка админа (в будущем можно сделать нормальную авторизацию)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin_secret")

def render_page(content: str) -> str:
    """Оборачиваем контент в HTML."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Админка — Кабинет УЗИ</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 0 15px; }}
            h1 {{ color: #333; }}
            .menu {{ margin-bottom: 20px; }}
            .menu a {{ margin-right: 10px; text-decoration: none; color: #0066cc; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #f0f0f0; }}
            form {{ margin: 10px 0; }}
            input, textarea {{ width: 100%; padding: 8px; margin: 5px 0; }}
            button {{ padding: 8px 16px; background: #0066cc; color: white; border: none; cursor: pointer; }}
            .block {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>Админка — Кабинет УЗИ</h1>
        <div class="menu">
            <a href="/admin">Главная</a>
            <a href="/admin/services">Исследования</a>
            <a href="/admin/faq">FAQ</a>
            <a href="/admin/contacts">Контакты</a>
            <a href="/admin/news">Новости</a>
            <a href="/admin/settings">Настройки</a>
        </div>
        {content}
    </body>
    </html>
    """

@router.get("/admin")
async def admin_home():
    """Главная страница админки."""
    conn = database.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    total_users = cursor.fetchone()[0]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today,))
    new_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    deleted = cursor.fetchone()[0]

    conn.close()

    content = f"""
    <h2>Главная</h2>
    <div class="block">
        <p>Всего пользователей: <b>{total_users}</b></p>
        <p>Новых за сегодня: <b>{new_today}</b></p>
        <p>Удалили бота: <b>{deleted}</b></p>
    </div>
    """
    return HTMLResponse(render_page(content))

@router.get("/admin/services")
async def admin_services():
    """Список исследований."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services ORDER BY id")
    services = cursor.fetchall()
    conn.close()

    rows = ""
    for s in services:
        prep = "Да" if s["preparation"] else "Нет"
        rows += f"""
        <tr>
            <td>{s['id']}</td>
            <td>{s['name']}</td>
            <td>{s['price']}</td>
            <td>{prep}</td>
            <td>{'Да' if s['is_active'] else 'Нет'}</td>
            <td><a href="/admin/services/edit/{s['id']}">Редактировать</a></td>
        </tr>"""

    content = f"""
    <h2>Исследования</h2>
    <a href="/admin/services/add"><button>Добавить исследование</button></a>
    <table>
        <tr><th>ID</th><th>Название</th><th>Цена</th><th>Подготовка</th><th>Активно</th><th></th></tr>
        {rows}
    </table>
    """
    return HTMLResponse(render_page(content))

@router.get("/admin/faq")
async def admin_faq():
    """Список FAQ."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faq ORDER BY sort_order")
    faqs = cursor.fetchall()
    conn.close()

    rows = ""
    for f in faqs:
        rows += f"""
        <tr>
            <td>{f['id']}</td>
            <td>{f['question']}</td>
            <td>{f['answer'][:50]}...</td>
            <td>{f['sort_order']}</td>
            <td><a href="/admin/faq/edit/{f['id']}">Редактировать</a></td>
        </tr>"""

    content = f"""
    <h2>FAQ</h2>
    <a href="/admin/faq/add"><button>Добавить вопрос</button></a>
    <table>
        <tr><th>ID</th><th>Вопрос</th><th>Ответ</th><th>Порядок</th><th></th></tr>
        {rows}
    </table>
    """
    return HTMLResponse(render_page(content))

@router.get("/admin/contacts")
async def admin_contacts():
    """Редактирование контактов."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()

    content = f"""
    <h2>Контакты и график</h2>
    <form action="/admin/contacts/save" method="post">
        <label>Адрес:</label>
        <input type="text" name="address" value="{settings.get('address', '')}">
        <label>Часы работы:</label>
        <input type="text" name="work_hours" value="{settings.get('work_hours', '')}">
        <label>Телефон:</label>
        <input type="text" name="phone" value="{settings.get('phone', '')}">
        <label>Ссылка на карту:</label>
        <input type="text" name="map_link" value="{settings.get('map_link', '')}">
        <button type="submit">Сохранить</button>
    </form>
    """
    return HTMLResponse(render_page(content))

@router.post("/admin/contacts/save")
async def admin_contacts_save(request: Request):
    """Сохранение контактов."""
    form = await request.form()

    conn = database.get_db()
    cursor = conn.cursor()
    for key in ["address", "work_hours", "phone", "map_link"]:
        value = form.get(key, "")
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/contacts", status_code=303)

@router.get("/admin/news")
async def admin_news():
    """Страница рассылок."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC LIMIT 20")
    news = cursor.fetchall()
    conn.close()

    rows = ""
    for n in news:
        rows += f"""
        <tr>
            <td>{n['id']}</td>
            <td>{n['text'][:80]}...</td>
            <td>{n['sent_at']}</td>
            <td>{n['recipients']}</td>
        </tr>"""

    content = f"""
    <h2>Новости и рассылки</h2>
    <form action="/admin/news/send" method="post">
        <label>Текст рассылки:</label>
        <textarea name="text" rows="5"></textarea>
        <button type="submit">Разослать</button>
    </form>
    <h3>История рассылок</h3>
    <table>
        <tr><th>ID</th><th>Текст</th><th>Дата</th><th>Отправлено</th></tr>
        {rows}
    </table>
    """
    return HTMLResponse(render_page(content))

@router.post("/admin/news/send")
async def admin_news_send(request: Request):
    """Отправка рассылки."""
    form = await request.form()
    text = form.get("text", "")

    if not text:
        return RedirectResponse("/admin/news", status_code=303)

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users WHERE is_active = 1")
    users = cursor.fetchall()

    sent = 0
    from bot import bot
    for user in users:
        try:
            await bot.send_message(chat_id=user["chat_id"], text=text)
            sent += 1
        except:
            pass

    cursor.execute(
        "INSERT INTO news (text, recipients) VALUES (?, ?)",
        (text, sent)
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/news", status_code=303)

@router.get("/admin/settings")
async def admin_settings():
    """Настройки."""
    content = """
    <h2>Настройки</h2>
    <p>Настройки задаются через переменные окружения Bothost:</p>
    <ul>
        <li><b>BOT_TOKEN</b> — токен бота Telegram</li>
        <li><b>ADMIN_USER_ID</b> — ваш Telegram ID</li>
        <li><b>PORT</b> — порт (обычно 8000)</li>
        <li><b>ADMIN_TOKEN</b> — секретный токен для входа в админку</li>
    </ul>
    """
    return HTMLResponse(render_page(content))
