from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Armadura, Equipado
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
# Carrega o texto de armaduras
async def armadura_msg(jogador, armadura):
    with open("bot/textos/midtheim/personagem/equipamentos/armaduras.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        armadura_1=armadura.Item1 or "Vazio",
        armadura_2=armadura.Item2 or "Vazio",
        armadura_3=armadura.Item3 or "Vazio",
        armadura_4=armadura.Item4 or "Vazio",
        armadura_5=armadura.Item5 or "Vazio",
        armadura_6=armadura.Item6 or "Vazio",
        armadura_7=armadura.Item7 or "Vazio",
        armadura_8=armadura.Item8 or "Vazio",
        armadura_9=armadura.Item9 or "Vazio",
        armadura_10=armadura.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de armaduras disponíveis
async def mostrar_armaduras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    armadura = session.query(Armadura).filter_by(chat_id=chat_id).first()
    texto = await armadura_msg(jogador, armadura)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_armadura")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_armadura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    armadura = session.query(Armadura).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_armadura":
        if equipado.armadura:
            nova = equipado.armadura
            atualizar_atributos_base(jogador, nova, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(armadura, slot) in [None, ""]:
                    setattr(armadura, slot, nova)
                    break
            equipado.armadura = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. A armadura foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        nova_armadura = getattr(armadura, slot_nome)
        if not nova_armadura or nova_armadura == "":
            texto = "Este slot está vazio!"
        else:
            antiga_armadura = equipado.armadura
            atualizar_atributos_base(jogador, antiga_armadura, nova_armadura)
            equipado.armadura = nova_armadura
            setattr(armadura, slot_nome, None)
            if antiga_armadura:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(armadura, slot) in [None, ""]:
                        setattr(armadura, slot, antiga_armadura)
                        break
            texto = f"Você equipou <b>{nova_armadura}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()