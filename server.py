from fastapi import FastAPI
import asyncio
import threading
from bot import start_bot

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running!"}

def run_bot():
    asyncio.run(start_bot())

threading.Thread(target=run_bot).start()
