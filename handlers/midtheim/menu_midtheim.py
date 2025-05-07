from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.ler_texto import ler_texto # type: ignore

async def menu_midtheim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ler_texto("../texts/midtheim/menu_midtheim.txt")
    message = update.message or update.callback_query.message
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Arena de Valhalla", callback_data="arena")],
        [InlineKeyboardButton("🪙 Mercado de Skald", callback_data="coming_soon")],
        [InlineKeyboardButton("⚒️ Forja de Brokk", callback_data="coming_soon")],
        [InlineKeyboardButton("📜 Missões de Yggdrasil", callback_data="coming_soon")],
        [InlineKeyboardButton("👤 Meu Personagem", callback_data="personagem")],
        [InlineKeyboardButton("✨ Bênçãos de Odin (Conteúdo Pago)", callback_data="coming_soon")]
    ])
    
    await message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")