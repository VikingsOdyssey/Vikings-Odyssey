from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu_ferreiro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = (
        "<b>🏺 Forja de Midtheim</b>\n"
        "<i>O fogo molda os bravos. Escolha tua ação:</i>"
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔨 Forjar Equipamento", callback_data="forjar_equipamento")],
        [InlineKeyboardButton("⚙️ Aprimorar Equipamento", callback_data="aprimorar_equipamento")],
        [InlineKeyboardButton("🛠️ Reparar Equipamento", callback_data="reparar_equipamento")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
