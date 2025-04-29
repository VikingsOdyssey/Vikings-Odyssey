from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Equipado
from utils.leitor_texto import ler_texto
import os
import re

# Emojis para os atributos
EMOJIS_ATRIBUTOS = {
    "forca": "💪",
    "magia": "🔮",
    "precisao": "🎯",
    "resistencia": "❤️‍🩹",
    "velocidade": "⚡",
    "destreza": "🌀",
    "furia": "🔥",
    "bencao": "✨",
    "dominio": "🏹"
}

# Mapeamento reverso
EMOJI_PARA_ATRIBUTO = {v: k for k, v in EMOJIS_ATRIBUTOS.items()}

# Regex que pega corretamente buffs repetidos
REGEX_BUFFS = r"(" + "|".join(map(re.escape, EMOJI_PARA_ATRIBUTO.keys())) + r")\+(\d+)"

def extrair_buffs(nome_item):
    atributos = {chave: 0 for chave in EMOJIS_ATRIBUTOS}
    if not nome_item:
        return atributos
    matches = re.findall(REGEX_BUFFS, nome_item)
    for emoji, valor in matches:
        chave = EMOJI_PARA_ATRIBUTO.get(emoji.strip())
        if chave:
            atributos[chave] += int(valor)
    return atributos

async def mostrar_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    caminho_texto = os.path.join("bot", "textos", "midtheim", "personagem", "status.txt")
    texto_base = ler_texto(caminho_texto)

    # Atributos base do jogador
    atributos = {
        "forca": jogador.forca,
        "magia": jogador.magia,
        "precisao": jogador.precisao,
        "resistencia": jogador.resistencia,
        "velocidade": jogador.velocidade,
        "destreza": jogador.destreza,
        "furia": jogador.furia,
        "bencao": jogador.bencao,
        "dominio": jogador.dominio
    }

    # Equipamentos equipados
    equipamentos = [
        equipado.arma,
        equipado.elmo,
        equipado.armadura,
        equipado.calca,
        equipado.bota,
    ]

    if equipado.amuleto:
        equipamentos.append(equipado.amuleto)

    # Soma os buffs dos equipamentos
    for item in equipamentos:
        if item:
            buffs = extrair_buffs(item)
            for chave in atributos:
                atributos[chave] += buffs[chave]

    # Define o atributo de ataque pela classe
    atributo_ataque_por_classe = {
        "guardiao": "forca",
        "bárbaro": "furia",
        "lanceiro": "dominio",
        "caçador": "precisao",
        "arcano": "magia",
        "espadachim": "destreza"
    }
    classe = jogador.classe.lower()
    atributo_chave = atributo_ataque_por_classe.get(classe)
    atributo_ataque = atributos[atributo_chave] if atributo_chave else 0

    # Status derivados
    vida = atributos["resistencia"] * 3
    agilidade = int(atributos["velocidade"] * 1.5)
    critico = int(atributos["bencao"] * 1.5)
    dano = atributo_ataque * 1

    texto = texto_base.format(
        vida=vida,
        agilidade=agilidade,
        critico=critico,
        dano=dano,
        forca=atributos["forca"],
        magia=atributos["magia"],
        precisao=atributos["precisao"],
        resistencia=atributos["resistencia"],
        velocidade=atributos["velocidade"],
        destreza=atributos["destreza"],
        furia=atributos["furia"],
        bencao=atributos["bencao"],
        dominio=atributos["dominio"]
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()