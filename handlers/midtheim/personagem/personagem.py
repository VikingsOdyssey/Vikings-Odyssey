from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database.models import Jogador  # type: ignore
from database.config import SessionLocal # type: ignore
from utils.ler_texto import ler_texto # type: ignore

async def mostrar_ficha(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = query.from_user.id
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    texto = texto = ler_texto("../texts/midtheim/personagem/ficha.txt").format(nome=jogador.nome, lvl=jogador.nivel, xp=jogador.xp, classe=jogador.classe, local=jogador.local_atual)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎒 Inventário", callback_data="inventario")],
        [InlineKeyboardButton("🛡️ Equipamento", callback_data="equipamentos")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("↩️ Voltar", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()