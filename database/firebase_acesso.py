from database.firebase import get_db_ref

def get_valor(chat_id: str, path: str, default=None):
    """
    Lê um valor do Firebase usando o caminho relativo ao chat_id.
    Exemplo: path='Perfil/nome'
    """
    ref = get_db_ref(f"{chat_id}/{path}")
    return ref.get() if ref.get() is not None else default

def set_valor(chat_id: str, path: str, valor):
    """
    Define um valor no Firebase em um caminho relativo ao chat_id.
    Exemplo: path='Perfil/nome', valor='Arthur'
    """
    ref = get_db_ref(f"{chat_id}/{path}")
    ref.set(valor)

def update_valores(chat_id: str, path: str, dados: dict):
    """
    Faz update de um dicionário em um caminho relativo ao chat_id.
    Exemplo: path='Perfil', dados={'xp': 100, 'ouro': 50}
    """
    ref = get_db_ref(f"{chat_id}/{path}")
    ref.update(dados)
