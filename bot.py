import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure o logging para ver o que está acontecendo
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# SUBSTITUA pelo seu Token do bot (o que você anotou no Word)
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Função para responder ao comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /start"""
    await update.message.reply_text(
        'Olá! Eu sou seu novo bot e estou funcionando perfeitamente! 🤖\n'
        'Digite /help para ver os comandos disponíveis.'
    )

# Função para responder ao comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /help"""
    await update.message.reply_text(
        'Comandos disponíveis:\n'
        '/start - Iniciar o bot\n'
        '/help - Mostrar esta ajuda\n'
        '/teste - Testar se o bot está respondendo'
    )

# Função para responder ao comando /teste
async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /teste"""
    await update.message.reply_text('✅ Bot funcionando perfeitamente!')

def main() -> None:
    """Função principal que inicia o bot"""
    # Verifica se o token foi carregado corretamente
    if not BOT_TOKEN:
        print("Erro: BOT_TOKEN não encontrado nas variáveis de ambiente!")
        return
    
    # Cria a aplicação
    application = Application.builder().token(BOT_TOKEN).build()

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("teste", teste))

    # Inicia o bot (otimizado para Render)
    print("Bot iniciado no Render! Rodando 24/7...")
    application.run_polling(drop_pending_updates=True)