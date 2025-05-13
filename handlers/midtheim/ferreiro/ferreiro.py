from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.ler_texto import ler_texto

async def ferreiro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto('../texts/midtheim/ferreiro/ferreiro.txt')
    message = update.message or update.callback_query.message
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Forja", callback_data="forja")],
        [InlineKeyboardButton("Reparo", callback_data="coming_soon")],
        [InlineKeyboardButton("Desmache", callback_data="coming_soon")],
    ])
    
    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")