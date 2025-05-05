import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database.config import SessionLocal
from database.models import Jogador, Inventario, Equipado
from utils.atributos_calc import calcular_atributos
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

    session = SessionLocal()
    chat_id = str(update.effective_user.id)

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    inventario = session.query(Inventario).filter_by(chat_id=chat_id).first()

    if inventario.arena <= 0:
        await update.callback_query.message.reply_text("⚠️ Você não possui entradas de Arena disponíveis.")
        session.close()
        return ConversationHandler.END

    categoria = obter_categoria(jogador.rank)
    oponentes = session.query(Jogador).filter(Jogador.chat_id != chat_id).all()
    oponentes_mesma_cat = [j for j in oponentes if obter_categoria(j.rank) == categoria]

    if not oponentes_mesma_cat:
        await update.callback_query.message.reply_text("Nenhum oponente disponível na sua categoria.")
        session.close()
        return ConversationHandler.END

    oponente = random.choice(oponentes_mesma_cat)

    meu_eq = session.query(Equipado).filter_by(chat_id=chat_id).first()
    op_eq = session.query(Equipado).filter_by(chat_id=oponente.chat_id).first()

    meus_attr, vida1, agi1, crit1, dano1 = calcular_atributos(jogador, meu_eq)
    op_attr, vida2, agi2, crit2, dano2 = calcular_atributos(oponente, op_eq)

    vida1_ini, vida2_ini = vida1, vida2
    Pontos_Anteriores, Pontos_Oponente_Ant = jogador.rank, oponente.rank

    log, rodada = "", 1
    ordem = [(jogador, dano1, crit1, op_attr, "vida2"), (oponente, dano2, crit2, meus_attr, "vida1")]
    if agi2 > agi1:
        ordem.reverse()

    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atacante, dano_base, crit, defesa_attr, alvo in ordem:
            critado = random.randint(1, 100) <= crit
            dano = dano_base * (2 if critado else 1)

            defesa = defesa_attr.get(atacante.atributo_ataque, 0)
            dano -= min(dano * 0, defesa)  # no máximo 80% de redução
            dano = max(1, int(dano))  # dano mínimo garantido

            if alvo == "vida1":
                vida1 = max(0, vida1 - dano)
                log += f"{atacante.nome} causou {dano} em {jogador.nome} | Vida: ♥️{vida1}\n"
            else:
                vida2 = max(0, vida2 - dano)
                log += f"{atacante.nome} causou {dano} em {oponente.nome} | Vida: ♥️{vida2}\n"

            if vida1 == 0 or vida2 == 0:
                break
        rodada += 1
        log += "\n"

    if vida1 > vida2:
        resultado = f"{jogador.nome} venceu"
        jogador.rank += 3
        oponente.rank = max(0, oponente.rank - 1)
    elif vida2 > vida1:
        resultado = f"{oponente.nome} venceu"
        jogador.rank = max(0, jogador.rank - 1)
        oponente.rank += 3
    else:
        resultado = "Empate"

    registrar_uso_de_equipado(meu_eq)
    danificados = extrair_equipamentos_danificados(meu_eq)

    texto_danificados = ""
    if danificados:
        texto_danificados = "\n⚠️ Os seguintes equipamentos estavam danificados e foram ignorados:\n"
        texto_danificados += "\n".join(f"• {d}" for d in danificados)

    inventario.arena -= 1
    session.commit()

    texto = ler_texto("../texts/midtheim/arena/combate_ranqueado.txt").format(
        resultado=resultado,
        Nome=jogador.nome,
        Classe=jogador.classe,
        Vida=vida1_ini,
        Dano=dano1,
        Agilidade=agi1,
        Critico=crit1,
        Nome_Oponente=oponente.nome,
        Classe_Oponente=oponente.classe,
        Vida_Oponente=vida2_ini,
        Dano_Oponente=dano2,
        Agilidade_Oponente=agi2,
        Critico_Oponente=crit2,
        Log=log,
        Pontos_Anteriores=Pontos_Anteriores,
        Pontos_Atualizados=jogador.rank,
        Pontos_Oponente_Ant=Pontos_Oponente_Ant,
        Pontos_Oponente_Novo=oponente.rank
    ) + texto_danificados
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data="arena_rankeado")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await update.callback_query.message.reply_text(texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
    return ConversationHandler.END
