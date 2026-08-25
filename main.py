import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

import config
import database
import bot
import scheduler
import admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы
    database.init_db()

    # Запуск бота в фоне
    bot_task = asyncio.create_task(bot.run_bot())

    # Запуск планировщика в фоне
    scheduler_task = asyncio.create_task(scheduler.run_scheduler())

    yield

    # При остановке
    bot_task.cancel()
    scheduler_task.cancel()

app = FastAPI(lifespan=lifespan)

# Подключаем админку
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "uzi-usolie-bot"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
