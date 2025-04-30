from utils.extrator_buffs import extrair_buffs


def item_possui_durabilidade(nome_item):
    if not nome_item:
        return False
    return nome_item.startswith("[") and "/" in nome_item.split()[0]


def extrair_durabilidade(nome_item):
    if not item_possui_durabilidade(nome_item):
        return 0, 0
    durabilidade_raw = nome_item.split()[0].strip("[]")
    atual, maxima = map(int, durabilidade_raw.split("/"))
    return atual, maxima


def reduzir_durabilidade(nome_item):
    if not item_possui_durabilidade(nome_item):
        return nome_item

    partes = nome_item.split(" ", 1)
    durabilidade_raw = partes[0].strip("[]")
    atual, maxima = map(int, durabilidade_raw.split("/"))
    novo_valor = max(0, atual - 1)
    nova_tag = f"[{novo_valor}/{maxima}]"

    return f"{nova_tag} {partes[1]}"


def extrair_buffs_com_durabilidade(nome_item):
    atual, _ = extrair_durabilidade(nome_item)
    if atual == 0:
        return extrair_buffs(None)
    return extrair_buffs(nome_item)
