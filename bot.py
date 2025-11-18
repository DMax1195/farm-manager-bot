import os
import logging
from aiohttp import web # Импортируем веб-фреймворк
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Update
import json
from dotenv import load_dotenv # Для локального тестирования
# ... (Импорты sqlite3, List, Tuple остаются) ...

# --------------------------
# НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# --------------------------

# Vercel требует считывания переменных из окружения.
# Для локальной разработки используйте .env файл и load_dotenv().
# На Vercel переменные будут предоставлены автоматически.
load_dotenv() 

# Получение данных из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook/"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH # Это будет URL вашего деплоя на Vercel

# --------------------------
# КОНСТАНТЫ И ИНИЦИАЛИЗАЦИЯ (Остаются прежними)
# --------------------------
# ... (TARGET_CHAT, TARGET_THREAD, DB_NAME, init_db, calc, и т.д. остаются) ...

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --------------------------
# ОБРАБОТЧИКИ КОМАНД (Остаются прежними: /start, /help, /calc, /yield, /seed, /addalert, /showalerts)
# --------------------------
# ... (Все ваши обработчики @dp.message(...) и @dp.callback_query() остаются без изменений) ...


# --------------------------
# ОСНОВНАЯ ЛОГИКА WEBHOOK
# --------------------------

async def set_webhook():
    """Устанавливает Webhook при запуске, если он не установлен."""
    if not BOT_TOKEN or not WEBHOOK_URL:
        logging.error("Не настроены переменные BOT_TOKEN или WEBHOOK_URL.")
        return False

    # Устанавливаем Webhook
    return await bot.set_webhook(WEBHOOK_URL)


async def handle_webhook(request):
    """Обрабатывает входящий POST-запрос от Telegram."""
    if request.match_info.get('path') != WEBHOOK_PATH.strip('/'):
        return web.Response(status=404) # Неверный путь

    data = await request.json()
    
    # Aiogram автоматически обрабатывает входящие данные
    telegram_update = Update.model_validate(data)
    
    # Пропускаем обновление через диспетчер
    await dp.feed_update(bot, telegram_update)
    
    return web.Response()

async def on_startup(app):
    """Запускается при старте веб-сервера Vercel."""
    logging.warning("Запуск Webhook. Устанавливаем Webhook...")
    
    # ❗️ Важно: Мы устанавливаем Webhook только один раз при запуске.
    webhook_status = await set_webhook()
    
    if webhook_status:
        logging.warning(f"Webhook установлен: {WEBHOOK_URL}")
    else:
        logging.error("Не удалось установить Webhook.")

    # Создаем команды
    await bot.set_my_commands([
        {"command": "start", "description": "🚀 Запустить бота"},
        # ... (остальные команды) ...
    ])


def create_app():
    """Функция, которую Vercel будет искать для запуска."""
    app = web.Application()
    
    # Назначаем обработчик на путь Webhook
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    
    # Регистрация хука запуска
    app.on_startup.append(on_startup)
    
    # ❗️ Важно: Инициализация БД должна быть здесь
    init_db() 
    
    return app


# --------------------------
# ЗАПУСК (Только для локального тестирования)
# --------------------------
if __name__ == "__main__":
    # Локальный запуск
    logging.basicConfig(level=logging.WARNING)
    # Здесь можно настроить локальный Webhook или Polling для тестирования
    # Но для Vercel эта часть игнорируется
    pass