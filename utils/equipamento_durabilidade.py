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

def extrair_equipamentos_danificados(equipado):
    danificados = []

    for nome, item in {
        "arma": equipado.arma,
        "elmo": equipado.elmo,
        "armadura": equipado.armadura,
        "botas": equipado.bota,
        "calca": equipado.calca,
        "amuleto": equipado.amuleto
    }.items():
        atual, _ = extrair_durabilidade(item)
        if atual == 0 and item:
            danificados.append(f"{nome} ({item})")

    return danificados

def registrar_uso_de_equipado(equipado):
    for slot in ["arma", "elmo", "armadura", "bota", "calca", "amuleto"]:
        equipamento = getattr(equipado, slot)
        if equipamento and '/' in equipamento:
            atual, maximo = extrair_durabilidade(equipamento)
            if atual > 0:
                novo_valor = f"[{max(atual - 1, 0)}/{maximo}] {equipamento.split(']', 1)[-1].strip()}"
                setattr(equipado, slot, novo_valor)
