# orquestrador.py

from datetime import datetime
import requests
import os

# Armazena nomes temporariamente
usuarios = {}
assinantes = set()  # Simulado. Idealmente vem da planilha.

# Endpoints do middleware

URL_VINCULAR = os.getenv("URL_VINCULAR", "https://kiwify-middleware.onrender.com/vincular_nome")
URL_VERIFICAR = os.getenv("URL_VERIFICAR", "https://kiwify-middleware.onrender.com/verificar_assinante")

# Função para saudação com base no horário
def saudacao(nome):
    hora = datetime.now().hour
    if hora < 12:
        return f"Bom dia {nome}, tudo bem?"
    elif hora < 18:
        return f"Boa tarde {nome}, tudo bem?"
    else:
        return f"Boa noite {nome}, tudo bem?"

# Função para registrar nome + username no middleware (planilha)
def registrar_nome(username, nome):
    try:
        response = requests.post(URL_VINCULAR, json={"username": username, "nome": nome})
        return response.status_code == 200
    except Exception as e:
        print("Erro ao registrar nome:", e)
        return False

# Função para verificar se o usuário é assinante
def verificar_assinante(username):
    try:
        response = requests.post(URL_VERIFICAR, json={"username": username})
        if response.status_code == 200:
            dados = response.json()
            return dados.get("assinatura_ativa", False), dados.get("nome", "")
        return False, ""
    except Exception as e:
        print("Erro na verificação de assinante:", e)
        return False, ""

# Função principal de processamento da mensagem
def processar_mensagem(texto, username):
    texto = texto.strip().lower()

    # Verifica se já é assinante
    ativo, nome_assinante = verificar_assinante(username)
    if ativo:
        if username not in usuarios:
            usuarios[username] = nome_assinante or "Assinante"
        return (f"Muito feliz por entrar para esse seleto grupo de pessoas que quer melhorar sua produtividade.\n"
                f"Bem-vindo ao seu assistente de produtividade, {usuarios[username]}. Comece hoje mesmo a planejar seu dia!")

    if username not in usuarios:
        if texto.startswith("/start"):
            return "Antes de começarmos, qual é o seu nome? Responda assim: 'Meu nome é Fulano'"
        if texto.startswith("meu nome é"):
            nome = texto.replace("meu nome é", "").strip().title()
            usuarios[username] = nome
            registrar_nome(username, nome)
            saud = saudacao(nome)
            return (f"{saud} Percebi que tem interesse em adquirir seu assistente de produtividade, "
                    f"que ocorre através de uma assinatura mensal e vai te ajudar todos os dias em seu planejamento diário.\n"
                    f"Estou te enviando o link para assinatura: https://pay.kiwify.com.br/yZfmggt\n"
                    f"Apenas lembrando que você terá 30 dias para cancelamento.")
        else:
            return "Antes de começarmos, qual é o seu nome? Responda assim: 'Meu nome é Fulano'"

    nome = usuarios[username]

    if texto.startswith("/vincular"):
        return "Por favor, me envie o seu e-mail da compra para associarmos ao seu usuário."

    if "ajuda" in texto:
        return f"Oi {nome}, claro! Estou aqui para te ajudar. O que você precisa?"

    return f"{nome}, recebi sua mensagem: '{texto}'. Em breve terei mais funções!"
