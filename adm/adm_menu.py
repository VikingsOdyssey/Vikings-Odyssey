from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.ler_texto import ler_texto

async def menu_adm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    message = update.message or update.callback_query.message
    texto = "teste"
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Estatisticas", callback_data="estatisicas")]
    ])

    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
