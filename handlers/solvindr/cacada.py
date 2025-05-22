import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import db
from utils.atributos_calc import calcular_dano_com_reducao, calcular_atributos
from utils.equipamento_durabilidade import registrar_uso_de_equipado
from utils.ler_texto import ler_texto
from libs.mobs import MOBS

EXPLICACAO, COMBATE = range(2)

XP_POR_REGIAO = {
    "solvindr": 50,
    "modrheim": 80,
    "yggdreth": 120,
    "aska": 180,
    "skjovik": 250,
    "hrimgard": 400,
}

MOEDAS_POR_REGIAO = {
    "solvindr": 20,
    "modrheim": 35,
    "yggdreth": 50,
    "aska": 75,
    "skjovik": 100,
    "hrimgard": 150,
}

XP_NECESSARIO = [0, 100, 200, 400, 600, 1200, 1800, 3600, 5400, 10800]

def calcular_atributos_mob(mob):
    atributos = mob.get("atributos", {})
    return {
        "vida": atributos.get("resistencia") * 3,
        "dano": atributos.get(mob.get("atributo_ataque")),
        "agilidade": int(atributos.get("velocidade") * 1.5),
        "critico": atributos.get("precisao") * 1.5,
        "atributos": atributos
    }

async def menu_cacada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)
    await query.edit_message_reply_markup(reply_markup=None)
    texto = ler_texto("../texts/solvindr/cacada.txt")
    local = db.reference(f"{chat_id}/Perfil/Local_Atual").get().lower()
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐺 Caçar", callback_data="iniciar_cacada")],
        [InlineKeyboardButton("↩️ Voltar", callback_data=f"menu_{local}")]
    ])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    return EXPLICACAO

async def iniciar_cacada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)
    entradas_ref = db.reference(f"{chat_id}/Entradas")
    entradas = entradas_ref.get()
    if not entradas or entradas.get("Cacada", 0) <= 0:
        await query.message.reply_text("❌ Você não possui entradas de caçada disponíveis.")
        return ConversationHandler.END

    entradas_ref.update({"Cacada": entradas["Cacada"] - 1})

    local = db.reference(f"{chat_id}/Perfil/Local_Atual").get()
    mobs_da_regiao = MOBS.get(local)
    if not mobs_da_regiao:
        await query.message.reply_text("❌ Esta região ainda não possui inimigos definidos.")
        return ConversationHandler.END

    mob = random.choice(list(mobs_da_regiao.values()))
    atributos_combate = calcular_atributos_mob(mob)
    mob.update(atributos_combate)

    context.user_data["mob_cacada"] = mob
    context.user_data["mob_vida"] = mob["vida"]

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Atacar", callback_data="atacar_mob")],
        [InlineKeyboardButton("🏃 Fugir", callback_data="voltar_local")]
    ])
    await query.message.reply_text(
        f"<b>🐾 Encontrou um inimigo!</b>\n"
        f"<b>Nome:</b> {mob['nome']}\n"
        f"<b>Classe:</b> {mob['classe']}\n"
        f"<b>Vida:</b> ♥️ {mob['vida']}\n"
        f"<b>Dano:</b> {mob['dano']}\n"
        f"<b>Agilidade:</b> {mob['agilidade']}\n"
        f"<b>Crítico:</b> {mob['critico']}%",
        reply_markup=teclado,
        parse_mode="HTML"
    )
    return COMBATE

