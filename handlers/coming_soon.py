from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def coming_soon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    texto = 'Em Breve'
    message = update.message or update.callback_query.message
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data="start")],
    ])
    
    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")