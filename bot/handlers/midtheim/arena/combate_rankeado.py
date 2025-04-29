# bot/handlers/midtheim/arena/arena_rankeada.py
import os
import random
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.config import SessionLocal
from database.models import Jogador, Inventario, Equipado
from utils.atributos import calcular_atributos
from utils.leitor_texto import ler_texto

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
    todos = session.query(Jogador).filter(Jogador.chat_id != chat_id).all()

    oponentes_possiveis = [j for j in todos if obter_categoria(j.rank) == categoria]

    if not oponentes_possiveis:
        await update.callback_query.message.reply_text("Nenhum oponente disponível na sua categoria.")
        session.close()
        return ConversationHandler.END

    oponente = random.choice(oponentes_possiveis)

    meu_eq = session.query(Equipado).filter_by(chat_id=chat_id).first()
    op_eq = session.query(Equipado).filter_by(chat_id=oponente.chat_id).first()

    meus_attr, minha_vida, minha_agilidade, meu_critico, meu_dano = calcular_atributos(jogador, meu_eq)
    attrs_op, vida_op, agilidade_op, critico_op, dano_op = calcular_atributos(oponente, op_eq)

    vida1_inicial, vida2_inicial = minha_vida, vida_op
    vida1, vida2 = minha_vida, vida_op
    rodada = 1
    log = ""

    # Armazena pontuação antes do combate
    Pontos_Anteriores = jogador.rank
    Pontos_Oponente_Ant = oponente.rank

    if minha_agilidade >= agilidade_op:
        ordem = [(jogador, meu_dano, meu_critico, attrs_op, "vida2"), (oponente, dano_op, critico_op, meus_attr, "vida1")]
    else:
        ordem = [(oponente, dano_op, critico_op, meus_attr, "vida1"), (jogador, meu_dano, meu_critico, attrs_op, "vida2")]

    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atacante, dano_base, critico, defesa_attr, alvo in ordem:
            critado = random.randint(1, 100) <= critico
            dano = dano_base * (2 if critado else 1)
            redutor = defesa_attr.get(atacante.atributo_ataque, 0)
            dano -= redutor
            dano = max(dano, 0)

            if alvo == "vida1":
                vida1 -= int(dano)
                vida1 = max(0, vida1)
                log += f"{atacante.nome} causou {int(dano)} de dano em {jogador.nome} | Vida: ♥️{vida1}\n"
            else:
                vida2 -= int(dano)
                vida2 = max(0, vida2)
                log += f"{atacante.nome} causou {int(dano)} de dano em {oponente.nome} | Vida: ♥️{vida2}\n"

            if vida1 <= 0 or vida2 <= 0:
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

    # Pontos atualizados
    Pontos_Atualizados = jogador.rank
    Pontos_Oponente_Novo = oponente.rank

    inventario.arena -= 1
    session.commit()

    caminho = os.path.join("bot", "textos", "midtheim", "arena", "combate_ranqueado.txt")
    texto_base = ler_texto(caminho)

    texto = texto_base.format(
        resultado=resultado,
        Nome=jogador.nome,
        Classe=jogador.classe,
        Vida=vida1_inicial,
        Dano=meu_dano,
        Agilidade=minha_agilidade,
        Critico=meu_critico,
        Nome_Oponente=oponente.nome,
        Classe_Oponente=oponente.classe,
        Vida_Oponente=vida2_inicial,
        Dano_Oponente=dano_op,
        Agilidade_Oponente=agilidade_op,
        Critico_Oponente=critico_op,
        Log=log,
        Pontos_Anteriores=Pontos_Anteriores,
        Pontos_Atualizados=Pontos_Atualizados,
        Pontos_Oponente_Ant=Pontos_Oponente_Ant,
        Pontos_Oponente_Novo=Pontos_Oponente_Novo
    )

    await update.callback_query.message.reply_text(texto, parse_mode="HTML")
    session.close()
    return ConversationHandler.END
