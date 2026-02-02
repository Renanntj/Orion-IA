from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ApplicationBuilder,
)

from main import processar_mensagem
from dotenv import load_dotenv
import time
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN não encontrado")

SENHA_ACESSO = os.getenv("SENHA_ACESSO")

usuarios_autenticados = set()
usuarios_aguardando_senha = set()

TEMPO_MINIMO_ENTRE_MSG = 10
ultimo_acesso = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    usuarios_aguardando_senha.add(chat_id)

    await update.message.reply_text(
        "Para acessar o Orion IA digite a senha fornecida por Renan."
    )



async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    chat_id = update.effective_chat.id
    texto = update.message.text.strip()

    if not texto:
        return

    if chat_id not in usuarios_autenticados:

        if chat_id in usuarios_aguardando_senha:
            if texto == SENHA_ACESSO:
                usuarios_autenticados.add(chat_id)
                usuarios_aguardando_senha.remove(chat_id)

                await update.message.reply_text(
                    "Acesso liberado. Pode enviar sua mensagem."
                )
            else:
                await update.message.reply_text(
                    "Senha incorreta. Tente novamente."
                )
            return

        await update.message.reply_text(
            "Envie /start para iniciar o acesso ao Orion IA."
        )
        return

    agora = time.time()
    ultimo = ultimo_acesso.get(chat_id)

    if ultimo and (agora - ultimo) < TEMPO_MINIMO_ENTRE_MSG:
        await update.message.reply_text(
            "Aguarde alguns segundos antes de enviar outra mensagem."
        )
        return

    ultimo_acesso[chat_id] = agora

    resposta = processar_mensagem(texto)
    await update.message.reply_text(resposta)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, responder)
    )

    print("Telegram rodando...")
    application.run_polling()


if __name__ == "__main__":
    main()

