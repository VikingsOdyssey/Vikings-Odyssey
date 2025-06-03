from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
import random
import re
from libs.emoji_atributos import EMOJIS_ATRIBUTOS

ESCOLHER_TIPO, ESCOLHER_ITEM, CONFIRMAR = range(3)

QUALIDADES = ["🔵", "🟠", "🔴", "🟢"]
REQUISITOS_QUALIDADE = {"🔵": 4, "🟠": 6, "🔴": 8}

async def menu_aprimoramento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    teclado = [
        [InlineKeyboardButton("⬆️ Melhorar Nível", callback_data="aprimorar_nivel")],
        [InlineKeyboardButton("🌟 Melhorar Qualidade", callback_data="aprimorar_qualidade")],
        [InlineKeyboardButton("Voltar", callback_data="forja")]
    ]
    await query.message.reply_text(
        "<b>Escolha o tipo de aprimoramento:</b>",
        reply_markup=InlineKeyboardMarkup(teclado),
        parse_mode="HTML"
    )
    return ESCOLHER_TIPO

async def selecionar_equipamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo_aprimoramento = query.data.replace("aprimorar_", "")
    context.user_data["tipo_aprimoramento"] = tipo_aprimoramento
    chat_id = str(query.from_user.id)
    equipado = db.reference(f"{chat_id}/Equipado").get()

    botoes = []
    for tipo, item in equipado.items():
        if item:
            botoes.append([InlineKeyboardButton(item, callback_data=f"1aprimorar_item_{tipo}")])

    if not botoes:
        await query.message.reply_text("Você não possui itens equipados para aprimorar.")
        return ConversationHandler.END

    await query.message.reply_text(
        "<b>Escolha o equipamento que deseja aprimorar:</b>",
        reply_markup=InlineKeyboardMarkup(botoes),
        parse_mode="HTML"
    )
    return ESCOLHER_ITEM

async def confirmar_aprimoramento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo_item = query.data.replace("1aprimorar_item_", "")
    context.user_data["slot_escolhido"] = tipo_item
    chat_id = str(query.from_user.id)

    item = db.reference(f"{chat_id}/Equipado/{tipo_item}").get()
    inventario_ref = db.reference(f"{chat_id}/Inventario")
    perfil_ref = db.reference(f"{chat_id}/Perfil")
    tipo_aprimoramento = context.user_data.get("tipo_aprimoramento")

    # Nível de forja influencia a chance de sucesso (nível * 10%)
    nivel_forja = perfil_ref.child("Nivel_Forja").get() or 1
    chance_sucesso = min(90, nivel_forja * 10)

    if tipo_aprimoramento == "nivel":
        joias = inventario_ref.child("Joia_Aperfeicoamento").get() or 0
        if joias < 1:
            await query.message.reply_text("❌ Você não possui joias de aprimoramento suficientes.")
            return ConversationHandler.END

        sucesso = random.randint(1, 100) <= chance_sucesso
        if not sucesso:
            await query.message.reply_text("💥 O aprimoramento falhou. Nenhuma alteração foi feita.")
            return ConversationHandler.END

        inventario_ref.child("Joia_Aperfeicoamento").set(joias - 1)

        atualizado = aprimorar_nivel(item)
        db.reference(f"{chat_id}/Equipado/{tipo_item}").set(atualizado)
        await query.message.reply_text(f"✅ Equipamento aprimorado com sucesso:\n{atualizado}", parse_mode="HTML")

    elif tipo_aprimoramento == "qualidade":
        joias = inventario_ref.child("Joia_Aperfeicoamento").get() or 0
        if joias < 2:
            await query.message.reply_text("❌ Você precisa de 2 Joias de Aprimoramento para isso.")
            return ConversationHandler.END

        qualidade_atual = re.search(r"\[(🔵|🟠|🔴|🟢)]", item)
        if not qualidade_atual:
            await query.message.reply_text("❌ Qualidade inválida neste equipamento.")
            return ConversationHandler.END

        emoji_atual = qualidade_atual.group(1)
        if emoji_atual not in REQUISITOS_QUALIDADE:
            await query.message.reply_text("⚠️ Este item já está na qualidade máxima.")
            return ConversationHandler.END

        lvl = int(re.search(r"\[(\d+)]", item).group(1))
        if lvl < REQUISITOS_QUALIDADE[emoji_atual]:
            await query.message.reply_text("⚠️ Nível insuficiente para subir de qualidade.")
            return ConversationHandler.END

        inventario_ref.child("Joia_Aperfeicoamento").set(joias - 2)

        novo_item = aprimorar_qualidade(item)
        db.reference(f"{chat_id}/Equipado/{tipo_item}").set(novo_item)
        await query.message.reply_text(f"✨ Qualidade aprimorada com sucesso:\n{novo_item}", parse_mode="HTML")

    return ConversationHandler.END

