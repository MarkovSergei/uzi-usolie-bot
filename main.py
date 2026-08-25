import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

import config
import database
import bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы
    database.init_db()

    # Запуск бота в фоне
    bot_task = asyncio.create_task(bot.run_bot())

    yield

    # При остановке
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "ok", "service": "uzi-usolie-bot"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
