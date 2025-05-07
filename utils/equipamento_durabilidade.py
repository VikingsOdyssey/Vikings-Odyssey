import re
from utils.extrator_buffs import extrair_buffs

DURABILIDADE_REGEX = re.compile(r"\[(\d+)/(\d+)]")

def item_possui_durabilidade(nome_item: str) -> bool:
    return bool(nome_item and DURABILIDADE_REGEX.search(nome_item))

def extrair_durabilidade(nome_item: str) -> tuple[int, int]:
    if not item_possui_durabilidade(nome_item):
        return 0, 0
    match = DURABILIDADE_REGEX.search(nome_item)
    return int(match.group(1)), int(match.group(2))

def reduzir_durabilidade(nome_item: str) -> str:
    if not item_possui_durabilidade(nome_item):
        return nome_item
    match = DURABILIDADE_REGEX.search(nome_item)
    atual, maxima = int(match.group(1)), int(match.group(2))
    novo_valor = max(0, atual - 1)
    item_sem_durabilidade = DURABILIDADE_REGEX.sub("", nome_item).strip()
    return f"[{novo_valor}/{maxima}] {item_sem_durabilidade}"

def extrair_equipamentos_danificados(equipado_dict: dict) -> list[str]:
    danificados = []
    for tipo, item in equipado_dict.items():
        dur, _ = extrair_durabilidade(item)
        if dur == 0 and item:
            danificados.append(f"{tipo.capitalize()}: {item}")
    return danificados

def registrar_uso_de_equipado(chat_id: str, db_ref):
    equipado_ref = db_ref.child(f"{chat_id}/Equipado")
    equipado_atual = equipado_ref.get()
    if not equipado_atual:
        return

    atualizado = {}
    for tipo, item in equipado_atual.items():
        atualizado[tipo] = reduzir_durabilidade(item)

    equipado_ref.update(atualizado)
