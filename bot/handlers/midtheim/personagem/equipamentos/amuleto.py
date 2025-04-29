from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Amuleto, Equipado
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
# Carrega o texto de amuletos
async def amuleto_msg(jogador, amuleto):
    with open("bot/textos/midtheim/personagem/equipamentos/amuletos.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        amuleto_1=amuleto.Item1 or "Vazio",
        amuleto_2=amuleto.Item2 or "Vazio",
        amuleto_3=amuleto.Item3 or "Vazio",
        amuleto_4=amuleto.Item4 or "Vazio",
        amuleto_5=amuleto.Item5 or "Vazio",
        amuleto_6=amuleto.Item6 or "Vazio",
        amuleto_7=amuleto.Item7 or "Vazio",
        amuleto_8=amuleto.Item8 or "Vazio",
        amuleto_9=amuleto.Item9 or "Vazio",
        amuleto_10=amuleto.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de amuletos disponíveis
async def mostrar_amuletos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    amuleto = session.query(Amuleto).filter_by(chat_id=chat_id).first()
    texto = await amuleto_msg(jogador, amuleto)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_amuleto")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_amuleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    amuleto = session.query(Amuleto).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_amuleto":
        if equipado.amuleto:
            novo = equipado.amuleto
            atualizar_atributos_base(jogador, novo, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(amuleto, slot) in [None, ""]:
                    setattr(amuleto, slot, novo)
                    break
            equipado.amuleto = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. O amuleto foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        novo_amuleto = getattr(amuleto, slot_nome)
        if not novo_amuleto or novo_amuleto == "":
            texto = "Este slot está vazio!"
        else:
            antigo_amuleto = equipado.amuleto
            atualizar_atributos_base(jogador, antigo_amuleto, novo_amuleto)
            equipado.amuleto = novo_amuleto
            setattr(amuleto, slot_nome, None)
            if antigo_amuleto:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(amuleto, slot) in [None, ""]:
                        setattr(amuleto, slot, antigo_amuleto)
                        break
            texto = f"Você equipou <b>{novo_amuleto}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()