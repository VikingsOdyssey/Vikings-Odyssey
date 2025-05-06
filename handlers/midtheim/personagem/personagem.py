from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from firebase_admin import db
from utils.ler_texto import ler_texto

async def mostrar_ficha(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.from_user.id)
    jogador_ref = db.reference(f"{chat_id}/Perfil")
    jogador = jogador_ref.get()

    if not jogador:
        await query.message.reply_text("❌ Não foi possível encontrar seus dados.")
        return

    texto = ler_texto("../texts/midtheim/personagem/ficha.txt").format(
        nome=jogador.get("Nome"),
        lvl=jogador.get("Nivel"),
        xp=jogador.get("Xp"),
        classe=jogador.get("Classe"),
        local=jogador.get("Local_Atual")
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎒 Inventário", callback_data="inventario")],
        [InlineKeyboardButton("🛡️ Equipamento", callback_data="equipamentos")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("↩️ Voltar", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
