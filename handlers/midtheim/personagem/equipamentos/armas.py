# Exemplo padronizado para todos os tipos de equipamento
# Local: bot/handlers/midtheim/personagem/equipamentos/armas.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Equipado, Arma
from utils.equipamentos import get_equipamento_model, mover_item_para_equipado, desequipar_item
from utils.ler_texto import ler_texto

async def mostrar_armas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    inventario = session.query(Arma).filter_by(chat_id=chat_id).first()

    texto = ler_texto(f"../texts/midtheim/personagem/equipamentos/armas.txt").format(
        arma_1=inventario.Item1 or "Vazio",
        arma_2=inventario.Item2 or "Vazio",
        arma_3=inventario.Item3 or "Vazio",
        arma_4=inventario.Item4 or "Vazio",
        arma_5=inventario.Item5 or "Vazio",
        arma_6=inventario.Item6 or "Vazio",
        arma_7=inventario.Item7 or "Vazio",
        arma_8=inventario.Item8 or "Vazio",
        arma_9=inventario.Item9 or "Vazio",
        arma_10=inventario.Item10 or "Vazio"
    )

    teclado = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)] +
        [[InlineKeyboardButton("Desequipar", callback_data=f"desequipar_arma")]]
    )

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

async def selecionar_arma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()
    inventario = session.query(Arma).filter_by(chat_id=chat_id).first()

    if escolha == f"desequipar_arma":
        sucesso = desequipar_item(jogador, equipado, inventario, arma)
        texto = f"{arma.capitalize()} desequipado com sucesso!" if sucesso else f"Você não estava com um(a) arma equipado(a)."
    else:
        slot_index = int(escolha[1:])
        item_novo, erro = mover_item_para_equipado(jogador, equipado, inventario, arma, slot_index)
        if erro:
            texto = erro
        else:
            texto = f"Você equipou <b>{item_novo}</b>!"

    session.commit()

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Equipamentos", callback_data="equipamentos")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
