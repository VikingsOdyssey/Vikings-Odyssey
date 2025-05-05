from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal # type: ignore
from database.models import Jogador, Inventario # type: ignore
from utils.ler_texto import ler_texto # type: ignore

async def mostrar_inventario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup = None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id = chat_id).first()
    inventario = session.query(Inventario).filter_by(chat_id = chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/inventario.txt").format(nome=
        jogador.nome,
        moedas = inventario.moedas,
        diamantes = inventario.diamantes,
        madeira = inventario.madeira,
        aco = inventario.aco,
        pedra = inventario.pedra,
        linha = inventario.linha,
        couro = inventario.couro,
        criacao = inventario.joia_criacao,
        aperfeicoamento = inventario.joia_aperfeicoamento
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data = "personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data = "menu_midtheim")]
    ])
    await query.message.reply_text(text = texto, reply_markup = teclado, parse_mode = "HTML")
    session.close()