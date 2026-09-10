import json
import logging
import os
from threading import Thread
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask

# Твои данные
TOKEN = "8874357037:AAHu8dEk97Mb9NT9MCfpEPCpDj7z6NQnKRo"
ADMIN_ID = 8870678654

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"notes": [], "alarms": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    user_name = (
        "Хозяин" if message.from_user.id == ADMIN_ID else message.from_user.first_name
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📝 Мои заметки", callback_data="my_notes"),
        types.InlineKeyboardButton("⏰ Будильники", callback_data="my_alarms"),
    )
    await message.answer(
        f"Привет, {user_name}! Я твой бот-помощник техникум-проекта. Выбери действие:",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(text="my_notes")
async def show_notes_callback(call: types.CallbackQuery):
    data = load_data()
    notes = data.get("notes", [])

    if not notes:
        await call.message.answer("У тебя пока нет сохраненных заметок.")
        await call.answer()
        return

    response = "📝 **Твои заметки:**\n\n"
    for note in notes:
        priority = note.get("priority", "Routine")
        emoji = (
            "🟢" if priority == "Routine" else "🟠" if priority == "Medium" else "🔴"
        )
        response += f"{emoji} **{note.get('title')}**\n{note.get('content')}\n\n"

    await call.message.answer(response, parse_mode="Markdown")
    await call.answer()


@dp.message_handler(commands=["notes"])
async def show_notes_command(message: types.Message):
    data = load_data()
    notes = data.get("notes", [])

    if not notes:
        await message.answer("У тебя пока нет сохраненных заметок.")
        return

    response = "📝 **Твои заметки:**\n\n"
    for note in notes:
        priority = note.get("priority", "Routine")
        emoji = (
            "🟢" if priority == "Routine" else "🟠" if priority == "Medium" else "🔴"
        )
        response += f"{emoji} **{note.get('title')}**\n{note.get('content')}\n\n"

    await message.answer(response, parse_mode="Markdown")


# --- Настройка веб-сервера для Render ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"  # Исправлено: добавлено return и кавычки

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()


# --- Единая точка входа ---
if __name__ == "__main__":
    # Запускаем Flask-сервер в фоне для Render
    keep_alive()
    
    # Запускаем планировщик и самого бота
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
