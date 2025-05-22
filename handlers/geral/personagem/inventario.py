from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto

async def mostrar_inventario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    
    chat_id = str(query.message.chat_id)
    ref = db.reference(f"{chat_id}")
    
    perfil = ref.child("Perfil").get()
    inventario = ref.child("Inventario").get()
    loot = ref.child("Recebimentos").get()

    if not perfil or not inventario:
        await query.message.reply_text("❌ Não foi possível carregar os dados do inventário.")
        return

    texto = ler_texto("../texts/midtheim/personagem/inventario.txt").format(
        nome=perfil.get("Nome", "Desconhecido"),
        moedas=inventario.get("Moedas", 0),
        diamantes=inventario.get("Diamantes", 0),
        madeira=inventario.get("Madeira", 0),
        aco=inventario.get("Aco", 0),
        pedra=inventario.get("Pedra", 0),
        la=inventario.get("La", 0),
        couro=inventario.get("Couro", 0),
        criacao=inventario.get("Joia_Criacao", 0),
        aperfeicoamento=inventario.get("Joia_Aperfeicoamento", 0),
        loot_diario=loot.get("Loot_diario"),
        loot_cacada=loot.get("Loot_cacada")
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Abrir Loot Diario", callback_data="abrir_Loot_diario")],
        [InlineKeyboardButton("Abrir Loot de Caçada", callback_data="abrir_Loot_cacada")],
        [InlineKeyboardButton("Menu", callback_data=f"menu_{perfil.get("Local_Atual").lower()}")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