async def atacar_mob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('inicio do Combate:')
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)
    perfil = db.reference(f"{chat_id}/Perfil").get()
    atributos = db.reference(f"{chat_id}/Atributos").get()
    equipado = db.reference(f"{chat_id}/Equipado").get()

    # Dados do mob
    mob = context.user_data["mob_cacada"]
    mob_vida = context.user_data["mob_vida"]
    mob_agilidade = mob["agilidade"]
    mob_critico = mob["critico"]
    mob_dano = mob["dano"]
    mob_atributo = mob["atributo_ataque"]
    mob_classe = mob["classe"]
    mob_atributos = mob["atributos"]

    # Cálculo do player
    atributos_calc, vida, agilidade, critico, dano = calcular_atributos({"Atributos": atributos, "Equipado": equipado}, equipado)
    log, rodada = "", 1
    player_nome = perfil["Nome"]
    mob_nome = mob["nome"]

    ordem = [
        (player_nome, dano, critico, mob_atributos, "mob"),
        (mob_nome, mob_dano, mob_critico, atributos_calc, "player")
    ]
    if mob_agilidade > agilidade:
        ordem.reverse()

    while vida > 0 and mob_vida > 0 and rodada <= 10:
        log += f"<b>Rodada {rodada}</b>\n"
        for nome, dano_base, crit, defensor_attr, alvo in ordem:
            perfil_ = db.reference(f"{chat_id}/Atributos/").get()
            critado = random.randint(1, 100) <= crit
            dano_calc = calcular_dano_com_reducao(
                dano_base, critado,
                perfil_.get("atributo_ataque") if nome == player_nome else mob_atributo,
                defensor_attr,
                perfil["Classe"] if nome == player_nome else mob_classe,
                mob_classe if nome == player_nome else perfil["Classe"]
            )
            if alvo == "mob":
                mob_vida = max(0, mob_vida - dano_calc)
                log += f"{nome} causou {dano_calc} em {mob_nome} | Vida: ♥️{mob_vida}\n"
            else:
                vida = max(0, vida - dano_calc)
                log += f"{nome} causou {dano_calc} em {player_nome} | Vida: ♥️{vida}\n"
            if vida == 0 or mob_vida == 0:
                break
        rodada += 1
        log += "\n"

    venceu = vida > mob_vida
    local = db.reference(f"{chat_id}/Perfil/Local_Atual").get().lower()
    ganho_xp = XP_POR_REGIAO.get(local, 50)
    ganho_moedas = MOEDAS_POR_REGIAO.get(local, 10)

    inventario_ref = db.reference(f"{chat_id}/Inventario")
    loot_ref = db.reference(f"{chat_id}/Recebimentos")
    perfil_ref = db.reference(f"{chat_id}/Perfil")

    perfil_atual = perfil_ref.get()
    xp_atual = perfil_atual.get("Xp", 0)
    nivel = perfil_atual.get("Nivel", 1)
    novo_xp = xp_atual + (ganho_xp if venceu else -10)
    novo_xp = max(0, novo_xp)

    # Verifica up de nível
    xp_necessario = XP_NECESSARIO[nivel] if nivel < len(XP_NECESSARIO) else 999999
    subiu_nivel = False
    if novo_xp >= xp_necessario:
        novo_xp = 0
        nivel += 1
        subiu_nivel = True

    perfil_ref.update({
        "Xp": novo_xp,
        "Nivel": nivel
    })

    # Atualiza inventário com moedas e loot
    loot_calc = random.random() <= 0.4
    inventario = inventario_ref.get()
    inventario_ref.update({"Moedas": inventario.get("Moedas") + (ganho_moedas if venceu else 0)})
    loot = loot_ref.get()
    loot_ref.update({"Loot_cacada": int(loot.get("Loot_cacada")) + (1 if venceu and loot_calc else 0)})

    # Desgaste dos equipamentos
    registrar_uso_de_equipado(chat_id, db.reference())

    texto_resultado = (
        f"<b>🛡 Combate Finalizado</b>\n"
        f"{'✅ Vitória!' if venceu else '❌ Derrota!'}\n\n"
        f"{log}"
        f"{'🏆 XP ganho: ' + str(ganho_xp) + '\\n' if venceu else '💀 XP perdido: 10\\n'}"
        f"{'🪙 Moedas: ' + str(ganho_moedas) + '\\n' if venceu else ''}"
        f"{'📦 Loot de caçada recebido!\n' if venceu and loot_calc else ''}"
        f"{'⬆️ Você subiu para o nível ' + str(nivel) + '!\n' if subiu_nivel else ''}"
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐺 Caçar", callback_data="iniciar_cacada")],
        [InlineKeyboardButton("↩️ Voltar", callback_data=f"menu_{local}")]
    ])
    print('Fim do Combate\n\n')
    await query.message.reply_text(texto_resultado, reply_markup=teclado, parse_mode="HTML")
    return ConversationHandler.END