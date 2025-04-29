from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Bota, Equipado
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
# Carrega o texto de botas
async def bota_msg(jogador, bota):
    with open("bot/textos/midtheim/personagem/equipamentos/botas.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(
        bota_1=bota.Item1 or "Vazio",
        bota_2=bota.Item2 or "Vazio",
        bota_3=bota.Item3 or "Vazio",
        bota_4=bota.Item4 or "Vazio",
        bota_5=bota.Item5 or "Vazio",
        bota_6=bota.Item6 or "Vazio",
        bota_7=bota.Item7 or "Vazio",
        bota_8=bota.Item8 or "Vazio",
        bota_9=bota.Item9 or "Vazio",
        bota_10=bota.Item10 or "Vazio"
    )

#-------------------------------------------------------------------
# Mostra a lista de botas disponíveis
async def mostrar_botas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    bota = session.query(Bota).filter_by(chat_id=chat_id).first()
    texto = await bota_msg(jogador, bota)
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_bota")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_bota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    bota = session.query(Bota).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    if escolha == "desequipar_bota":
        if equipado.bota:
            nova = equipado.bota
            atualizar_atributos_base(jogador, nova, None)  # remove buffs
            for i in range(1, 11):
                slot = f"Item{i}"
                if getattr(bota, slot) in [None, ""]:
                    setattr(bota, slot, nova)
                    break
            equipado.bota = None
            session.commit()
        texto = "Você voltou ao menu de Midtheim. A bota foi guardada com segurança."
    else:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
        nova_bota = getattr(bota, slot_nome)
        if not nova_bota or nova_bota == "":
            texto = "Este slot está vazio!"
        else:
            antiga_bota = equipado.bota
            atualizar_atributos_base(jogador, antiga_bota, nova_bota)
            equipado.bota = nova_bota
            setattr(bota, slot_nome, None)
            if antiga_bota:
                for i in range(1, 11):
                    slot = f"Item{i}"
                    if getattr(bota, slot) in [None, ""]:
                        setattr(bota, slot, antiga_bota)
                        break
            texto = f"Você equipou <b>{nova_bota}</b>!"

        session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()