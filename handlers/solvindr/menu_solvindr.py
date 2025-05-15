from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto

async def menu_solvindr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    ref = db.reference(f"{chat_id}")
    perfil = ref.child("Perfil").get()
    inventario = ref.child("Inventario").get()
    entradas = ref.child("Entradas").get()
    texto = ler_texto("../texts/solvindr/menu_solvindr.txt").format(
        level = perfil.get("Nivel"),
        moedas = inventario.get("Moedas"),
        la = inventario.get("La"),
        cacada = entradas.get("Cacada"),
        cavernas = entradas.get("Caverna"),
        dungeons = entradas.get("Dungeon")
    )
    message = update.message or update.callback_query.message
    match chat_id:
        case "5753061231":
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("Adm", callback_data="adm")],
                [InlineKeyboardButton("Caçada", callback_data="coming_soon")],
                [InlineKeyboardButton("Caverna", callback_data="coming_soon")],
                [InlineKeyboardButton("Dungeon", callback_data="coming_soon")],
                [InlineKeyboardButton("Pastorear Ovelhas", callback_data="coming_soon")],
                [InlineKeyboardButton("👤 Meu Personagem", callback_data="personagem")],
                [InlineKeyboardButton("Viajar", callback_data="menu_viagem")],
            ])
        
        case _:
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("Caçada", callback_data="coming_soon")],
                [InlineKeyboardButton("Caverna", callback_data="coming_soon")],
                [InlineKeyboardButton("Dungeon", callback_data="coming_soon")],
                [InlineKeyboardButton("Pastorear Ovelhas", callback_data="coming_soon")],
                [InlineKeyboardButton("👤 Meu Personagem", callback_data="personagem")],
                [InlineKeyboardButton("Viajar", callback_data="menu_viagem")],
            ])
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)
        await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    except:
        await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")