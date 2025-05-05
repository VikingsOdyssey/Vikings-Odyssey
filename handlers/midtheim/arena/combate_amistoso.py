from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database.config import SessionLocal
from database.models import Jogador, Equipado
from utils.ler_texto import ler_texto
from utils.atributos_calc import calcular_atributos, calcular_dano_com_reducao
from utils.equipamento_durabilidade import extrair_equipamentos_danificados, registrar_uso_de_equipado
import os
import random
import time

BUSCA_OPONENTE = 1
duelo_cooldowns = {}
TEMPO_COOLDOWN = 60  # segundos

async def iniciar_combate_amistoso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    session = SessionLocal()
    chat_id = str(update.effective_user.id)

    jogadores = session.query(Jogador).filter(
        Jogador.nome != "A definir",
        Jogador.chat_id != chat_id
    ).all()

    lista = "<b>Lista de Oponentes:</b>\n<code>Escolha com sabedoria...</code>\n"

    for j in jogadores:
        eq = session.query(Equipado).filter_by(chat_id=j.chat_id).first()
        atributos, *_ = calcular_atributos(j, eq)
        atributo = j.atributo_ataque or "forca"
        pc = atributos.get("resistencia", 0) + atributos.get(atributo, 0)
        nome_curto = j.nome[:25].ljust(25)
        lista += f"<code>Nome: {nome_curto}\nPC: {str(pc).rjust(5)}</code>\n\n"

    session.close()
    await update.callback_query.message.reply_text(
        lista + "\n\n<b>Digite o nome do jogador que deseja desafiar:</b>",
        parse_mode="HTML"
    )
    return BUSCA_OPONENTE

async def resolver_combate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_oponente = update.message.text.strip()
    chat_id = str(update.effective_chat.id)

    agora = time.time()
    ultimo = duelo_cooldowns.get(chat_id, 0)
    if agora - ultimo < TEMPO_COOLDOWN:
        restante = int(TEMPO_COOLDOWN - (agora - ultimo))
        await update.message.reply_text(f"Você deve esperar {restante} segundos antes de iniciar outro duelo.")
        return ConversationHandler.END

    session = SessionLocal()
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    oponente = session.query(Jogador).filter_by(nome=nome_oponente).first()

    if not oponente or oponente.chat_id == chat_id:
        await update.message.reply_text("Oponente inválido. Verifique o nome digitado.")
        session.close()
        return ConversationHandler.END

    eq_jogador = session.query(Equipado).filter_by(chat_id=chat_id).first()
    eq_oponente = session.query(Equipado).filter_by(chat_id=oponente.chat_id).first()

    meus_attr, vida1, agi1, crit1, dano1 = calcular_atributos(jogador, eq_jogador)
    attrs_op, vida2, agi2, crit2, dano2 = calcular_atributos(oponente, eq_oponente)

    vida1_ini, vida2_ini = vida1, vida2

    ordem = (
        [(jogador, dano1, crit1, attrs_op, eq_jogador, "vida2", oponente.classe),
         (oponente, dano2, crit2, meus_attr, eq_oponente, "vida1", jogador.classe)]
        if agi1 >= agi2 else
        [(oponente, dano2, crit2, meus_attr, eq_oponente, "vida1", jogador.classe),
         (jogador, dano1, crit1, attrs_op, eq_jogador, "vida2", oponente.classe)]
    )

    log = ""
    rodada = 1
    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atk, dano_base, crit, defensor_attr, _, alvo, classe_defensor in ordem:
            critado = random.randint(1, 100) <= crit
            dano = calcular_dano_com_reducao(
                dano_base, critado,
                atk.atributo_ataque or "forca",
                defensor_attr,
                atk.classe,
                classe_defensor
            )
            if alvo == "vida1":
                vida1 = max(0, vida1 - dano)
                log += f"{atk.nome} causou {dano} de dano em {jogador.nome} | Vida de {jogador.nome}: ♥️{vida1}\n"
            else:
                vida2 = max(0, vida2 - dano)
                log += f"{atk.nome} causou {dano} de dano em {oponente.nome} | Vida de {oponente.nome}: ♥️{vida2}\n"
            if vida1 <= 0 or vida2 <= 0:
                break
        rodada += 1
        log += "\n"

    resultado = (
        f"{jogador.nome} venceu" if vida1 > vida2 else
        f"{oponente.nome} venceu" if vida2 > vida1 else "Empate"
    )

    danificados = extrair_equipamentos_danificados(eq_jogador)
    registrar_uso_de_equipado(eq_jogador)

    texto = ler_texto("../texts/midtheim/arena/combate_amistoso.txt").format(
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
        Log=log + (f"<i>Itens danificados ignorados: {', '.join(danificados)}</i>" if danificados else "")
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Voltar", callback_data="arena_amistoso")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await update.message.reply_text(texto, reply_markup=teclado, parse_mode="HTML")
    duelo_cooldowns[chat_id] = time.time()
    session.commit()
    session.close()
    return ConversationHandler.END
