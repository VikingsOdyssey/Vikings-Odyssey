from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto

async def mostrar_equipamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    
    chat_id = str(query.message.chat_id)
    ref_base = db.reference(f"{chat_id}")

    perfil = ref_base.child("Perfil").get()
    equipado = ref_base.child("Equipado").get()

    texto = ler_texto("../texts/midtheim/personagem/equipamentos/equipamentos.txt").format(
        nome=perfil.get("Nome", "Desconhecido"),
        arma=equipado.get("Arma", "Nenhuma"),
        elmo=equipado.get("Elmo", "Nenhum"),
        armadura=equipado.get("Armadura", "Nenhuma"),
        calca=equipado.get("Calca", "Nenhuma"),
        bota=equipado.get("Bota", "Nenhuma"),
        amuleto=equipado.get("Amuleto", "Nenhum")
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Alterar Arma", callback_data="arma")],
        [InlineKeyboardButton("🪖 Alterar Elmo", callback_data="elmo")],
        [InlineKeyboardButton("🥋 Alterar Armadura", callback_data="armadura")],
        [InlineKeyboardButton("👖 Alterar Calça", callback_data="calca")],
        [InlineKeyboardButton("🥾 Alterar Bota", callback_data="bota")],
        [InlineKeyboardButton("📿 Alterar Amuleto", callback_data="amuleto")],
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Menu", callback_data=f"menu_{perfil.get("Local_Atual").lower()}")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
