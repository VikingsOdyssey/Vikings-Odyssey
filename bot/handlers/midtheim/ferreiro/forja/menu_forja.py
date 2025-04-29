from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu_forja_equipamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = (
        "<b>🔨 Forja de Equipamentos</b>\n"
        "<i>Escolha o tipo de equipamento que deseja forjar:</i>"
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Arma", callback_data="forjar_arma")],
        [InlineKeyboardButton("🪖 Elmo", callback_data="forjar_elmo")],
        [InlineKeyboardButton("🥋 Armadura", callback_data="forjar_armadura")],
        [InlineKeyboardButton("👖 Calça", callback_data="forjar_calca")],
        [InlineKeyboardButton("🥾 Bota", callback_data="forjar_bota")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="forja")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
