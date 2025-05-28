# orquestrador.py

from datetime import datetime
import requests
import os
import json

# Armazena nomes temporariamente
usuarios = {}

# Endpoints do middleware
URL_VINCULAR = os.getenv("URL_VINCULAR", "https://telegram-bot-snxj.onrender.com/vincular_nome")
URL_VERIFICAR = os.getenv("URL_VERIFICAR", "https://telegram-bot-snxj.onrender.com/verificar_assinante")

# === Prompts dos agentes ===
PROMPT_VENDEDOR = """
Você é um assistente comercial cordial e persuasivo. Seu papel é apresentar a assinatura de um assistente de produtividade.
Seu objetivo é dar boas-vindas, explicar o valor do produto e encorajar a assinatura com empatia.
"""

PROMPT_CONTROLLER = """
Você é um agente que gerencia dados de assinaturas. Seu papel é validar se o usuário está ativo e responder de forma objetiva e educada.
"""

PROMPT_SUPORTE = """
Você é um assistente de suporte educado, acolhedor e proativo. Sempre que alguém pedir ajuda, você responde com empatia e disposição.
Se não entender a mensagem, pergunte educadamente o que a pessoa precisa.
"""

PROMPT_PLANEJADOR = """
Você é um planejador pessoal focado em produtividade. Seu objetivo é ajudar o usuário a organizar o dia e priorizar tarefas com base em seus objetivos.
"""

# === Função base para consulta ao OpenRouter ===
def consultar_openrouter(prompt):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("API KEY do OpenRouter não encontrada.")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Você é um assistente útil e amigável."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            print("Erro na API:", response.text)
            return None

    except Exception as e:
        print("Erro ao consultar OpenRouter:", e)
        return None

# === Agente: CONTROLLER ===
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

def registrar_nome(username, nome):
    try:
        response = requests.post(URL_VINCULAR, json={"username": username, "nome": nome})
        return response.status_code == 200
    except Exception as e:
        print("Erro ao registrar nome:", e)
        return False

# === Agente: SUPORTE ===
def agente_suporte(texto, nome):
    prompt = f"{PROMPT_SUPORTE}\n\nUsuário ({nome}) disse: {texto}\n\nComo você responderia?"
    resposta = consultar_openrouter(prompt)
    return resposta or f"{nome}, tive um problema para responder com a IA agora. Pode tentar novamente?"

# === Agente: PLANEJADOR ===
def agente_planejador(texto, nome):
    prompt = f"{PROMPT_PLANEJADOR}\n\nUsuário ({nome}) disse: {texto}\n\nComo você ajudaria no planejamento do dia dele?"
    resposta = consultar_openrouter(prompt)
    return resposta or f"{nome}, não consegui planejar agora. Tente novamente mais tarde."

# === Agente: VENDEDOR ===
def saudacao(nome):
    hora = datetime.now().hour
    if hora < 12:
        return f"Bom dia {nome}, tudo bem?"
    elif hora < 18:
        return f"Boa tarde {nome}, tudo bem?"
    else:
        return f"Boa noite {nome}, tudo bem?"

def agente_vendedor(texto, username):
    if username not in usuarios:
        if texto.startswith("/start"):
            return "Olá! Qual é o seu nome?"
        elif "meu nome é" in texto:
            nome = texto.replace("meu nome é", "").strip().title()
            usuarios[username] = nome
            registrar_nome(username, nome)
            saud = saudacao(nome)
            prompt = f"""{PROMPT_VENDEDOR}

O usuário {nome} iniciou a conversa com: \"{texto}\".

Crie uma resposta empática que:
1. Dê boas-vindas.
2. Explique o benefício da assinatura.
3. Envie o link de pagamento: https://pay.kiwify.com.br/iejR3F8
4. Oriente para informar o e-mail da compra após o pagamento, para ativar o acesso."""
            resposta = consultar_openrouter(prompt)
            return resposta or (f"{saud} Percebi que tem interesse em adquirir seu assistente de produtividade.\n"
                                f"Estou te enviando o link para assinatura: https://pay.kiwify.com.br/iejR3F8\n"
                                f"Após efetuar a compra, por favor, me envie o e-mail utilizado para que eu possa associar corretamente sua conta.\n"
                                f"Apenas lembrando que você terá 30 dias para cancelamento.")
        elif texto:
            prompt = f"""{PROMPT_VENDEDOR}

Usuário desconhecido disse: \"{texto}\"

Como responder educadamente pedindo o nome dele?"""
            resposta = consultar_openrouter(prompt)
            return resposta or "Desculpe, não entendi. Você poderia me dizer seu nome, por favor?"

# === Função orquestradora ===
def processar_mensagem(texto, username):
    texto = texto.strip().lower()

    ativo, nome_assinante = verificar_assinante(username)
    if ativo:
        if username not in usuarios:
            usuarios[username] = nome_assinante or "Assinante"
        nome = usuarios[username]
        return agente_planejador(texto, nome)

    if username not in usuarios or not usuarios[username]:
        resposta_vendedor = agente_vendedor(texto, username)
        if resposta_vendedor:
            return resposta_vendedor

    nome = usuarios.get(username, "Usuário")

    if texto.startswith("/vincular"):
        return "Por favor, me envie o seu e-mail da compra para associarmos ao seu usuário."

    resposta_suporte = agente_suporte(texto, nome)
    return resposta_suporte
