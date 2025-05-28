# orquestrador.py

from datetime import datetime

# Armazena nomes temporariamente (poderia ser melhor em banco/planilha futuramente)
usuarios = {}
assinantes = set()  # Poderia ser alimentado a partir da planilha

# Função para saudação com base no horário atual
def saudacao(nome):
    hora = datetime.now().hour
    if hora < 12:
        return f"Bom dia {nome}, tudo bem?"
    elif hora < 18:
        return f"Boa tarde {nome}, tudo bem?"
    else:
        return f"Boa noite {nome}, tudo bem?"

# Função principal de processamento da mensagem
def processar_mensagem(texto, username):
    texto = texto.strip().lower()

    if username not in usuarios:
        if texto.startswith("meu nome é"):
            nome = texto.replace("meu nome é", "").strip().title()
            usuarios[username] = nome
            saud = saudacao(nome)
            return (f"{saud} Percebi que tem interesse em adquirir seu assistente de produtividade, "
                    f"que ocorre através de uma assinatura mensal e vai te ajudar todos os dias em seu planejamento diário.\n"
                    f"Estou te enviando o link para assinatura: https://pay.kiwify.com.br/iejR3F8\n"
                    f"Apenas lembrando que você terá 30 dias para cancelamento.")
        else:
            return "Antes de começarmos, qual é o seu nome? Responda assim: 'Meu nome é Fulano'"

    nome = usuarios[username]

    # Simulando se é assinante para já dar boas-vindas sem precisar de /vincular
    if username in assinantes:
        return (f"Muito feliz por entrar para esse seleto grupo de pessoas que quer melhorar sua produtividade.\n"
                f"Bem-vindo ao seu assistente de produtividade, {nome}. Comece hoje mesmo a planejar seu dia!")

    if texto.startswith("/vincular"):
        return "Por favor, me envie o seu e-mail da compra para associarmos ao seu usuário."

    if "ajuda" in texto:
        return f"Oi {nome}, claro! Estou aqui para te ajudar. O que você precisa?"

    return f"{nome}, recebi sua mensagem: '{texto}'. Em breve terei mais funções!"
