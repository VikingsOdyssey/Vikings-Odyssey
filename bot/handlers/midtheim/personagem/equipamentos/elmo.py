from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Elmo, Equipado
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
# Carrega o texto de elmos
async def elmo_msg(jogador, elmo):
    with open("bot/textos/midtheim/personagem/equipamentos/elmos.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        elmo_1=elmo.Item1 or "Vazio",
        elmo_2=elmo.Item2 or "Vazio",
        elmo_3=elmo.Item3 or "Vazio",
        elmo_4=elmo.Item4 or "Vazio",
        elmo_5=elmo.Item5 or "Vazio",
        elmo_6=elmo.Item6 or "Vazio",
        elmo_7=elmo.Item7 or "Vazio",
        elmo_8=elmo.Item8 or "Vazio",
        elmo_9=elmo.Item9 or "Vazio",
        elmo_10=elmo.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de elmos disponíveis
async def mostrar_elmos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    elmo = session.query(Elmo).filter_by(chat_id=chat_id).first()
    texto = await elmo_msg(jogador, elmo)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_elmo")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_elmo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    elmo = session.query(Elmo).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_elmo":
        if equipado.elmo:
            novo = equipado.elmo
            atualizar_atributos_base(jogador, novo, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(elmo, slot) in [None, ""]:
                    setattr(elmo, slot, novo)
                    break
            equipado.elmo = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. O elmo foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        novo_elmo = getattr(elmo, slot_nome)
        if not novo_elmo or novo_elmo == "":
            texto = "Este slot está vazio!"
        else:
            antigo_elmo = equipado.elmo
            atualizar_atributos_base(jogador, antigo_elmo, novo_elmo)
            equipado.elmo = novo_elmo
            setattr(elmo, slot_nome, None)
            if antigo_elmo:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(elmo, slot) in [None, ""]:
                        setattr(elmo, slot, antigo_elmo)
                        break
            texto = f"Você equipou <b>{novo_elmo}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()