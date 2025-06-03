import os
import sys
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db
from libs.classes import classes_atributos
from utils.firebase_utils import criar_dados_iniciais
from handlers import coming_soon
from handlers.geral.viagem import menu_viagem
from handlers.geral.personagem import entradas_diarias
from handlers.geral.personagem import personagem, inventario, status
from handlers.geral.personagem.equipamentos import equipamentos, armas, elmo, armadura, calca, bota, amuleto
from handlers.geral.loot_box import loot_open
from handlers.midtheim.menu_midtheim import menu_midtheim
from handlers.midtheim.arena import arena, combate_amistoso, combate_rankeado, ranking
from handlers.midtheim.ferreiro import ferreiro
from handlers.midtheim.ferreiro.reparo import reparo
from handlers.midtheim.ferreiro.desmanche import desmanche
from handlers.midtheim.ferreiro.forja import forja, forja_arma, forja_elmo, forja_armadura, forja_calca, forja_bota
from handlers.midtheim.ferreiro.aprimoramento import aprimoramento
from handlers.solvindr.menu_solvindr import menu_solvindr
from handlers.solvindr import cacada

load_dotenv()
firebase_cred = credentials.Certificate("firebase_config.json")
initialize_app(firebase_cred, {'databaseURL': os.getenv("FIREBASE_DB_URL")})

NOME, CLASSE = range(2)
CLASSES_DISPONIVEIS = ["Espadachim", "Lanceiro", "Caçador", "Arcano", "Bárbaro", "Guardião"]

def ler_texto(caminho_relativo):
    base_dir = os.path.dirname(__file__)
    caminho_absoluto = os.path.join(base_dir, caminho_relativo)
    with open(caminho_absoluto, "r", encoding="utf-8") as f:
        return f.read()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    jogador_ref = db.reference(f"{chat_id}/Perfil")
    jogador = jogador_ref.get()
    if jogador and jogador.get("Nome") != "A definir" and jogador.get("Classe") != "A definir":
        local_atual = jogador.get("Local_Atual", "Midtheim").lower()
        func_name = f"menu_{local_atual}"
        func = globals().get(func_name)
        if callable(func):
            await func(update, context)
            return ConversationHandler.END
        else:
            await update.message.reply_text("Erro: localidade desconhecida.")
            return ConversationHandler.END
    if not jogador:
        criar_dados_iniciais(f"{chat_id}")
    await update.message.reply_text(ler_texto("texts/cadastro/nome.txt"), parse_mode="HTML")
    return NOME

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text
    chat_id = str(update.effective_chat.id)
    db.reference(f"{chat_id}/Perfil/Nome").set(nome)
    keyboard = [[InlineKeyboardButton(classe, callback_data=classe)] for classe in CLASSES_DISPONIVEIS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = ler_texto("texts/cadastro/classe.txt").format(nome=nome)
    await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode="HTML")
    return CLASSE

