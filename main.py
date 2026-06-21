import asyncio
import logging
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from create_bot import bot, dp, client

async def ask_ai(question: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini", 
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Помилка OpenRouter API: {e}")
        return "Вибач, виникла помилка при обробці запиту до ШІ. Спробуй ще раз трохи пізніше."

# Створення головного меню
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")]
    ],
    resize_keyboard=True  
)

# Хендлер для команди /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    username = message.from_user.first_name
    welcome_text = (
        f"👋 Вітаю у світі Jakbyte_AI, {username}!\n\n"
        "Я готовий до роботи. Надішли мені будь-яке запитання, задачу, "
        "шматок коду для перевірки або тему для роздумів, і я миттєво дам відповідь.\n\n"
        "⚙️ Доступні команди:\n"
        "/start — перезапустити бота та викликати це меню\n"
        "/help — отримати підказку щодо використання\n\n"
        "Який запит у тебе готовий на зараз? Напиши мені! 👇"
    )
    await message.answer(welcome_text, reply_markup=keyboard)

# Хендлер для команди /help
@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "❓ Довідка та корисні поради для роботи з Jakbyte_AI\n\n"
        "Я створений, щоб розуміти звичайну людську мову, тому тобі не потрібно вчити спеціальні команди. "
        "Просто пиши свій запит у чат, наче спілкуєшся з колегою або другом.\n\n"
        "💡 Клика порад для найкращого результату:\n"
        "• Будь конкретним: чим детальніше ти опишеш задачу, тим точнішою буде відповідь.\n"
        "• Форматуй код: використовуй теги форматування Telegram, щоб мені було зручніше його аналізувати.\n"
        "• Контекст розмови: наразі кожен запит обробляється окремо.\n\n"
        "🛠️ Що робити, якщо бот не відповідає або завис?\n"
        "Надішли команду /start — це оновить твою сесію."
    )
    await message.answer(help_text)

# Хендлер для обробки усіх текстових повідомлень (запитів до ШІ)
@dp.message()
async def text_user(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    text = message.text
    answer = await ask_ai(text)
    await message.answer(answer)

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())