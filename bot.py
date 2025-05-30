from flask import Flask, request
import requests
import os
from orquestrador import processar_mensagem, verificar_assinante  # Importando também a verificação

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

    # === VALIDAÇÃO DE ASSINATURA NO INÍCIO DA CONVERSA ===
    texto_minusculo = message.lower().strip()
    if texto_minusculo == "/start" or texto_minusculo == "oi" or texto_minusculo == "olá":
        ativo, nome_assinante = verificar_assinante(username)
        if ativo:
            saud = f"Olá {nome_assinante or nome}, sua assinatura está ativa. Aproveite seu assistente de planejamento diário!"
            requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": saud})
            return "ok"
        elif nome_assinante:
            saud = f"Olá {nome_assinante or nome}, sua assinatura foi cancelada ou expirada. Para reativar, use esse link: https://pay.kiwify.com.br/yZfmggt"
            requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": saud})
            return "ok"

    # === VALIDAÇÃO DE ASSINATURA POR E-MAIL ===
    if "@" in message and "." in message:
        email = message.strip().lower()
        try:
            response = requests.post(os.getenv("URL_VINCULAR"), json={"email": email, "username": username, "nome": nome})
            if response.status_code == 200:
                dados = response.json()
                if dados.get("vinculado"):
                    saud = f"E-mail recebido! Acesso ativado para {dados.get('nome', nome)}. Aproveite seu assistente de produtividade!"
                    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": saud})
                    return "ok"
        except Exception as e:
            print("Erro ao tentar vincular e-mail:", e)

    # Toda outra mensagem será tratada pelo orquestrador
    resposta = processar_mensagem(message, username, nome)
    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": resposta})
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
