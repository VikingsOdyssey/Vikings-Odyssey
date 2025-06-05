from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
import uuid

ESCOLHER_TIPO_EQUIP, ESCOLHER_EQUIPAMENTO, DEFINIR_VALOR = range(3)

TIPOS_EQUIPAMENTO = ["Armas", "Elmos", "Armaduras", "Calcas", "Botas", "Amuletos"]

async def iniciar_venda_equipamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    botoes = [[InlineKeyboardButton(tipo, callback_data=f"vender_tipo_{tipo}")] for tipo in TIPOS_EQUIPAMENTO]
    await query.message.reply_text(
        "<b>Escolha o tipo de equipamento que deseja vender:</b>",
        reply_markup=InlineKeyboardMarkup(botoes),
        parse_mode="HTML"
    )
    return ESCOLHER_TIPO_EQUIP

async def escolher_equipamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo = query.data.replace("vender_tipo_", "")
    context.user_data["tipo_equip"] = tipo

    chat_id = str(query.from_user.id)
    equipamentos = db.reference(f"{chat_id}/Equipamentos/{tipo}").get() or {}

    botoes = []
    for slot, valor in equipamentos.items():
        if valor:
            botoes.append([InlineKeyboardButton(valor, callback_data=f"vender_eq_{slot}")])

    if not botoes:
        await query.message.reply_text("❌ Você não possui equipamentos desse tipo para vender.")
        return ConversationHandler.END

    await query.message.reply_text(
        f"<b>Escolha o equipamento que deseja vender:</b>",
        reply_markup=InlineKeyboardMarkup(botoes),
        parse_mode="HTML"
    )
    return ESCOLHER_EQUIPAMENTO

async def definir_valor_equip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slot = query.data.replace("vender_eq_", "")
    context.user_data["slot"] = slot

    await query.message.reply_text("Digite o <b>preço</b> de venda do equipamento:", parse_mode="HTML")
    return DEFINIR_VALOR

async def confirmar_venda_equip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        preco = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Valor inválido. Digite um número inteiro.")
        return DEFINIR_VALOR

    chat_id = str(update.effective_chat.id)
    tipo = context.user_data["tipo_equip"]
    slot = context.user_data["slot"]
    nome = db.reference(f"{chat_id}/Perfil/Nome").get() or "Anônimo"

    item_ref = db.reference(f"{chat_id}/Equipamentos/{tipo}/{slot}")
    item = item_ref.get()

    if not item:
        await update.message.reply_text("❌ Equipamento não encontrado.")
        return ConversationHandler.END

    # Remove o equipamento do jogador
    item_ref.set("")

    # Salva no mercado
    item_id = str(uuid.uuid4())[:8]
    venda = {
        "tipo": tipo,
        "item": item,
        "preco": preco,
        "vendedor": nome,
        "chat_id": chat_id
    }
    db.reference(f"Mercado/Equipamentos/{item_id}").set(venda)

    await update.message.reply_text(f"✅ Equipamento colocado à venda por {preco} moedas.")
    return ConversationHandler.END
