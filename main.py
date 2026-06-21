import asyncio
import logging
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from create_bot import bot, dp, client

# Словник для зберігання історії розмов
MESSAGES_HISTORY = {}
# Максимальна кількість повідомлень в історії
MAX_HISTORY_LEN = 10

# Асинхронна функція запиту до ШІ, яка тепер приймає user_id та історію
async def ask_ai(user_id: int, question: str) -> str:
    try:
        # 1. Якщо користувач пише вперше, створюємо для нього пусту історію
        if user_id not in MESSAGES_HISTORY:
            MESSAGES_HISTORY[user_id] = [
                {"role": "system", "content": "Ти дружній ШІ-помічник на ім'я Jakbyte_AI. Відповідай чітко й лаконічно."}
            ]  
        # 2. Додаємо нове питання користувача в його історію
        MESSAGES_HISTORY[user_id].append({"role": "user", "content": question}) 
        # 3. Обмежуємо розмір історії (тримаємо SYSTEM-промпт + останні повідомлення)
        if len(MESSAGES_HISTORY[user_id]) > MAX_HISTORY_LEN:
            MESSAGES_HISTORY[user_id] = [MESSAGES_HISTORY[user_id][0]] + MESSAGES_HISTORY[user_id][-(MAX_HISTORY_LEN-1):]
        # 4. Відправляємо ВСЮ історію в OpenRouter
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini", 
            messages=MESSAGES_HISTORY[user_id]
        )
        bot_answer = response.choices[0].message.content
        MESSAGES_HISTORY[user_id].append({"role": "assistant", "content": bot_answer})
        return bot_answer
        
    except Exception as e:
        logging.error(f"Помилка OpenRouter API: {e}")
        return "Вибач, виникла помилка при обробці запиту до ШІ. Спробуй ще раз трохи пізніше."

# Створення головного меню з кнопками /start та /help
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")]
    ],
    resize_keyboard=True  
)

# Хендлер для команди /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Скидаємо контекст при команді /start
    if user_id in MESSAGES_HISTORY:
        del MESSAGES_HISTORY[user_id]
        
    welcome_text = (
        f"👋 Вітаю у світі Jakbyte_AI, {username}!\n\n"
        "Тепер у мене є пам'ять! Я пам'ятаю хід нашої бесіди, тож ти можеш ставити мені уточнювальні запитання.\n\n"
        "⚙️ Доступні команди:\n"
        "/start — очистити контекст розмови та перезапустити бота\n"
        "/help — отримати підказку щодо використання\n\n"
        "Про що поспілкуємось? 👇"
    )
    await message.answer(welcome_text, reply_markup=keyboard)

# Хендлер для команди /help
@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "❓ Довідка та корисні поради для роботи з Jakbyte_AI\n\n"
        "• Контекст розмови: я пам'ятаю попередні повідомлення. Ти можеш просто писати: 'А поясни детальніше другий пункт' або 'Переклади попередній код на C++'.\n\n"
        "🛠️ Що робити, якщо я почав плутатися або хочеш почати нову тему?\n"
        "Надішли команду /start — це повністю очистить мою пам'ять і ми почнемо з чистого аркуша."
    )
    await message.answer(help_text)

# Хендлер для обробки усіх текстових повідомлень (запитів до ШІ)
@dp.message()
async def text_user(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    user_id = message.from_user.id
    text = message.text
    answer = await ask_ai(user_id, text)
    await message.answer(answer)

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())