import os
import logging
import pandas as pd
from binance.client import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Tokens e chaves via variáveis de ambiente (Render)
BOT_TOKEN = os.getenv("8435677944:AAHJTLyv0iUeM-NgIlXZ_E1PVxz6SahknCA")
BINANCE_KEY = os.getenv("jpFeo8Aa5cHgqFBNpUICjOnMgUSLHbgpmR7Rsf4XEJpkqCxb8UfnLLlT2L9XE7u3")
BINANCE_SECRET = os.getenv("tLzoyxd2ElwxKdhpjMPfeTPKmkqtK5GMmmiC0bChKs6c02nSCGXwRRDoSgjgzwfQ")

# Conecta na Binance
client = Client(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET)

# Função para calcular RSI (simplificada)
def calculate_rsi(data, period=14):
    delta = data.diff()
    ganho = delta.clip(lower=0).rolling(window=period).mean()
    perda = -delta.clip(upper=0).rolling(window=period).mean()
    rs = ganho / perda
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]  # último valor

# Verificação do RSI
async def check_rsi(context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pegamos só algumas moedas para teste (evita travar)
        symbols = [s['symbol'] for s in client.futures_exchange_info()['symbols']]
        top_symbols = symbols[:5]  # ⚠️ limita a 5 só para começar tranquilo

        for sym in top_symbols:
            # Baixamos candles de 5min
            klines = client.futures_klines(symbol=sym, interval='5m', limit=100)
            closes = pd.Series([float(k[4]) for k in klines])

            rsi = calculate_rsi(closes)
            msg = None
            if rsi > 90:
                msg = f"⚠️ {sym}: RSI={rsi:.2f} → SOBRECOMPRADO FORTE!"
            elif rsi > 67:
                msg = f"{sym}: RSI={rsi:.2f} → Sobrecomprado."
            elif rsi < 10:
                msg = f"⚠️ {sym}: RSI={rsi:.2f} → SOBREVENDA FORTE!"
            elif rsi < 33:
                msg = f"{sym}: RSI={rsi:.2f} → Sobrevendido."

            if msg:
                await context.bot.send_message(chat_id=context.job.chat_id, text=msg)

    except Exception as e:
        logging.warning(f"Erro monitorando pares: {e}")

# Comando start → ativa monitoramento
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot RSI iniciado! Monitorando moedas a cada 5 minutos...")
    # Executa a checagem de 5 em 5 minutos, começando daqui 10s
    context.job_queue.run_repeating(check_rsi, interval=300, first=10, chat_id=update.effective_chat.id)

# Comando help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponíveis:\n/start → inicia monitoramento\n/help → mostra ajuda")

def main():
    if not BOT_TOKEN:
        print("❌ Erro: BOT_TOKEN não encontrado!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("✅ Bot online no Render (monitorando RSI)")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()