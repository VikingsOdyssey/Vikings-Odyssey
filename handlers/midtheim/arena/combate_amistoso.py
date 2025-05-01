from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.config import SessionLocal
from database.models import Jogador, Equipado
from utils.ler_texto import ler_texto
from utils.atributos_calc import calcular_atributos, calcular_dano_com_reducao
from utils.equipamento_durabilidade import registrar_uso_equipamentos
import random
import time

BUSCA_OPONENTE = 1
TEMPO_COOLDOWN = 60
duelo_cooldowns = {}

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

    meus_attr, minha_vida, minha_agilidade, meu_critico, meu_dano = calcular_atributos(jogador, eq_jogador)
    attrs_op, vida_op, agilidade_op, critico_op, dano_op = calcular_atributos(oponente, eq_oponente)

    vida1_inicial, vida2_inicial = minha_vida, vida_op
    vida1, vida2 = minha_vida, vida_op
    log = ""
    rodada = 1

    if minha_agilidade >= agilidade_op:
        ordem = [(jogador, meu_dano, meu_critico, attrs_op, "vida2"),
                 (oponente, dano_op, critico_op, meus_attr, "vida1")]
    else:
        ordem = [(oponente, dano_op, critico_op, meus_attr, "vida1"),
                 (jogador, meu_dano, meu_critico, attrs_op, "vida2")]

    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atacante, dano_base, chance_crit, defensor_attrs, alvo in ordem:
            critado = random.randint(1, 100) <= chance_crit
            atributo_ataque = atacante.atributo_ataque or "forca"
            dano_final = calcular_dano_com_reducao(dano_base, critado, atributo_ataque, defensor_attrs, classe_atacante=atacante.classe, classe_defensor=jogador.classe if alvo == "vida1" else oponente.classe)

            if alvo == "vida1":
                vida1 -= dano_final
                vida1 = max(0, vida1)
                log += f"{atacante.nome} causou {dano_final} de dano em {jogador.nome} | Vida de {jogador.nome}: ♥️{vida1}\n"
            else:
                vida2 -= dano_final
                vida2 = max(0, vida2)
                log += f"{atacante.nome} causou {dano_final} de dano em {oponente.nome} | Vida de {oponente.nome}: ♥️{vida2}\n"

            if vida1 <= 0 or vida2 <= 0:
                break
        rodada += 1
        log += "\n"

    if vida1 > vida2:
        resultado = f"{jogador.nome} venceu"
    elif vida2 > vida1:
        resultado = f"{oponente.nome} venceu"
    else:
        resultado = "Empate"

    texto = ler_texto("../texts/midtheim/arena/combate_amistoso.txt").format(
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
        Log=log
    )

    await update.message.reply_text(texto, parse_mode="HTML")

    # ↓↓↓ Reduz durabilidade após o combate ↓↓↓
    equipamentos_usados = [
        eq_jogador.arma, eq_jogador.elmo, eq_jogador.armadura,
        eq_jogador.calca, eq_jogador.bota, eq_jogador.amuleto
    ]
    equipamentos_atualizados = registrar_uso_equipamentos(equipamentos_usados)

    (
        eq_jogador.arma, eq_jogador.elmo, eq_jogador.armadura,
        eq_jogador.calca, eq_jogador.bota, eq_jogador.amuleto
    ) = equipamentos_atualizados

    session.commit()
    duelo_cooldowns[chat_id] = time.time()
    session.close()
    return ConversationHandler.END
