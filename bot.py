from flask import Flask, request, jsonify
import requests
import os
from orquestrador import processar_mensagem, verificar_assinante, processar_evento_kiwify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
print("BOT_URL:", BOT_URL)

usuarios = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json

    if "event" in update and "email" in update:
        resultado = processar_evento_kiwify(update)
        return jsonify({"status": resultado}), 200

    message = update.get("message", {}).get("text", "")
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    from_user = update.get("message", {}).get("from", {})
    username = from_user.get("username") or f"user_{from_user.get('id')}"
    nome = from_user.get("first_name", "")

    print(f"username: {username}, nome: {nome}")
    print("Mensagem recebida:", message)

    texto_minusculo = message.lower().strip()

    if texto_minusculo in ["/start", "oi", "olá"]:
        ativo, nome_assinante = verificar_assinante(username)
        if ativo:
            usuarios[username] = nome_assinante or nome
            texto = f"Olá {usuarios[username]}, sua assinatura está ativa. Aproveite seu assistente de planejamento diário!"
        elif nome_assinante:
            usuarios[username] = nome_assinante
            texto = f"Olá {usuarios[username]}, sua assinatura foi cancelada ou expirada. Para reativar, use esse link: https://pay.kiwify.com.br/yZfmggt"
        else:
            usuarios[username] = nome
            texto = f"Olá {usuarios[username]}, tudo bem? Estou aqui para te ajudar a começar com seu assistente de produtividade. Qual é o seu principal objetivo hoje?"

        requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
        return "ok"

    if "@" in message and "." in message:
        email = message.strip().lower()
        try:
            verif = requests.post(os.getenv("URL_VERIFICAR_EMAIL"), json={"email": email})
            dados_verif = verif.json()

            if verif.status_code == 200 and dados_verif.get("assinatura_ativa") is not None:
                if dados_verif.get("assinatura_ativa"):
                    vinculo = requests.post(os.getenv("URL_VINCULAR"), json={"email": email, "username": username, "nome": nome})
                    if vinculo.status_code == 200 and vinculo.json().get("vinculado"):
                        nome_assinante = vinculo.json().get("nome", nome)
                        usuarios[username] = nome_assinante
                        texto = f"E-mail recebido! Acesso ativado para {nome_assinante}. Aproveite seu assistente de produtividade!"
                        requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
                        return "ok"
                else:
                    texto = "Identificamos seu e-mail, mas sua assinatura está inativa ou expirada. Você pode reativá-la aqui: https://pay.kiwify.com.br/yZfmggt"
                    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
                    return "ok"
            else:
                texto = "Não conseguimos localizar seu e-mail na nossa base. Por favor, verifique se digitou corretamente."
                requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
                return "ok"

        except Exception as e:
            print("Erro ao tentar verificar e vincular e-mail:", e)
            texto = "Tivemos um erro ao processar seu e-mail. Por favor, tente novamente."
            requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
            return "ok"

    nome_armazenado = usuarios.get(username, nome)
    resposta = processar_mensagem(message, username, nome_armazenado)
    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": resposta})
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
