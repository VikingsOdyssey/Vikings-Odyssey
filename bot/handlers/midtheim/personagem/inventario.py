# importa modulos e bibliotecas
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Inventario
import os
#-------------------------------------------------------------------
#Carrega texto e configura
async def carregar_texto_ficha(jogador, inventario):
    with open("bot/textos/midtheim/personagem/inventario.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    return texto.format(nome = jogador.nome,
        moedas = inventario.moedas,
        diamantes = inventario.diamantes,
        madeira = inventario.madeira,
        aco = inventario.aco,
        pedra = inventario.pedra,
        linha = inventario.linha,
        couro = inventario.couro,
        criacao = inventario.joia_criacao,
        aperfeicoamento = inventario.joia_aperfeicoamento)


#-------------------------------------------------------------------
# Função que mostra o Inventario
async def mostrar_inventario(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    inventario = session.query(Inventario).filter_by(chat_id = chat_id).first()
    # Referencia texto
    texto = await carregar_texto_ficha(jogador, inventario)
    # Configurar teclado
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data = "personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data = "menu_midtheim")]
    ])
    # Envia mensagem
    await query.message.reply_text(text = texto, reply_markup = teclado, parse_mode = "HTML")
    session.close()