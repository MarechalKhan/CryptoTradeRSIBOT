import os
from dotenv import load_dotenv

load_dotenv()
print("TOKEN:", os.getenv("TELEGRAM_TOKEN"))
print("CHAT_ID:", os.getenv("TELEGRAM_CHAT_ID"))