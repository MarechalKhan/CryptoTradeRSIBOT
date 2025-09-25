import os, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("TELEGRAM_TOKEN nao definido no .env")
    raise SystemExit(1)

url = f"https://api.telegram.org/bot{TOKEN}/getMe"
try:
    r = requests.get(url, timeout=10)
    j = r.json()
    print(j)
    if j.get("ok"):
        print("Token válido. Bot info:", j.get("result"))
    else:
        print("getMe retornou erro:", j)
except Exception as e:
    print("Erro ao verificar token:", e)