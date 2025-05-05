from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.ler_texto import ler_texto

async def menu_arena(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto("../texts/midtheim/arena/arena.txt")
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Combate Amistoso", callback_data="arena_amistoso")],
        [InlineKeyboardButton("Combate Rankeado", callback_data="arena_rankeado")],
        [InlineKeyboardButton("Ranking", callback_data="ranking_arena")],
        [InlineKeyboardButton("Voltar", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")