from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.config import SessionLocal
from database.models import Equipado

def encontrar_primeiro_slot_vazio(container):
    for i in range(1, 11):
        slot = f"Item{i}"
        if getattr(container, slot) in [None, ""]:
            return slot
    return None

def mover_equipamento_para_inventario(jogador, inventario, equipado, tipo):

    item_atual = getattr(equipado, tipo)
    if not item_atual:
        return "Voce nao está equipado!"
    slot_vazio = encontrar_primeiro_slot_vazio(inventario)
    if not slot_vazio:
        return False
    setattr(inventario, slot_vazio, item_atual)
    setattr(equipado, tipo, "")
    return f"Você desequipou <b>{item_atual}</b>!"

def equipar_item(jogador, inventario, equipado, tipo_equipamento, slot_nome):
    """
    Equipa um item de um inventário de equipamentos (como Amuleto, Arma, etc) para o slot adequado em `equipado`.
    """
    novo_item = getattr(inventario, slot_nome)
    if not novo_item:
        return "Este slot está vazio."

    # Remove item anterior, se existir
    item_antigo = getattr(equipado, tipo_equipamento)
    if item_antigo:
        # Devolve ao inventário
        for i in range(1, 11):
            campo = f"Item{i}"
            if not getattr(inventario, campo):
                setattr(inventario, campo, item_antigo)
                break

    # Equipa o novo item e limpa o slot do inventário
    setattr(equipado, tipo_equipamento, novo_item)
    setattr(inventario, slot_nome, "")

    return f"Você equipou <b>{novo_item}</b>!"


def teclado_pos_equipar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])