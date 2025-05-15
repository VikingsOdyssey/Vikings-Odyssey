from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from datetime import datetime

async def receber_itens_diarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    diario_ref = db.reference(f"{chat_id}/Recebimentos/Entradas")
    ultima_data = diario_ref.get()
    jogador = db.reference(f"{chat_id}/Perfil").get()
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Menu", callback_data=f"menu_{jogador.get("Local_Atual").lower()}")]
    ])

    if ultima_data == data_hoje:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📅 Você já recebeu seus itens diários hoje!\nVolte após a meia-noite.", reply_markup = teclado
        )
        return

    entradas_ref = db.reference(f"{chat_id}/Entradas")
    entradas_ref.set({
        "Cacada": 10,
        "Caverna": 3,
        "Arena": 10
    })
    loot_ref = db.reference(f"{chat_id}/Recebimentos")
    loot_ref.set({
        "Loot_diario": 1,
    })

    diario_ref.set(data_hoje)

    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "🎁 Itens diários recebidos com sucesso!\n\n"
        "• 10x Entrada de Caçada\n"
        "• 3x Entrada de Caverna\n"
        "• 10x Entrada de Arena",
        reply_markup = teclado
    )
