from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto # type: ignore

async def menu_midtheim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    ref = db.reference(f"{chat_id}")
    perfil = ref.child("Perfil").get()
    inventario = ref.child("Inventario").get()
    entradas = ref.child("Entradas").get()
    texto = ler_texto("../texts/midtheim/menu_midtheim.txt").format(
        level = perfil.get("Nivel"),
        moedas = inventario.get("Moedas"),
        arena = entradas.get("Arena")
    )
    message = update.message or update.callback_query.message
    match chat_id:
        case "5753061231":
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("Adm", callback_data="adm")],
                [InlineKeyboardButton("⚔️ Arena de Valhalla", callback_data="arena")],
                [InlineKeyboardButton("🪙 Mercado de Skald", callback_data="mercado")],
                [InlineKeyboardButton("⚒️ Ferreiro de Brokk", callback_data="ferreiro")],
                [InlineKeyboardButton("📜 Missões de Yggdrasil", callback_data="coming_soon")],
                [InlineKeyboardButton("👤 Meu Personagem", callback_data="personagem")],
                [InlineKeyboardButton("Viajar", callback_data="menu_viagem")],
                [InlineKeyboardButton("✨ Bênçãos de Odin (Conteúdo Pago)", callback_data="coming_soon")]
            ])
        case _:
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Arena de Valhalla", callback_data="arena")],
                [InlineKeyboardButton("🪙 Mercado de Skald", callback_data="mercado")],
                [InlineKeyboardButton("⚒️ Ferreiro de Brokk", callback_data="ferreiro")],
                [InlineKeyboardButton("📜 Missões de Yggdrasil", callback_data="coming_soon")],
                [InlineKeyboardButton("👤 Meu Personagem", callback_data="personagem")],
                [InlineKeyboardButton("Viajar", callback_data="menu_viagem")],
                [InlineKeyboardButton("✨ Bênçãos de Odin (Conteúdo Pago)", callback_data="coming_soon")]
            ])
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)
        await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    except:
        await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")