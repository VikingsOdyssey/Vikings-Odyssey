from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Calca, Equipado
import os
import re

#-------------------------------------------------------------------
# Mapeia emojis para nomes de atributos no banco de dados
ATRIBUTOS_EMOJI = {
    "❤️‍🩹": "resistencia",
    "💪": "forca",
    "⚡": "velocidade",
    "✨": "bencao",
    "🔮": "magia",
    "🎯": "precisao",
    "🏹": "destreza",
    "🔥": "furia",
    "🧠": "dominio"
}

#-------------------------------------------------------------------
# Extrai buffs do nome do item
def extrair_buffs(nome_item):
    if not nome_item or "[" not in nome_item:
        return {}

    buffs = {}
    partes = nome_item.split("[")
    if len(partes) < 3:
        return {}

    try:
        level = int(re.search(r"(\d+)", nome_item).group(1))
    except:
        return {}

    buffs_brutos = re.findall(r"([❤️‍🩹💪⚡✨🔮🎯🏹🔥🧠])\+(\d+)", nome_item)
    for emoji, _ in buffs_brutos:
        atributo = ATRIBUTOS_EMOJI.get(emoji)
        if atributo:
            buffs[atributo] = level
    return buffs

#-------------------------------------------------------------------
# Atualiza os atributos do jogador com base na troca de item
def atualizar_atributos_base(jogador, item_antigo, item_novo):
    buffs_antigo = extrair_buffs(item_antigo)
    buffs_novo = extrair_buffs(item_novo)

    for atributo in ATRIBUTOS_EMOJI.values():
        valor_atual = getattr(jogador, atributo, 0)
        remover = buffs_antigo.get(atributo, 0)
        adicionar = buffs_novo.get(atributo, 0)
        setattr(jogador, atributo, valor_atual - remover + adicionar)

#-------------------------------------------------------------------
# Carrega o texto de calcas
async def calca_msg(jogador, calca):
    with open("bot/textos/midtheim/personagem/equipamentos/calcas.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        calca_1=calca.Item1 or "Vazio",
        calca_2=calca.Item2 or "Vazio",
        calca_3=calca.Item3 or "Vazio",
        calca_4=calca.Item4 or "Vazio",
        calca_5=calca.Item5 or "Vazio",
        calca_6=calca.Item6 or "Vazio",
        calca_7=calca.Item7 or "Vazio",
        calca_8=calca.Item8 or "Vazio",
        calca_9=calca.Item9 or "Vazio",
        calca_10=calca.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de calcas disponíveis
async def mostrar_calcas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    calca = session.query(Calca).filter_by(chat_id=chat_id).first()
    texto = await calca_msg(jogador, calca)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_calca")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_calca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    calca = session.query(Calca).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_calca":
        if equipado.calca:
            nova = equipado.calca
            atualizar_atributos_base(jogador, nova, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(calca, slot) in [None, ""]:
                    setattr(calca, slot, nova)
                    break
            equipado.calca = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. A calca foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        nova_calca = getattr(calca, slot_nome)
        if not nova_calca or nova_calca == "":
            texto = "Este slot está vazio!"
        else:
            antiga_calca = equipado.calca
            atualizar_atributos_base(jogador, antiga_calca, nova_calca)
            equipado.calca = nova_calca
            setattr(calca, slot_nome, None)
            if antiga_calca:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(calca, slot) in [None, ""]:
                        setattr(calca, slot, antiga_calca)
                        break
            texto = f"Você equipou <b>{nova_calca}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()