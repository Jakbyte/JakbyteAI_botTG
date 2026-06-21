import os
from aiogram import Bot, Dispatcher
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)