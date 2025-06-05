from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

async def menu_mercado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    teclado = [
        [InlineKeyboardButton("🛒 Comprar", callback_data="comprar")],
        [InlineKeyboardButton("💰 Vender", callback_data="vender")],
        [InlineKeyboardButton("Voltar", callback_data="menu_midtheim")]
    ]
    await query.message.reply_text(
        "<b>🏪 Bem-vindo ao Mercado dos Nove Reinos!</b>\nO que deseja fazer?",
        reply_markup=InlineKeyboardMarkup(teclado),
        parse_mode="HTML"
    )
