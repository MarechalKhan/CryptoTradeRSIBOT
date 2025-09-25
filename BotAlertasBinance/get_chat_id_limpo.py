import requests

# coloque aqui o token do seu bot válido
TOKEN = "8205737231:AAFkVHTWGCTzznv6HHJkyiZAztXDTq_MV2M"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

resp = requests.get(url).json()
print(resp)