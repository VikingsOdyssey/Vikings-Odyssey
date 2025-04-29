from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.leitor_texto import ler_texto
import os

async def menu_arena(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    # Carrega texto
    caminho = os.path.join("bot", "textos", "midtheim", "arena", "arena.txt")
    texto = ler_texto(caminho)

    # Teclado inline da arena
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Combate Amistoso", callback_data="arena_amistoso")],
        [InlineKeyboardButton("Combate Rankeado", callback_data="arena_rankeado")],
        [InlineKeyboardButton("Ranking", callback_data="ranking_arena")],
        [InlineKeyboardButton("Voltar", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")