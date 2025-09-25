import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = requests.get(url).json()
print(resp)