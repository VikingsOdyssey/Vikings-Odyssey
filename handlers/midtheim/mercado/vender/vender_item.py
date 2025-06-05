from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
import uuid

ESCOLHER_ITEM, DEFINIR_QTD, DEFINIR_VALOR = range(3)

async def iniciar_venda_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)
    inventario = db.reference(f"{chat_id}/Inventario").get() or {}

    botoes = []
    for item, qtd in inventario.items():
        if isinstance(qtd, int) and qtd > 0:
            botoes.append([InlineKeyboardButton(f"{item} (Você possui: {qtd})", callback_data=f"venderitem_{item}")])

    if not botoes:
        await query.message.reply_text("Você não possui itens para vender.")
        return ConversationHandler.END

    await query.message.reply_text(
        "<b>Qual item deseja vender?</b>",
        reply_markup=InlineKeyboardMarkup(botoes),
        parse_mode="HTML"
    )
    return ESCOLHER_ITEM

async def definir_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = query.data.replace("venderitem_", "")
    context.user_data["item"] = item

    await query.message.reply_text(f"Digite a <b>quantidade</b> de <b>{item}</b> que deseja vender:", parse_mode="HTML")
    return DEFINIR_QTD

async def definir_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qtd = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Quantidade inválida. Digite um número.")
        return DEFINIR_QTD

    chat_id = str(update.effective_chat.id)
    item = context.user_data.get("item")
    atual = db.reference(f"{chat_id}/Inventario/{item}").get() or 0

    if qtd <= 0 or qtd > atual:
        await update.message.reply_text("Quantidade insuficiente no inventário.")
        return ConversationHandler.END

    context.user_data["quantidade"] = qtd
    await update.message.reply_text(f"Agora digite o <b>preço total</b> pela venda dos {qtd} {item}:", parse_mode="HTML")
    return DEFINIR_VALOR

async def confirmar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        preco = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Valor inválido. Digite um número inteiro.")
        return DEFINIR_VALOR

    chat_id = str(update.effective_chat.id)
    item = context.user_data["item"]
    qtd = context.user_data["quantidade"]
    nome = db.reference(f"{chat_id}/Perfil/Nome").get() or "Anônimo"

    # Subtrai do inventário
    inventario_ref = db.reference(f"{chat_id}/Inventario/{item}")
    inventario_ref.set(inventario_ref.get() - qtd)

    # Salva no mercado
    item_id = str(uuid.uuid4())[:8]
    venda = {
        "item": item,
        "quantidade": qtd,
        "preco": preco,
        "vendedor": nome,
        "chat_id": chat_id
    }
    db.reference(f"Mercado/Itens/{item_id}").set(venda)

    await update.message.reply_text(f"✅ {qtd}x {item} colocado à venda por {preco} moedas.")
    return ConversationHandler.END
