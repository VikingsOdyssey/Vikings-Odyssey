# loot_open.py

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db

# Estrutura das loot boxes: chave = nome da box no banco, valores = itens e range de quantidade
LOOT_BOXES = {
    "Loot_cacada": {
        "Joia_Criacao": (0,1),
        "Madeira": (1, 5),
        "Couro": (1, 5),
        "La": (1, 5),
        "Aco": (1, 5),
        "Pedra": (1, 5),
    },
    "Loot_diario": {
        "Madeira": (0, 3),
        "Couro": (0, 3),
        "La": (0, 3),
        "Aco": (0, 3),
        "Pedra": (0, 3),
    },
    # Adicione mais loot boxes aqui conforme necessidade
}

async def abrir_lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.from_user.id)
    lootbox_nome = query.data.replace("abrir_", "")  # exemplo: "abrir_loot_cacada" vira "loot_cacada"

    if lootbox_nome not in LOOT_BOXES:
        await query.message.reply_text("❌ Loot box desconhecida.")
        return

    ref_inventario = db.reference(f"{chat_id}/Inventario")
    inventario_atual = ref_inventario.get()
    ref_recebimentos = db.reference(f"{chat_id}/Recebimentos")
    recebimentos_atual = ref_recebimentos.get()
    loot_n = recebimentos_atual.get(lootbox_nome) if recebimentos_atual else 0


    if loot_n <= 0:
        await query.message.reply_text("❌ Você não possui essa loot box.")
        return

    # Reduz uma loot box
    nova_quantidade = max(0, loot_n - 1)
    ref_recebimentos.child(lootbox_nome).set(nova_quantidade)

    # Gerar os itens
    recompensas = {}
    for item, (min_qtd, max_qtd) in LOOT_BOXES[lootbox_nome].items():
        quantidade = random.randint(min_qtd, max_qtd)
        if quantidade > 0:
            recompensas[item] = recompensas.get(item, 0) + quantidade
            atual = inventario_atual.get(item, 0)
            ref_inventario.child(item).set(atual + quantidade)

    # Mensagem de retorno
    texto = f"📦 <b>Você abriu uma loot box!</b>\n\n"
    for item, qtd in recompensas.items():
        texto += f"• {item}: +{qtd}\n"

        ref = db.reference(f"{chat_id}")
        perfil = ref.child("Perfil").get()

        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Abrir Loot Diario", callback_data="abrir_Loot_diario")],
        [InlineKeyboardButton("Abrir Loot de Caçada", callback_data="abrir_Loot_cacada")],
        [InlineKeyboardButton("↩️ Voltar", callback_data="inventario")],
        [InlineKeyboardButton("Menu", callback_data=f"menu_{perfil.get("Local_Atual").lower()}")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
