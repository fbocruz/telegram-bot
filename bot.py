from flask import Flask, request
import requests
import os
from orquestrador import processar_mensagem  # Importando o orquestrador

app = Flask(__name__)

# Pegando o token da variável de ambiente no Render
TELEGRAM_TOKEN = os.getenv("7969184483:AAEHfgUFiUmeWIJBpAV6KxjJl7okF02Ud2I")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
print("BOT_URL:", BOT_URL)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    message = update.get("message", {}).get("text", "")
    username = update.get("message", {}).get("from", {}).get("username", "")
    chat_id = update.get("message", {}).get("chat", {}).get("id")

    print("Mensagem recebida:", message)

    if message.lower().startswith("/start"):
        text = f"Olá @{username}, seja bem-vindo! Aqui está seu link de compra: https://pay.kiwify.com.br/iejR3F8"
    elif message.lower().startswith("/vincular"):
        text = "Por favor, me envie o seu e-mail da compra para associarmos ao seu usuário."
    else:
        # Qualquer outra mensagem será tratada pela IA do orquestrador
        text = processar_mensagem(message, username)

    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
