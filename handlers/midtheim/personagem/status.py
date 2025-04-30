from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal # type: ignore
from database.models import Jogador, Equipado # type: ignore
from utils.ler_texto import ler_texto # type: ignore
from utils.atributos_calc import extrair_buffs # type: ignore

async def mostrar_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()
    atributos = {"forca": jogador.forca, "magia": jogador.magia, "precisao": jogador.precisao, "resistencia": jogador.resistencia, "velocidade": jogador.velocidade, "destreza": jogador.destreza, "furia": jogador.furia, "bencao": jogador.bencao, "dominio": jogador.dominio}
    equipamentos = [equipado.arma, equipado.elmo, equipado.armadura, equipado.calca, equipado.bota]
    if equipado.amuleto:
        equipamentos.append(equipado.amuleto)
    for item in equipamentos:
        if item:
            buffs = extrair_buffs(item)
            for chave in atributos:
                atributos[chave] += buffs[chave]
    atributo_ataque_por_classe = {"guardiao": "forca", "bárbaro": "furia", "lanceiro": "dominio", "caçador": "precisao", "arcano": "magia", "espadachim": "destreza"}
    classe = jogador.classe.lower()
    atributo_chave = atributo_ataque_por_classe.get(classe)
    atributo_ataque = atributos[atributo_chave] if atributo_chave else 0
    vida = atributos["resistencia"] * 3
    agilidade = int(atributos["velocidade"] * 1.5)
    critico = int(atributos["bencao"] * 1.5)
    dano = atributo_ataque * 1
    texto = ler_texto("../texts/midtheim/personagem/status.txt").format(vida=vida, agilidade=agilidade, critico=critico, dano=dano, forca=atributos["forca"], magia=atributos["magia"], precisao=atributos["precisao"], resistencia=atributos["resistencia"], velocidade=atributos["velocidade"], destreza=atributos["destreza"], furia=atributos["furia"], bencao=atributos["bencao"], dominio=atributos["dominio"])
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()