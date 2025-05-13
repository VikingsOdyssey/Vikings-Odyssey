import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto
from libs.emoji_atributos import EMOJIS_ATRIBUTOS

QUALIDADES = [
    ("🔵", "Comum", 3),
    ("🟠", "Bom", 7),
    ("🔴", "Perfeito", 20),
    ("🟢", "Divino", 70),
]

ARMAS_POR_CLASSE = {
    "Espadachim": "Lâmina de Skuld",
    "Caçador": "Arco de Fenrir",
    "Guardião": "Espada de Ymir",
    "Lanceiro": "Lança de Nidhöggr",
    "Bárbaro": "Machado de Surtr",
    "Arcano": "Cedro de Mímir"
}

async def forja_armas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = ler_texto("../texts/midtheim/ferreiro/forja/forja_armas.txt")
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

    chat_id = str(query.message.chat_id)
    ref = db.reference(f"{chat_id}")
    perfil = ref.child("Perfil").get()
    inventario = ref.child("Inventario").get()
    armas_ref = ref.child("Equipamentos/Armas")
    armas = armas_ref.get()

    if inventario["Madeira"] < 3 or inventario["Aco"] < 6 or inventario["Joia_Criacao"] < 1:
        await query.message.reply_text(
            "❌ Você não possui recursos suficientes para forjar uma arma.", parse_mode="HTML")
        return

    nivel_forja = perfil["Nivel_Forja"]
    chance_sucesso = min(50 + (nivel_forja - 1) * 5, 100)
    sucesso = random.randint(1, 100) <= chance_sucesso

    # Consome recursos
    inventario["Madeira"] -= 3
    inventario["Aco"] -= 6
    inventario["Joia_Criacao"] -= 1
    ref.child("Inventario").set(inventario)

    if sucesso:
        perfil["Xp_Forja"] += 10
        ref.child("Perfil").update({"Xp_Forja": perfil["Xp_Forja"]})

        qualidade = random.choices(QUALIDADES, weights=[q[2] for q in QUALIDADES[::-1]], k=1)[0]
        emoji, nome_qualidade, _ = qualidade
        nome_arma = ARMAS_POR_CLASSE.get(perfil["Classe"], "Arma Misteriosa")
        atributo_ataque = ref.child("Atributos/atributo_ataque").get()

        buffs_possiveis = list(set(EMOJIS_ATRIBUTOS.keys()))
        quantidade_buffs = QUALIDADES.index(qualidade) + 1
        buffs_escolhidos = [atributo_ataque] + random.sample(buffs_possiveis, quantidade_buffs - 1)

        buffs_formatados = ", ".join(f"{EMOJIS_ATRIBUTOS[attr.lower()]}+1" for attr in buffs_escolhidos)
        equipamento = f"[20/20] [{emoji}] {nome_arma} [1] [{buffs_formatados}]"

        for i in range(1, 11):
            slot = f"Item{i}"
            if not armas.get(slot):
                armas_ref.child(slot).set(equipamento)
                break

        await query.message.reply_text(
            f"🔥 <b>Forja Concluída!</b> 🔨\n"
            f"Parabéns, guerreiro! A chama dos anões te favoreceu.\n"
            f"Você criou um novo equipamento: <b>{equipamento}</b> ⚔️\n\n"
            f"🌟 <i>+10 XP de Forja</i>\n"
            f"Seu martelo ressoou nos salões de Nidavellir... e os deuses ouviram.",
            parse_mode="HTML")
    else:
        await query.message.reply_text(
            "💥 <b>Forja Fracassada</b> ❌\n"
            "A bigorna tremeu, o aço não cedeu...\n"
            "O item se perdeu entre as brasas e a fumaça.\n\n"
            "🛠️ <i>O destino não sorriu desta vez.</i>\n"
            "Tente novamente, pois até os deuses erram antes de criar algo digno de lenda.",
            parse_mode="HTML")
