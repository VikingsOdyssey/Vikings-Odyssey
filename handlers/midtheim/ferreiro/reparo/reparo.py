from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.equipamento_durabilidade import reparar_simples, reparar_completo
from utils.ler_texto import ler_texto

async def menu_reparo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = ler_texto("../texts/midtheim/ferreiro/reparo/reparo.txt")
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛠️ Reparo Simples (100 moedas)", callback_data="reparo_simples")],
        [InlineKeyboardButton("💎 Reparo Completo (1 joia ou 150 moedas)", callback_data="reparo_completo")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="ferreiro")]
    ])
    await query.message.reply_text(texto, reply_markup=teclado, parse_mode="HTML")

async def executar_reparo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tipo = query.data
    chat_id = str(query.from_user.id)

    inv_ref = db.reference(f"{chat_id}/Inventario")
    eqp_ref = db.reference(f"{chat_id}/Equipado")
    inventario = inv_ref.get()
    equipado = eqp_ref.get()

    equipamentos_atualizados = {}

    if tipo == "reparo_simples":
        if inventario["Moedas"] < 100:
            await query.message.reply_text("❌ Você não tem moedas suficientes para reparo simples.")
            return
        inv_ref.child("Moedas").set(inventario["Moedas"] - 100)
        for slot, item in equipado.items():
            equipamentos_atualizados[slot] = reparar_simples(item)
        mensagem = "🛠️ Seus equipamentos foram reparados (+10 durabilidade cada, até o máximo)."

    elif tipo == "reparo_completo":
        if inventario["Joia_Reparo"] >= 1:
            inv_ref.child("Joia_Reparo").set(inventario["Joia_Reparo"] - 1)
        elif inventario["Moedas"] >= 150:
            inv_ref.child("Moedas").set(inventario["Moedas"] - 150)
        else:
            await query.message.reply_text("❌ Você não tem joias nem moedas suficientes para o reparo completo.")
            return
        for slot, item in equipado.items():
            equipamentos_atualizados[slot] = reparar_completo(item)
        mensagem = "💎 Seus equipamentos foram totalmente restaurados (durabilidade máxima)."

    eqp_ref.update(equipamentos_atualizados)
    await query.message.reply_text(mensagem)
