import re
from utils.extrator_buffs import extrair_buffs

DURABILIDADE_REGEX = re.compile(r"\[(\d+)/(\d+)]")

def item_possui_durabilidade(nome_item):
    if not nome_item:
        return False
    return bool(DURABILIDADE_REGEX.match(nome_item))

def extrair_durabilidade(nome_item):
    if not item_possui_durabilidade(nome_item):
        return 0, 0
    match = DURABILIDADE_REGEX.match(nome_item)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0

def reduzir_durabilidade(nome_item):
    if not item_possui_durabilidade(nome_item):
        return nome_item
    match = DURABILIDADE_REGEX.match(nome_item)
    atual, maxima = int(match.group(1)), int(match.group(2))
    novo_valor = max(0, atual - 1)
    item_sem_durabilidade = nome_item[match.end():].strip()
    return f"[{novo_valor}/{maxima}] {item_sem_durabilidade}"

def registrar_uso_equipamentos(lista_itens: list[str], quantidade: int = 1) -> list[str]:
    """
    Subtrai 'quantidade' da durabilidade de cada equipamento da lista.
    Retorna a lista de equipamentos atualizados com nova durabilidade.
    """
    atualizados = []
    for item in lista_itens:
        if not item:
            atualizados.append("")
            continue
        match = DURABILIDADE_REGEX.match(item)
        if not match:
            atualizados.append(item)
            continue
        atual, maximo = int(match.group(1)), int(match.group(2))
        novo_atual = max(0, atual - quantidade)
        item_sem_durabilidade = item[match.end():].strip()
        atualizado = f"[{novo_atual}/{maximo}] {item_sem_durabilidade}"
        atualizados.append(atualizado)
    return atualizados

def extrair_buffs_com_durabilidade(nome_item):
    atual, _ = extrair_durabilidade(nome_item)
    if atual == 0:
        return extrair_buffs(None)
    return extrair_buffs(nome_item)

def extrair_equipamentos_danificados(lista_itens: list[str]) -> list[str]:
    """
    Retorna uma lista com os nomes dos equipamentos cuja durabilidade está zerada.
    """
    danificados = []
    for item in lista_itens:
        atual, _ = extrair_durabilidade(item)
        if atual == 0:
            # Extrai o nome limpo do item (sem a parte da durabilidade)
            partes = item.split("]", 1)
            nome_limpo = partes[1].strip() if len(partes) > 1 else item
            danificados.append(nome_limpo)
    return danificados
