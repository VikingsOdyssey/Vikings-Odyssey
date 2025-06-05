from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

async def menu_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Vender item", callback_data="vender_item")],
        [InlineKeyboardButton("💰 Vender equipamento", callback_data="vender_equipamento")],
        [InlineKeyboardButton("Voltar", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(
        "🏪 O que deseja vender?",
        reply_markup=teclado,
        parse_mode="HTML"
    )
