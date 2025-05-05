# bot/utils/equipamentos.py
from database.config import SessionLocal
from database.models import Jogador, Equipado, Arma, Elmo, Armadura, Calca, Bota, Amuleto

TIPOS_EQUIPAMENTO = {
    "arma": Arma,
    "elmo": Elmo,
    "armadura": Armadura,
    "calca": Calca,
    "bota": Bota,
    "amuleto": Amuleto,
}

def get_equipamento_model(tipo: str):
    return TIPOS_EQUIPAMENTO.get(tipo)

def mover_item_para_equipado(jogador, equipado, inventario, tipo, slot_index):
    slot_nome = f"Item{slot_index}"
    item = getattr(inventario, slot_nome)

    if not item:
        return None, "Este slot está vazio!"

    antigo_item = getattr(equipado, tipo)
    setattr(equipado, tipo, item)
    setattr(inventario, slot_nome, None)

    if antigo_item:
        for i in range(1, 11):
            slot = f"Item{i}"
            if getattr(inventario, slot) in [None, ""]:
                setattr(inventario, slot, antigo_item)
                break

    return item, None

def desequipar_item(jogador, equipado, inventario, tipo):
    item_atual = getattr(equipado, tipo)
    if item_atual:
        for i in range(1, 11):
            slot = f"Item{i}"
            if getattr(inventario, slot) in [None, ""]:
                setattr(inventario, slot, item_atual)
                setattr(equipado, tipo, None)
                return True
    return False
