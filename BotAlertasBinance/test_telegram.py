from telegram import Bot
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não encontrados no .env")
else:
    bot = Bot(token=TOKEN)
    resp = bot.send_message(chat_id=CHAT_ID, text="Teste do bot — mensagem enviada com sucesso ✅")
    print("Mensagem enviada. OK.")