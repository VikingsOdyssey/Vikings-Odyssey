from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db

DIGITAR_ID = 0

async def menu_compras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    equipamentos = db.reference("Mercado/Equipamentos").get() or {}
    itens = db.reference("Mercado/Itens").get() or {}

    texto = "<b>🏪 Itens à Venda:</b>\n\n"

    if itens:
        texto += "<b>📦 Itens de Inventário:</b>\n"
        for id_item, dados in itens.items():
            texto += f"Item: {dados['item']}\nID do Item: <code>{id_item}</code>\n👤 Vendedor: {dados['vendedor']}\nQuantidade{dados['quantidade']}x\nPreço: 💰{dados['preco']}\n\n"
    else:
        texto += "❌ Nenhum item de inventário à venda.\n\n"

    if equipamentos:
        texto += "<b>🛡️ Equipamentos:</b>\n"
        for id_item, dados in equipamentos.items():
            texto += f"Equip: {dados['item']}\nID do Equip: <code>{id_item}</code>\n👤 Vendedor: {dados['vendedor']}\nPreço: 💰{dados['preco']}\n\n"
    else:
        texto += "❌ Nenhum equipamento à venda.\n\n"

    texto += "📝 Para comprar, digite o ID do item que deseja adquirir."

    await query.message.reply_text(texto, parse_mode="HTML")
    return DIGITAR_ID

async def processar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    id_digitado = update.message.text.strip()

    # Verifica se o ID está em Itens
    item_ref = db.reference(f"Mercado/Itens/{id_digitado}")
    dados_item = item_ref.get()

    inventario_ref = db.reference(f"{chat_id}/Inventario")
    moedas_ref = inventario_ref.child("Moedas")
    saldo = moedas_ref.get() or 0

    if dados_item:
        preco = dados_item["preco"]
        if saldo < preco:
            await update.message.reply_text("❌ Você não possui moedas suficientes.")
            return ConversationHandler.END

        # Transação
        moedas_ref.set(saldo - preco)
        vendedor_ref = db.reference(f"{dados_item['chat_id']}/Inventario/Moedas")
        vendedor_saldo = vendedor_ref.get() or 0
        vendedor_ref.set(vendedor_saldo + preco)

        # Adiciona item ao inventário
        atual = inventario_ref.child(dados_item["item"]).get() or 0
        inventario_ref.child(dados_item["item"]).set(atual + dados_item["quantidade"])

        item_ref.delete()

        await update.message.reply_text(f"✅ Compra realizada com sucesso!\nVocê adquiriu {dados_item['quantidade']}x {dados_item['item']} por 💰{preco}.")
        return ConversationHandler.END

    # Verifica se é Equipamento
    equip_ref = db.reference(f"Mercado/Equipamentos/{id_digitado}")
    dados_equip = equip_ref.get()

    if dados_equip:
        preco = dados_equip["preco"]
        if saldo < preco:
            await update.message.reply_text("❌ Você não possui moedas suficientes.")
            return ConversationHandler.END

        # Transação
        moedas_ref.set(saldo - preco)
        vendedor_ref = db.reference(f"{dados_equip['chat_id']}/Inventario/Moedas")
        vendedor_saldo = vendedor_ref.get() or 0
        vendedor_ref.set(vendedor_saldo + preco)

        # Adiciona o equipamento no primeiro slot vazio
        tipo = dados_equip["tipo"].capitalize() + "s"
        slots = db.reference(f"{chat_id}/Equipamentos/{tipo}").get() or {}
        for slot, valor in slots.items():
            if not valor:
                db.reference(f"{chat_id}/Equipamentos/{tipo}/{slot}").set(dados_equip["item"])
                break

        equip_ref.delete()

        await update.message.reply_text(f"✅ Compra realizada!\nVocê adquiriu: {dados_equip['item']} por 💰{preco}.")
        return ConversationHandler.END

    await update.message.reply_text("❌ ID inválido. Nenhum item encontrado.")
    return ConversationHandler.END
