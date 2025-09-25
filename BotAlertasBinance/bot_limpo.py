import os

# leitura manual do .env para evitar problemas com dotenv
def read_dotenv(path):
    d = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                # remover aspas simples/duplas se houver
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                d[k] = v.strip()
    except FileNotFoundError:
        pass
    return d

env = read_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
TOKEN = env.get("TELEGRAM_TOKEN")
CHAT_ID = env.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise SystemExit("TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não encontrados no .env")

from telegram import Bot
bot = Bot(token=TOKEN)

try:
    bot.send_message(chat_id=int(CHAT_ID), text="🚀 Teste do bot_limpo.py — mensagem enviada com sucesso ✅")
    print("Mensagem enviada com sucesso!")
except Exception as e:
    print("ERRO:", e)