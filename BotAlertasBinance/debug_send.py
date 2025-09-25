# debug_send.py — força leitura manual do .env e tenta get_chat + send_message
import os, time
from telegram import Bot

# Função simples para ler .env na mesma pasta e retornar dict
def read_dotenv(path):
    d = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                # remover aspas simples/duplas se houver
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                # trim spaces
                v = v.strip()
                d[k] = v
    except FileNotFoundError:
        print("Arquivo .env não encontrado:", path)
    return d

env_path = os.path.join(os.path.dirname(__file__), ".env")
env = read_dotenv(env_path)
# colocar no os.environ apenas se presente
for k,v in env.items():
    os.environ[k] = v

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")

print("cwd:", os.getcwd())
print("env_path:", env_path)
print("dotenv read TELEGRAM_TOKEN present:", bool(env.get("TELEGRAM_TOKEN")), "len:", len(env.get("TELEGRAM_TOKEN") or ""))
print("dotenv read TELEGRAM_CHAT_ID repr:", repr(env.get("TELEGRAM_CHAT_ID")))
print("os.environ TELEGRAM_TOKEN present:", bool(TOKEN), "len:", len(TOKEN) if TOKEN else 0)
print("os.environ TELEGRAM_CHAT_ID repr:", repr(CHAT))

if not TOKEN:
    print("Erro: TELEGRAM_TOKEN nao encontrado apos leitura manual. Abra .env e verifique.")
    raise SystemExit(1)

# converter chat id quando possivel
try:
    CHAT_int = int(CHAT)
except Exception:
    CHAT_int = CHAT

bot = Bot(token=TOKEN)

# tentar get_chat
try:
    info = bot.get_chat(chat_id=CHAT_int)
    print("get_chat OK. type:", getattr(info, 'type', None), "title/username/first_name:", getattr(info, 'title', None), getattr(info, 'username', None), getattr(info, 'first_name', None))
except Exception as e:
    print("get_chat ERROR:", type(e).__name__, e)

# tentar enviar mensagem
try:
    r = bot.send_message(chat_id=CHAT_int, text="DEBUG_FINAL: teste de envio direto (debug_send.py)")
    print("send_message OK. message_id:", getattr(r, 'message_id', None))
except Exception as e:
    print("send_message ERROR:", type(e).__name__, e)