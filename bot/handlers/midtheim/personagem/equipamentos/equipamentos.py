# importa modulos e bibliotecas
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Equipado
import os
#-------------------------------------------------------------------
#Carrega texto e configura
async def equipamentos_msg(jogador, equipado):
    with open("bot/textos/midtheim/personagem/equipamentos/equipamentos.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(nome = jogador.nome,
        arma = equipado.arma,
        elmo = equipado.elmo,
        armadura = equipado.armadura,
        calca = equipado.calca,
        bota = equipado.bota,
        amuleto = equipado.amuleto)

#-------------------------------------------------------------------
# Função que mostra o Inventario
async def mostrar_equipamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Retira os botões após a seleção
    await query.edit_message_reply_markup(reply_markup = None)
    # Captuta ChatID
    chat_id = str(query.message.chat_id)
    # Abre banco de dados
    session = SessionLocal()
    # pesquisa no banco de dados
    jogador = session.query(Jogador).filter_by(chat_id = chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id = chat_id).first()
    # Referencia texto
    texto = await equipamentos_msg(jogador, equipado)
    # Configurar teclado
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Alterar Arma", callback_data = "arma")],
        [InlineKeyboardButton("🪖 Alterar Elmo", callback_data = "elmo")],
        [InlineKeyboardButton("🥋 Alterar Armadura", callback_data = "armadura")],
        [InlineKeyboardButton("👖 Alterar Calça", callback_data = "calca")],
        [InlineKeyboardButton("🥾 Alterar Bota", callback_data = "bota")],
        [InlineKeyboardButton("📿 Alterar Amuleto", callback_data = "amuleto")],
        [InlineKeyboardButton("Voltar", callback_data = "personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data = "menu_midtheim")]
    ])
    # Envia mensagem
    await query.message.reply_text(text = texto, reply_markup = teclado, parse_mode = "HTML")
    session.close()