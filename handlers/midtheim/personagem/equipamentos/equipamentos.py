from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal # type: ignore
from database.models import Jogador, Equipado # type: ignore
from utils.ler_texto import ler_texto # type: ignore

async def mostrar_equipamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup = None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id = chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id = chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/equipamentos.txt").format(nome = jogador.nome, arma = equipado.arma, elmo = equipado.elmo, armadura = equipado.armadura, calca = equipado.calca, bota = equipado.bota, amuleto = equipado.amuleto)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Alterar Arma", callback_data = "arma")],
        [InlineKeyboardButton("🪖 Alterar Elmo", callback_data = "elmo")],
        [InlineKeyboardButton("🥋 Alterar Armadura", callback_data = "armadura")],
        [InlineKeyboardButton("👖 Alterar Calça", callback_data = "calca")],
        [InlineKeyboardButton("🥾 Alterar Bota", callback_data = "bota")],
        [InlineKeyboardButton("📿 Alterar Amuleto", callback_data = "amuleto")],
        [InlineKeyboardButton("Voltar", callback_data = "personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data = "menu_midtheim")]
    ])
    await query.message.reply_text(text = texto, reply_markup = teclado, parse_mode = "HTML")
    session.close()