from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.ler_texto import ler_texto

async def forja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto('../texts/midtheim/ferreiro/forja/forja.txt')
    message = update.message or update.callback_query.message
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Forjar Arma", callback_data="forja_arma")],
        [InlineKeyboardButton("Forjar Elmo", callback_data="forja_elmo")],
        [InlineKeyboardButton("Forjar Armadura", callback_data="forja_armadura")],
        [InlineKeyboardButton("Forjar Calça", callback_data="forja_calca")],
        [InlineKeyboardButton("Forjar Botas", callback_data="forja_bota")],
    ])
    
    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")