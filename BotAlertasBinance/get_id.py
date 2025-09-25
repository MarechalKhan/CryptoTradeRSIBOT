from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)

updates = bot.get_updates()
for u in updates:
    if u.message:
        print("chat.id:", u.message.chat.id, "| Nome:", u.message.chat.chat_id)