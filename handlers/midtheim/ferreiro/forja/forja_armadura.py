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
RECEITA = {"Joia_Criacao": 1, "Aco": 6, "Couro": 2, "Pedra": 2}

async def forja_armadura_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    texto = ler_texto("../texts/midtheim/ferreiro/forja/forja_armadura.txt")
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Criar", callback_data="criar_armadura")],
        [InlineKeyboardButton("Voltar", callback_data="forjar_equipamento")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")],
    ])
    await query.message.reply_text(text=texto, parse_mode="HTML", reply_markup=teclado)


async def criar_armadura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    ref = db.reference(f"{chat_id}")
    perfil = ref.child("Perfil").get()
    inventario = ref.child("Inventario").get()
    armaduras = ref.child("Equipamentos/Armaduras").get()
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data="forja")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])


    # Verifica recursos
    for recurso, qtd in RECEITA.items():
        if inventario.get(recurso, 0) < qtd:
            await query.message.reply_text(
            "❌ Você não possui recursos suficientes para forjar uma arma.", reply_markup = teclado, parse_mode="HTML")
            return

    # Gasta os recursos
    for recurso, qtd in RECEITA.items():
        ref.child("Inventario").child(recurso).set(inventario[recurso] - qtd)

    nivel_forja = perfil.get("Nivel_Forja", 1)
    sucesso = random.randint(1, 100) <= min(50 + (nivel_forja - 1) * 5, 100)

    if sucesso:
        ref.child("Perfil/Xp_Forja").set(perfil.get("Xp_Forja", 0) + 10)
        qualidade = random.choices(QUALIDADES, weights=[q[2] for q in QUALIDADES[::-1]], k=1)[0]
        emoji, nome_qualidade, _ = qualidade

        buffs_possiveis = list(set(EMOJIS_ATRIBUTOS.keys()) - {"resistencia"})
        qtd_buffs = QUALIDADES.index(qualidade) + 1
        buffs_escolhidos = ["resistencia"] + random.sample(buffs_possiveis, qtd_buffs - 1)
        buffs = ", ".join(f"{EMOJIS_ATRIBUTOS[b]}+1" for b in buffs_escolhidos)
        equipamento = f"[20/20] [{emoji}] Armadura de Ferro [1] [{buffs}]"

        for i in range(1, 11):
            if armaduras.get(f"Item{i}") == "":
                ref.child(f"Equipamentos/Armaduras/Item{i}").set(equipamento)
                break

        await query.message.reply_text(
            f"🔥 <b>Forja Concluída!</b> 🔨\n"
            f"Parabéns, guerreiro! A chama dos anões te favoreceu.\n"
            f"Você criou um novo equipamento: <b>{equipamento}</b>\n\n"
            f"🌟 <i>+10 XP de Forja</i>\n"
            f"Seu martelo ressoou nos salões de Nidavellir... e os deuses ouviram.", reply_markup = teclado,
            parse_mode="HTML")
    else:
        await query.message.reply_text(
            "💥 <b>Forja Fracassada</b> ❌\n"
            "A bigorna tremeu, o aço não cedeu...\n"
            "O item se perdeu entre as brasas e a fumaça.\n\n"
            "🛠️ <i>O destino não sorriu desta vez.</i>\n"
            "Tente novamente, pois até os deuses erram antes de criar algo digno de lenda.", reply_markup = teclado,
            parse_mode="HTML")