async def escolher_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    classe = query.data
    chat_id = str(query.message.chat.id)
    jogador_ref = db.reference(f"{chat_id}/Perfil")
    jogador_ref.update({"Classe": classe})
    atributos = classes_atributos.get(classe)
    if atributos:
        db.reference(f"{chat_id}/Atributos").set(atributos)
    await query.edit_message_reply_markup(reply_markup=None)
    await menu_midtheim(update, context)
    return ConversationHandler.END

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            CLASSE: [CallbackQueryHandler(escolher_classe)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(coming_soon.coming_soon, pattern="^coming_soon$"))
    app.add_handler(CallbackQueryHandler(menu_midtheim, pattern="^menu_midtheim$"))
    app.add_handler(CallbackQueryHandler(personagem.mostrar_ficha, pattern="^personagem$"))
    app.add_handler(CallbackQueryHandler(inventario.mostrar_inventario, pattern="^inventario$"))
    app.add_handler(CallbackQueryHandler(status.mostrar_status, pattern="^status$"))
    app.add_handler(CallbackQueryHandler(equipamentos.mostrar_equipamentos, pattern="^equipamentos$"))
    app.add_handler(CallbackQueryHandler(armas.mostrar_armas, pattern="^arma$"))
    app.add_handler(CallbackQueryHandler(armas.selecionar_arma, pattern="^(Arma[0-9]+|desequipar_armas)"))
    app.add_handler(CallbackQueryHandler(elmo.mostrar_elmos, pattern="^elmo$"))
    app.add_handler(CallbackQueryHandler(elmo.selecionar_elmo, pattern="^(Elmo[0-9]+|desequipar_elmo)"))
    app.add_handler(CallbackQueryHandler(armadura.mostrar_armaduras, pattern="^armadura$"))
    app.add_handler(CallbackQueryHandler(armadura.selecionar_armadura, pattern="^(Armadura[0-9]+|desequipar_armadura)"))
    app.add_handler(CallbackQueryHandler(calca.mostrar_calcas, pattern="^calca$"))
    app.add_handler(CallbackQueryHandler(calca.selecionar_calca, pattern="^(Calca[0-9]+|desequipar_calca)"))
    app.add_handler(CallbackQueryHandler(bota.mostrar_botas, pattern="^bota$"))
    app.add_handler(CallbackQueryHandler(bota.selecionar_bota, pattern="^(Bota[0-9]+|desequipar_bota)"))
    app.add_handler(CallbackQueryHandler(amuleto.mostrar_amuletos, pattern="^amuleto$"))
    app.add_handler(CallbackQueryHandler(amuleto.selecionar_amuleto, pattern="^(Amuleto[0-9]+|desequipar_amuleto)"))
    app.add_handler(CallbackQueryHandler(arena.menu_arena, pattern="^arena$"))
    app.add_handler(CallbackQueryHandler(combate_rankeado.iniciar_arena_rankeada, pattern="^arena_rankeado$"))
    app.add_handler(CallbackQueryHandler(combate_amistoso.iniciar_combate_amistoso, pattern="^arena_amistoso$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, combate_amistoso.resolver_combate))
    app.add_handler(CallbackQueryHandler(ranking.mostrar_ranking, pattern="^ranking_arena$"))
    app.add_handler(CallbackQueryHandler(ferreiro.ferreiro, pattern="^ferreiro$"))
    app.add_handler(CallbackQueryHandler(forja.forja, pattern="^forja$"))
    app.add_handler(CallbackQueryHandler(forja_arma.forja_armas_menu, pattern="^forja_arma$"))
    app.add_handler(CallbackQueryHandler(forja_arma.criar_arma, pattern="^criar_arma$"))
    app.add_handler(CallbackQueryHandler(forja_elmo.forja_elmo_menu, pattern="^forja_elmo$"))
    app.add_handler(CallbackQueryHandler(forja_elmo.criar_elmo, pattern="^criar_elmo$"))
    app.add_handler(CallbackQueryHandler(forja_armadura.forja_armadura_menu, pattern="^forja_armadura$"))
    app.add_handler(CallbackQueryHandler(forja_armadura.criar_armadura, pattern="^criar_armadura$"))
    app.add_handler(CallbackQueryHandler(forja_calca.forja_calca_menu, pattern="^forja_calca$"))
    app.add_handler(CallbackQueryHandler(forja_calca.criar_calca, pattern="^criar_calca$"))
    app.add_handler(CallbackQueryHandler(forja_bota.forja_bota_menu, pattern="^forja_bota$"))
    app.add_handler(CallbackQueryHandler(forja_bota.criar_bota, pattern="^criar_bota$"))
    app.add_handler(CallbackQueryHandler(menu_viagem.menu_viagem, pattern="^menu_viagem$"))
    app.add_handler(CallbackQueryHandler(menu_viagem.viajar_para_local, pattern="^viajar_"))
    app.add_handler(CallbackQueryHandler(entradas_diarias.receber_itens_diarios, pattern="^receber_itens_diarios$"))
    app.add_handler(CallbackQueryHandler(menu_solvindr, pattern="^menu_solvindr$"))
    app.add_handler(CallbackQueryHandler(cacada.menu_cacada, pattern="^menu_cacada$"))
    app.add_handler(CallbackQueryHandler(cacada.iniciar_cacada, pattern="^iniciar_cacada$"))
    app.add_handler(CallbackQueryHandler(cacada.atacar_mob, pattern="^atacar_mob$"))
    app.add_handler(CallbackQueryHandler(loot_open.abrir_lootbox, pattern="^abrir_"))
    app.add_handler(CallbackQueryHandler(reparo.menu_reparo, pattern="^menu_reparo$"))
    app.add_handler(CallbackQueryHandler(reparo.executar_reparo, pattern="^reparo_"))
    app.add_handler(CallbackQueryHandler(desmanche.menu_desmanche, pattern="^desmanche_menu$"))
    app.add_handler(CallbackQueryHandler(desmanche.escolher_tipo, pattern="^desmanche_tipo_"))
    app.add_handler(CallbackQueryHandler(desmanche.desmontar_item, pattern="^desmanche_item_"))
    app.add_handler(CallbackQueryHandler(aprimoramento.menu_aprimoramento, pattern="^up$"))
    app.add_handler(CallbackQueryHandler(aprimoramento.selecionar_equipamento, pattern="^aprimorar_"))
    app.add_handler(CallbackQueryHandler(aprimoramento.confirmar_aprimoramento, pattern="^1aprimorar_item_"))
    app.bot_data["menus"] = {"menu_midtheim": menu_midtheim, "menu_solvindr": menu_solvindr}
    app.run_polling()

if __name__ == "__main__":
    main()
