import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import os

TOKEN = os.getenv("BOT_TOKEN")

TARGET_CHAT = -1003098405352
TARGET_THREAD = 4708

bot = Bot(token=TOKEN)
dp = Dispatcher()


def calc(culture, min_price, max_price, current):
    avg24 = (min_price + max_price) / 2
    target = min_price * 1.05

    if current > avg24:
        sell_advice = "📈 Продавать выгодно!"
    elif current >= target:
        sell_advice = "⚖️ Цена в норме, можно подождать"
    else:
        sell_advice = "⏳ Ждать лучшей цены"

    if current <= avg24:
        buy_advice = "🌱 Покупать семена выгодно"
    else:
        buy_advice = "⏳ Подождать с покупкой семян"

    return {
        "sell": f"💰 {culture}\n• Целевая: {target:.2f}\n• Средняя: {avg24:.2f}\n• Текущая: {current:.2f}\n\n{sell_advice}",
        "buy": f"🌱 {culture}\n• Целевая: {target:.2f}\n• Средняя: {avg24:.2f}\n• Текущая: {current:.2f}\n\n{buy_advice}"
    }


@dp.message(F.chat.id == TARGET_CHAT)
async def handle_all(message: Message):
    if getattr(message, "message_thread_id", None) != TARGET_THREAD:
        return

    text = message.text or ""
    cmd = text.split("@")[0]

    if cmd == "/start":
        await message.answer(
            "Привет! 👋\n"
            "Формат:\n"
            "Культура min max current\n"
        )
        return

    parts = text.split()
    if len(parts) != 4:
        await message.answer("Неверный формат!")
        return

    culture, min_p, max_p, current = parts
    try:
        min_p, max_p, current = map(float, [min_p, max_p, current])
    except:
        await message.answer("Неверные числа!")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💸 Продажа", callback_data=f"sell_{culture}_{min_p}_{max_p}_{current}"),
            InlineKeyboardButton(text="🌱 Покупка", callback_data=f"buy_{culture}_{min_p}_{max_p}_{current}")
        ]
    ])

    await message.answer(f"Выбери действие по {culture}:", reply_markup=kb)


@dp.callback_query()
async def handle_buttons(cb: CallbackQuery):
    try:
        action, culture, min_p, max_p, current = cb.data.split("_")
        min_p, max_p, current = map(float, [min_p, max_p, current])
    except:
        await cb.answer("Ошибка!", show_alert=True)
        return

    res = calc(culture, min_p, max_p, current)
    await cb.message.edit_text(res[action])
    await cb.answer()


async def start_bot():
    print("Bot started!")
    await dp.start_polling(bot)