def aprimorar_nivel(equipamento: str) -> str:
    # Extrai durabilidade
    durabilidade = re.search(r"\[(\d+/\d+)]", equipamento).group(1)
    restante = re.sub(rf"\[{durabilidade}]", "", equipamento).strip()

    # Extrai qualidade, nome, nível
    qualidade, lvl, *_ = re.findall(r"\[(.*?)\]", restante)
    nome_match = re.search(r"\] (.*?) \[", restante)
    nome = nome_match.group(1) if nome_match else "Equipamento"

    # Extrai todos os buffs (permite repetição)
    matches = re.findall(r"([\u2600-\U0001FAFF]+)\+(\d+)", equipamento)
    novos_buffs = []
    for emoji, valor in matches:
        novos_buffs.append(f"{emoji}+{int(valor) + 1}")

    buffs_formatados = ", ".join(novos_buffs)

    # Novo nível
    novo_lvl = int(lvl) + 1

    return f"[{durabilidade}] [{qualidade}] {nome} [{novo_lvl}] [{buffs_formatados}]"

def aprimorar_qualidade(equipamento: str) -> str:

    # Extrai durabilidade
    durabilidade = re.search(r"\[(\d+/\d+)]", equipamento).group(1)
    restante = re.sub(rf"\[{durabilidade}]", "", equipamento).strip()

    # Extrai qualidade, nome
    qualidade, *_ = re.findall(r"\[(.*?)\]", restante)
    nome_match = re.search(r"\] (.*?) \[", restante)
    nome = nome_match.group(1) if nome_match else "Equipamento"

    # Ordem de qualidades
    QUALIDADES = ["🔵", "🟠", "🔴", "🟢"]
    if qualidade not in QUALIDADES:
        return equipamento

    indice = QUALIDADES.index(qualidade)
    if indice + 1 >= len(QUALIDADES):
        return equipamento  # já na qualidade máxima

    nova_qualidade = QUALIDADES[indice + 1]

    # Inverter dicionário: emoji → chave
    EMOJI_PARA_CHAVE = {v: k for k, v in EMOJIS_ATRIBUTOS.items()}

    # Extrai emojis dos buffs
    regex_emojis = '|'.join(re.escape(emoji) for emoji in EMOJI_PARA_CHAVE)
    emojis_buff = re.findall(rf"({regex_emojis})\+\d+", equipamento)

    # Converte emojis para chaves
    buffs_chaves = [EMOJI_PARA_CHAVE[e] for e in emojis_buff if e in EMOJI_PARA_CHAVE]

    # Adiciona novo buff aleatório
    todos_atributos = list(EMOJIS_ATRIBUTOS.keys())
    faltantes = [a for a in todos_atributos if a not in buffs_chaves]
    if faltantes:
        buffs_chaves.append(random.choice(faltantes))

    # Reconstrói com buffs +1
    buffs_formatados = ", ".join(f"{EMOJIS_ATRIBUTOS[chave]}+1" for chave in buffs_chaves)

    return f"[{durabilidade}] [{nova_qualidade}] {nome} [1] [{buffs_formatados}]"
