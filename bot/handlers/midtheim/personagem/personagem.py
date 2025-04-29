from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from database.models import Jogador  # ajuste se o nome for outro
from database.config import SessionLocal

async def carregar_texto_ficha(jogador):
    with open("bot/textos/midtheim/personagem/ficha.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        nome=jogador.nome,
        lvl=jogador.nivel,
        xp=jogador.xp,
        classe=jogador.classe,
        local=jogador.local_atual
    )

async def mostrar_ficha(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = query.from_user.id
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()

    if jogador:
        texto = await carregar_texto_ficha(jogador)
        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎒 Inventário", callback_data="inventario")],
        [InlineKeyboardButton("🛡️ Equipamento", callback_data="equipamentos")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("↩️ Voltar", callback_data="menu_midtheim")]
    ])
        await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()