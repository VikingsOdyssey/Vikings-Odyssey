from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Arma, Equipado
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
# Carrega o texto de armas
async def arma_msg(jogador, arma):
    with open("bot/textos/midtheim/personagem/equipamentos/armas.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        arma_1=arma.Item1 or "Vazio",
        arma_2=arma.Item2 or "Vazio",
        arma_3=arma.Item3 or "Vazio",
        arma_4=arma.Item4 or "Vazio",
        arma_5=arma.Item5 or "Vazio",
        arma_6=arma.Item6 or "Vazio",
        arma_7=arma.Item7 or "Vazio",
        arma_8=arma.Item8 or "Vazio",
        arma_9=arma.Item9 or "Vazio",
        arma_10=arma.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de armas disponíveis
async def mostrar_armas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    arma = session.query(Arma).filter_by(chat_id=chat_id).first()
    texto = await arma_msg(jogador, arma)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_arma")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_arma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    arma = session.query(Arma).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_arma":
        if equipado.arma:
            nova = equipado.arma
            atualizar_atributos_base(jogador, nova, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(arma, slot) in [None, ""]:
                    setattr(arma, slot, nova)
                    break
            equipado.arma = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. A arma foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        nova_arma = getattr(arma, slot_nome)
        if not nova_arma or nova_arma == "":
            texto = "Este slot está vazio!"
        else:
            antiga_arma = equipado.arma
            atualizar_atributos_base(jogador, antiga_arma, nova_arma)
            equipado.arma = nova_arma
            setattr(arma, slot_nome, None)
            if antiga_arma:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(arma, slot) in [None, ""]:
                        setattr(arma, slot, antiga_arma)
                        break
            texto = f"Você equipou <b>{nova_arma}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()