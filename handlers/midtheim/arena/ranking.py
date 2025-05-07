from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from firebase_admin import db

CATEGORIAS = {
    "Bronze": (0, 40),
    "Ferro": (41, 80),
    "Prata": (81, 120),
    "Ouro": (121, 160),
    "Diamante": (161, 9999),
}

CATEGORIAS_EMOJIS = {
    "Bronze": "🟤",
    "Ferro": "⚫",
    "Prata": "⚪",
    "Ouro": "🟡",
    "Diamante": "💎"
}

def obter_categoria_em_emoji(rank):
    
    for nome, (min_r, max_r) in CATEGORIAS.items():
        if min_r <= rank <= max_r:
            return CATEGORIAS_EMOJIS[nome]
    return "❓"

async def mostrar_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    ref = db.reference("/")
    todos_usuarios = ref.get()
    chat_id = str(update.effective_user.id)

    ranking = []

    for uid, dados in todos_usuarios.items():
        perfil = dados.get("Perfil", {})
        nome = perfil.get("Nome", "")
        rank = perfil.get("Rank", 0)

        if nome != "A definir":
            ranking.append({
                "chat_id": uid,
                "nome": nome,
                "rank": rank
            })

    ranking_ordenado = sorted(ranking, key=lambda x: x["rank"], reverse=True)

    texto = "<b>🏆 Ranking da Arena</b>\n\n"
    player_pos = None

    for i, jogador in enumerate(ranking_ordenado[:10], start=1):
        emoji = obter_categoria_em_emoji(jogador["rank"])
        texto += f"{i}° {emoji} {jogador['nome']}\n"

    for i, jogador in enumerate(ranking_ordenado, start=1):
        if jogador["chat_id"] == chat_id and i > 10:
            emoji = obter_categoria_em_emoji(jogador["rank"])
            texto += f"\n{i}° {emoji} {jogador['nome']} (você)\n"
            break
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="arena")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")

