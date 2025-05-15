from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db

def encontrar_primeiro_slot_vazio(container_dict):
    for i in range(1, 11):
        slot = f"Item{i}"
        if not container_dict.get(slot):
            return slot
    return None


def mover_equipamento_para_inventario(inventario_ref, equipado_ref, tipo):
    equipado = equipado_ref.get()
    inventario = inventario_ref.get()

    item_atual = equipado.get(tipo)
    if not item_atual:
        return "Você não está com um amuleto equipado!"

    slot_vazio = encontrar_primeiro_slot_vazio(inventario)
    if not slot_vazio:
        return "Seu inventário de amuletos está cheio!"

    # Atualiza dados no Firebase
    inventario_ref.child(slot_vazio).set(item_atual)
    equipado_ref.child(tipo).set("")
    return f"Você desequipou <b>{item_atual}</b>!"


def equipar_item(inventario_ref, equipado_ref, tipo_equipamento, slot_nome):
    inventario = inventario_ref.get()
    equipado = equipado_ref.get()

    novo_item = inventario.get(slot_nome)
    if not novo_item:
        return "Este slot está vazio."

    item_antigo = equipado.get(tipo_equipamento)
    if item_antigo:
        for i in range(1, 11):
            campo = f"Item{i}"
            if not inventario.get(campo):
                inventario_ref.child(campo).set(item_antigo)
                break

    # Equipa novo item
    equipado_ref.child(tipo_equipamento).set(novo_item)
    inventario_ref.child(slot_nome).set("")

    return f"Você equipou <b>{novo_item}</b>!"

def teclado_pos_equipar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu", callback_data=f"start")]
    ])