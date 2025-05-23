import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
from utils.atributos_calc import calcular_atributos, calcular_dano_com_reducao
from utils.equipamento_durabilidade import registrar_uso_de_equipado, extrair_equipamentos_danificados
from utils.ler_texto import ler_texto

RANKEADA = 1

CATEGORIAS = {
    "Bronze": (0, 40),
    "Ferro": (41, 80),
    "Prata": (81, 120),
    "Ouro": (121, 160),
    "Diamante": (161, 9999),
}

def obter_categoria(rank):
    for nome, (min_r, max_r) in CATEGORIAS.items():
        if min_r <= rank <= max_r:
            return nome
    return "Sem Categoria"

async def iniciar_arena_rankeada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(update.effective_user.id)
    db_ref = db.reference("/")
    jogador_data = db_ref.child(chat_id).get()

    if not jogador_data:
        await update.callback_query.message.reply_text("❌ Perfil não encontrado.")
        return ConversationHandler.END

    entradas = jogador_data.get("Entradas", {})
    if entradas.get("Arena") <= 0:
        texto = "⚠️ Você não possui entradas de Arena disponíveis."
        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="arena")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
        await update.callback_query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return ConversationHandler.END

    categoria = obter_categoria(jogador_data["Perfil"]["Rank"])
    todos = db_ref.get()
    oponentes = [
        (k, v) for k, v in todos.items()
        if k != chat_id and obter_categoria(v["Perfil"]["Rank"]) == categoria
    ]

    if not oponentes:
        texto = "Nenhum oponente disponível na sua categoria."
        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="arena")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
        await update.callback_query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return ConversationHandler.END

    op_chat_id, oponente = random.choice(oponentes)

    meus_attr, vida1, agi1, crit1, dano1 = calcular_atributos(jogador_data, jogador_data.get("Equipado", {}))
    op_attr, vida2, agi2, crit2, dano2 = calcular_atributos(oponente, oponente.get("Equipado", {}))

    vida1_ini, vida2_ini = vida1, vida2
    Pontos_Anteriores, Pontos_Oponente_Ant = jogador_data["Perfil"]["Rank"], oponente["Perfil"]["Rank"]

    ordem = [(jogador_data, dano1, crit1, op_attr, "vida2"), (oponente, dano2, crit2, meus_attr, "vida1")]
    if agi2 > agi1:
        ordem.reverse()

    log, rodada = "", 1
    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atacante, dano_base, crit, defesa_attr, alvo in ordem:
            critado = random.randint(1, 100) <= crit
            dano = calcular_dano_com_reducao(
                dano_base, critado,
                atacante["Atributos"]["atributo_ataque"].lower(),
                defesa_attr,
                atacante["Perfil"]["Classe"],
                ordem[1][0]["Perfil"]["Classe"]
            )
            if alvo == "vida1":
                vida1 = max(0, vida1 - dano)
                log += f"{atacante['Perfil']['Nome']} causou {dano} em {jogador_data['Perfil']['Nome']} | Vida: ♥️{vida1}\n"
            else:
                vida2 = max(0, vida2 - dano)
                log += f"{atacante['Perfil']['Nome']} causou {dano} em {oponente['Perfil']['Nome']} | Vida: ♥️{vida2}\n"
            if vida1 == 0 or vida2 == 0:
                break
        rodada += 1
        log += "\n"

    if vida1 > vida2:
        resultado = f"{jogador_data['Perfil']['Nome']} venceu"
        jogador_data["Perfil"]["Rank"] += 3
        oponente["Perfil"]["Rank"] = max(0, oponente["Perfil"]["Rank"] - 1)
    elif vida2 > vida1:
        resultado = f"{oponente['Perfil']['Nome']} venceu"
        jogador_data["Perfil"]["Rank"] = max(0, jogador_data["Perfil"]["Rank"] - 1)
        oponente["Perfil"]["Rank"] += 3
    else:
        resultado = "Empate"

    jogador_data["Equipado"] = db_ref.child(f"{chat_id}/Equipado").get()
    danificados = extrair_equipamentos_danificados(jogador_data["Equipado"])
    texto_danificados = ""
    if danificados:
        texto_danificados = "\n⚠️ Os seguintes equipamentos estavam danificados e foram ignorados:\n"
        texto_danificados += "\n".join(f"• {d}" for d in danificados)

    jogador_data["Entradas"]["Arena"] -= 1
    db_ref.child(chat_id).update(jogador_data)
    db_ref.child(op_chat_id).child("Perfil").child("Rank").set(oponente["Perfil"]["Rank"])

    texto = ler_texto("../texts/midtheim/arena/combate_ranqueado.txt").format(
        resultado=resultado,
        Nome=jogador_data["Perfil"]["Nome"],
        Classe=jogador_data["Perfil"]["Classe"],
        Vida=vida1_ini,
        Dano=dano1,
        Agilidade=agi1,
        Critico=crit1,
        Nome_Oponente=oponente["Perfil"]["Nome"],
        Classe_Oponente=oponente["Perfil"]["Classe"],
        Vida_Oponente=vida2_ini,
        Dano_Oponente=dano2,
        Agilidade_Oponente=agi2,
        Critico_Oponente=crit2,
        Log=log,
        Pontos_Anteriores=Pontos_Anteriores,
        Pontos_Atualizados=jogador_data["Perfil"]["Rank"],
        Pontos_Oponente_Ant=Pontos_Oponente_Ant,
        Pontos_Oponente_Novo=oponente["Perfil"]["Rank"]
    ) + texto_danificados

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Proxímo", callback_data="arena_rankeado")],
        [InlineKeyboardButton("Voltar", callback_data="arena")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await update.callback_query.message.reply_text(texto, reply_markup=teclado, parse_mode="HTML")
    registrar_uso_de_equipado(chat_id, db_ref)
    return ConversationHandler.END
