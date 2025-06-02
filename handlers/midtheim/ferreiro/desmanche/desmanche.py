from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
from utils.ler_texto import ler_texto

ESCOLHER_TIPO, ESCOLHER_ITEM = range(2)
TIPOS_EQUIPAMENTO = ["Armas", "Elmos", "Armaduras", "Calcas", "Botas", "Amuletos"]

async def menu_desmanche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto("../texts/midtheim/ferreiro/desmanche/desmanche.txt")
    teclado = [[InlineKeyboardButton(tipo, callback_data=f"desmanche_tipo_{tipo}")] for tipo in TIPOS_EQUIPAMENTO]
    teclado.append([InlineKeyboardButton("Voltar", callback_data="ferreiro")])
    await query.message.reply_text(text=texto, reply_markup=InlineKeyboardMarkup(teclado), parse_mode="HTML")
    return ESCOLHER_TIPO

async def escolher_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo = query.data.replace("desmanche_tipo_", "")
    chat_id = str(query.from_user.id)
    equipamentos = db.reference(f"{chat_id}/Equipamentos/{tipo}").get()
    context.user_data["tipo_desmanche"] = tipo
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="desmanche_menu")]])
    botoes = []
    for slot, item in equipamentos.items():
        if item:
            botoes.append([InlineKeyboardButton(item, callback_data=f"desmanche_item_{slot}")])
    if not botoes:
        await query.message.reply_text("⚠️ Você não possui itens desse tipo para desmontar.", reply_markup=teclado)
        return ConversationHandler.END
    botoes.append([InlineKeyboardButton("Voltar", callback_data="desmanche_menu")])
    await query.message.reply_text(
        f"🧩 <b>Escolha o item que deseja desmontar ({tipo}):</b>",
        reply_markup=InlineKeyboardMarkup(botoes),
        parse_mode="HTML"
    )
    return ESCOLHER_ITEM

async def desmontar_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slot = query.data.replace("desmanche_item_", "")
    chat_id = str(query.from_user.id)
    tipo = context.user_data.get("tipo_desmanche")
    item_ref = db.reference(f"{chat_id}/Equipamentos/{tipo}/{slot}")
    item = item_ref.get()
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="desmanche_menu")]])
    if not item:
        await query.message.reply_text("⚠️ Este item já foi desmontado ou não existe.", reply_markup=teclado)
        return ConversationHandler.END
    item_ref.set("")  # Deleta o item
    inventario_ref = db.reference(f"{chat_id}/Inventario")
    inventario_ref.child("Joia_Aperfeicoamento").transaction(lambda val: (val or 0) + 1)
    await query.message.reply_text(
        f"🧨 <b>Item desmontado:</b> {item}\n"
        f"💎 Você recebeu 1x Joia de Aprimoramento.",
        reply_markup=teclado,
        parse_mode="HTML"
    )
    return ConversationHandler.END
