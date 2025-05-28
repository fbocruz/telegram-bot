# orquestrador.py

def processar_mensagem(texto, username):
    # Aqui futuramente usaremos múltiplos agentes inteligentes
    # Por enquanto, apenas devolve uma resposta padrão

    if "ajuda" in texto.lower():
        return f"Oi @{username}, como posso te ajudar hoje?"

    return f"@{username}, recebi sua mensagem: '{texto}'. Em breve terei mais funções!"
