from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
from utils.ler_texto import ler_texto
from utils.atributos_calc import calcular_atributos, calcular_dano_com_reducao
from utils.equipamento_durabilidade import extrair_equipamentos_danificados, registrar_uso_de_equipado
import random
import time

BUSCA_OPONENTE = 1
duelo_cooldowns = {}
TEMPO_COOLDOWN = 60  # segundos

async def iniciar_combate_amistoso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(update.effective_user.id)
    todos = db.reference("/").get()
    jogadores = {
        cid: data for cid, data in todos.items()
        if data.get("Perfil", {}).get("Nome") != "A definir" and cid != chat_id
    }

    lista = "<b>Lista de Oponentes:</b>\n<code>Escolha com sabedoria...</code>\n"
    for cid, data in jogadores.items():
        atributos, *_ = calcular_atributos(data, data.get("Equipado", {}))
        atributo = data["Atributos"].get("atributo_ataque").lower()
        pc = atributos.get("resistencia") + atributos.get(atributo)
        nome_curto = data["Perfil"]["Nome"][:25].ljust(25)
        lista += f"<code>Nome: {nome_curto}\nPC: {str(pc).rjust(5)}</code>\n\n"

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
        texto = f"Você deve esperar {restante} segundos antes de iniciar outro duelo."
        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="arena_amistoso")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
        await update.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return ConversationHandler.END

    todos = db.reference("/").get()
    jogador_data = todos.get(chat_id)
    oponente_data = next((v for v in todos.values() if v["Perfil"]["Nome"] == nome_oponente), None)

    if not oponente_data or oponente_data == jogador_data:
        texto = "Oponente inválido. Verifique o nome digitado."
        teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="arena_amistoso")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])
        await update.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return ConversationHandler.END

    meus_attr, vida1, agi1, crit1, dano1 = calcular_atributos(jogador_data, jogador_data.get("Equipado", {}))
    attrs_op, vida2, agi2, crit2, dano2 = calcular_atributos(oponente_data, oponente_data.get("Equipado", {}))
    vida1_ini, vida2_ini = vida1, vida2

    ordem = (
        [(jogador_data, dano1, crit1, attrs_op, "vida2", oponente_data["Perfil"]["Classe"]),
         (oponente_data, dano2, crit2, meus_attr, "vida1", jogador_data["Perfil"]["Classe"])]
        if agi1 >= agi2 else
        [(oponente_data, dano2, crit2, meus_attr, "vida1", jogador_data["Perfil"]["Classe"]),
         (jogador_data, dano1, crit1, attrs_op, "vida2", oponente_data["Perfil"]["Classe"])]
    )

    log = ""
    rodada = 1
    while vida1 > 0 and vida2 > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for atk_data, dano_base, crit, defensor_attr, alvo, classe_def in ordem:
            critado = random.randint(1, 100) <= crit
            atributo = atk_data["Atributos"].get("atributo_ataque").lower()
            dano = calcular_dano_com_reducao(
                dano_base, critado, atributo,
                defensor_attr,
                atk_data["Perfil"]["Classe"],
                classe_def
            )
            if alvo == "vida1":
                vida1 = max(0, vida1 - dano)
                log += f"{atk_data['Perfil']['Nome']} causou {dano} de dano em {jogador_data['Perfil']['Nome']} | Vida: ♥️{vida1}\n"
            else:
                vida2 = max(0, vida2 - dano)
                log += f"{atk_data['Perfil']['Nome']} causou {dano} de dano em {oponente_data['Perfil']['Nome']} | Vida: ♥️{vida2}\n"
            if vida1 <= 0 or vida2 <= 0:
                break
        rodada += 1
        log += "\n"

    resultado = (
        f"{jogador_data['Perfil']['Nome']} venceu" if vida1 > vida2 else
        f"{oponente_data['Perfil']['Nome']} venceu" if vida2 > vida1 else "Empate"
    )

    danificados = extrair_equipamentos_danificados(jogador_data["Equipado"])
    db_ref = db.reference(f"{chat_id}/Equipado")
    registrar_uso_de_equipado(chat_id, db_ref)

    texto = ler_texto("../texts/midtheim/arena/combate_amistoso.txt").format(
        resultado=resultado,
        Nome=jogador_data["Perfil"]["Nome"],
        Classe=jogador_data["Perfil"]["Classe"],
        Vida=vida1_ini,
        Dano=dano1,
        Agilidade=agi1,
        Critico=crit1,
        Nome_Oponente=oponente_data["Perfil"]["Nome"],
        Classe_Oponente=oponente_data["Perfil"]["Classe"],
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
    return ConversationHandler.END
