from flask import Flask, request
import requests
import os
from orquestrador import processar_mensagem  # Importando o orquestrador

app = Flask(__name__)

# Pegando o token da variável de ambiente no Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
print("BOT_URL:", BOT_URL)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    message = update.get("message", {}).get("text", "")
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    from_user = update.get("message", {}).get("from", {})
    username = from_user.get("username") or f"user_{from_user.get('id')}"
    nome = from_user.get("first_name", "")

    print(f"username: {username}, nome: {nome}")
    
    print("Mensagem recebida:", message)

    # Toda mensagem será tratada pelo orquestrador
    resposta = processar_mensagem(message, username, nome)

    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": resposta})
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
