import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

import database
import config

# Импорт обработчиков (будут позже)
# import bot_handlers
# import admin_routes
# import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте
    database.init_db()
    # Запуск фонового планировщика
    # asyncio.create_task(scheduler.run())
    yield
    # При остановке
    pass

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "ok", "service": "uzi-usolie-bot"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.PORT
    )
