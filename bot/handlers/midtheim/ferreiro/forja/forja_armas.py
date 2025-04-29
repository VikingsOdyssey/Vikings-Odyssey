import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Inventario, Arma
from utils.leitor_texto import ler_texto
from utils.atributos_classe import EMOJIS_ATRIBUTOS  # <- IMPORTANTE

QUALIDADES = [
    ("🟢", "Divino", 3),
    ("🔴", "Perfeito", 7),
    ("🟠", "Bom", 20),
    ("🔵", "Comum", 70),
]

ARMAS_POR_CLASSE = {
    "Espadachim": "Lâmina de Skuld",
    "Caçador": "Arco de Fenrir",
    "Guardião": "Espada de Ymir",
    "Lanceiro": "Lança de Níðhöggr",
    "Bárbaro": "Machado de Surtr",
    "Arcano": "Cedro de Mímir"
}

async def forja_armas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = ler_texto("bot/textos/midtheim/ferreiro/forja/forja_armas.txt")
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Criar", callback_data="criar_arma")],
        [InlineKeyboardButton("Voltar", callback_data="forjar_equipamento")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")],
    ])
    await query.message.reply_text(text=texto, parse_mode="HTML", reply_markup=teclado)

async def criar_arma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    session = SessionLocal()
    chat_id = str(query.message.chat_id)
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    inventario = session.query(Inventario).filter_by(chat_id=chat_id).first()
    armas = session.query(Arma).filter_by(chat_id=chat_id).first()

    if inventario.madeira < 3 or inventario.aco < 6 or inventario.joia_criacao < 1:
        await query.message.reply_text(
            "❌ Você não possui recursos suficientes para forjar uma arma.", parse_mode="HTML")
        session.close()
        return

    nivel_forja = jogador.nivel_foja
    chance_sucesso = min(50 + (nivel_forja - 1) * 5, 100)
    sucesso = random.randint(1, 100) <= chance_sucesso

    inventario.madeira -= 3
    inventario.aco -= 6
    inventario.joia_criacao -= 1

    if sucesso:
        jogador.xp_forja += 10

        qualidade = random.choices(QUALIDADES, weights=[q[2] for q in QUALIDADES[::-1]], k=1)[0]
        emoji, nome_qualidade, _ = qualidade
        nome_arma = ARMAS_POR_CLASSE.get(jogador.classe, "Arma Misteriosa")
        atributo_ataque = jogador.atributo_ataque or "forca"

        # Seleciona buffs aleatórios (evita repetir o de ataque)
        buffs_possiveis = list(set(EMOJIS_ATRIBUTOS.keys()))
        quantidade_buffs = QUALIDADES.index(qualidade) + 1
        buffs_escolhidos = [atributo_ataque] + random.sample(buffs_possiveis, quantidade_buffs - 1)

        buffs_formatados = ", ".join(f"{EMOJIS_ATRIBUTOS[attr]}+1" for attr in buffs_escolhidos)
        equipamento = f"[{emoji}] {nome_arma} [1] [{buffs_formatados}] [20/20]"

        for i in range(1, 11):
            slot = f"Item{i}"
            if getattr(armas, slot) == "":
                setattr(armas, slot, equipamento)
                break

        session.commit()
        await query.message.reply_text(
            f"🔥 <b>Forja Concluída!</b> 🔨\n"
            f"Parabéns, guerreiro! A chama dos anões te favoreceu.\n"
            f"Você criou um novo equipamento: <b>{equipamento}</b> ⚔️\n\n"
            f"🌟 <i>+10 XP de Forja</i>\n"
            f"Seu martelo ressoou nos salões de Nidavellir... e os deuses ouviram.",
            parse_mode="HTML")
    else:
        session.commit()
        await query.message.reply_text(
            "💥 <b>Forja Fracassada</b> ❌\n"
            "A bigorna tremeu, o aço não cedeu...\n"
            "O item se perdeu entre as brasas e a fumaça.\n\n"
            "🛠️ <i>O destino não sorriu desta vez.</i>\n"
            "Tente novamente, pois até os deuses erram antes de criar algo digno de lenda.",
            parse_mode="HTML")

    session.close()
