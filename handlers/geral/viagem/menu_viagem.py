from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto

async def menu_viagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto("../texts/viagem/menu_viagem.txt")
    message = update.message or update.callback_query.message
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌾 Cidade de Midthem", callback_data="viajar_Midtheim")],
        [InlineKeyboardButton("🌾 Campos de Solvindr", callback_data="viajar_Solvindr")],
        [InlineKeyboardButton("🏞 Planícies de Modrheim", callback_data="coming_soon")],
        [InlineKeyboardButton("🌲 Floresta de Yggdreth", callback_data="coming_soon")],
        [InlineKeyboardButton("🔥 Deserto de Aska", callback_data="coming_soon")],
        [InlineKeyboardButton("🌊 Costa de Skjovik", callback_data="coming_soon")]
    ])
    
    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")

async def viajar_para_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)

    # Extrai o nome do local da callback_data: "viajar_<Local>"
    local_destino = query.data.replace("viajar_", "")

    # Atualiza o local no banco de dados
    db.reference(f"{chat_id}/Perfil/Local_Atual").set(local_destino)

    funcao_menu = context.bot_data['menus'].get(f"menu_{local_destino.lower()}")
    if callable(funcao_menu):
        await funcao_menu(update, context)
    else:
        await query.message.reply_text(f"Ainda não há conteúdo em {local_destino} — em breve!")
