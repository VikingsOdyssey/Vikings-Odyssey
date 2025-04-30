# Importa modulos e bibliotecas
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from database.config import SessionLocal # type: ignore
from database.models import Jogador, Inventario, Arma, Elmo, Armadura, Calca, Bota, Amuleto, Equipado # type: ignore
from database.init_db import init_db # type: ignore
from libs.classes import classes_atributos # type: ignore
from dotenv import load_dotenv
from handlers.midtheim.menu_midtheim import menu_midtheim # type: ignore
from handlers.midtheim.personagem import personagem # type: ignore
from handlers.midtheim.personagem import inventario # type: ignore
from handlers.midtheim.personagem import status # type: ignore
from handlers.midtheim.personagem.equipamentos import equipamentos # type: ignore
from handlers.midtheim.personagem.equipamentos import armas
from handlers.midtheim.personagem.equipamentos import elmo
from handlers.midtheim.personagem.equipamentos import armadura
from handlers.midtheim.personagem.equipamentos import calça
from handlers.midtheim.personagem.equipamentos import bota
from handlers.midtheim.personagem.equipamentos import amuleto
from handlers.midtheim.arena import arena
#from handlers.midtheim.arena import combate_rankeado
#from handlers.midtheim.arena import combate_amistoso
#from handlers.midtheim.arena import ranking
#from handlers.midtheim.ferreiro import ferreiro
#from handlers.midtheim.ferreiro.forja import menu_forja
#from handlers.midtheim.ferreiro.forja import forja_armas
load_dotenv()

# Estados da conversa
NOME, CLASSE = range(2)

# Lista de classes
CLASSES_DISPONIVEIS = [
    "Espadachim", "Lancero",         # Armas longas
    "Caçador", "Arcano",             # Combate à distância
    "Bárbaro", "Guardião"            # Corpo a corpo
]
# define diretorio raiz
def ler_texto(caminho_relativo):
    base_dir = os.path.dirname(__file__)
    caminho_absoluto = os.path.join(base_dir, caminho_relativo)
    with open(caminho_absoluto, "r", encoding="utf-8") as f:
        return f.read()
# cadastra ChatID no banco de dados
def criar_dados_iniciais(session, chat_id):
    session.add_all([
        Inventario(chat_id=chat_id),
        Arma(chat_id=chat_id),
        Elmo(chat_id=chat_id),
        Armadura(chat_id=chat_id),
        Calca(chat_id=chat_id),
        Bota(chat_id=chat_id),
        Amuleto(chat_id=chat_id),
        Equipado(chat_id=chat_id)
    ])
    session.commit()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    chat_id = str(update.effective_chat.id)
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    # envia jogador ja cadastrado para o menu
    if jogador and jogador.nome != "A definir" and jogador.classe != "A definir":
        await menu_midtheim(update, context)
        session.close()
        return ConversationHandler.END
    #inicia cadastro
    if not jogador:
        jogador = Jogador(chat_id=chat_id, nome="A definir", classe="A definir")
        session.add(jogador)
        session.commit()
        criar_dados_iniciais(session, chat_id)

    await update.message.reply_text(ler_texto("texts/cadastro/nome.txt"), parse_mode="HTML")
    session.close()
    return NOME

# Receber nome
async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text
    session = SessionLocal()
    chat_id = str(update.effective_chat.id)
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    jogador.nome = nome
    session.commit()
    session.close()

    keyboard = [
        [InlineKeyboardButton(classe, callback_data=classe)]
        for classe in CLASSES_DISPONIVEIS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    texto = ler_texto("texts/cadastro/classe.txt").format(nome=nome)
    await update.message.reply_text(
        texto,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return CLASSE

# Escolher classe
async def escolher_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    classe_escolhida = query.data

    session = SessionLocal()
    chat_id = str(query.message.chat.id)
    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    jogador.classe = classe_escolhida
    atributos = classes_atributos.get(classe_escolhida)
    if atributos:
        jogador.destreza = atributos["destreza"]
        jogador.dominio = atributos["dominio"]
        jogador.precisao = atributos["precisao"]
        jogador.magia = atributos["magia"]
        jogador.furia = atributos["furia"]
        jogador.forca = atributos["forca"]
        jogador.resistencia = atributos["resistencia"]
        jogador.bencao = atributos["bencao"]
        jogador.velocidade = atributos["velocidade"]
        jogador.atributo_ataque = atributos["atributo_ataque"]

    session.commit()
    session.close()

    await query.edit_message_reply_markup(reply_markup=None)
    await menu_midtheim(update, context)
    return ConversationHandler.END

# Main
def main():
    init_db()
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start)], states={NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)], CLASSE: [CallbackQueryHandler(escolher_classe)], }, fallbacks=[])
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(menu_midtheim, pattern="^menu_midtheim$"))
    app.add_handler(CallbackQueryHandler(personagem.mostrar_ficha, pattern="^personagem$"))
    app.add_handler(CallbackQueryHandler(inventario.mostrar_inventario, pattern="^inventario$"))
    app.add_handler(CallbackQueryHandler(status.mostrar_status, pattern= "^status$"))
    app.add_handler(CallbackQueryHandler(equipamentos.mostrar_equipamentos, pattern="^equipamentos$"))
    app.add_handler(CallbackQueryHandler(armas.mostrar_armas, pattern="^arma$"))
    app.add_handler(CallbackQueryHandler(armas.selecionar_arma, pattern="^(I[0-9]+|desequipar_arma)"))
    app.add_handler(CallbackQueryHandler(elmo.mostrar_elmos, pattern="^elmo$"))
    app.add_handler(CallbackQueryHandler(elmo.selecionar_elmo, pattern="^(I[0-9]+|desequipar_elmo)"))
    app.add_handler(CallbackQueryHandler(armadura.mostrar_armaduras, pattern="^armadura$"))
    app.add_handler(CallbackQueryHandler(armadura.selecionar_armadura, pattern="^(I[0-9]+|desequipar_armadura)"))
    app.add_handler(CallbackQueryHandler(calça.mostrar_calcas, pattern="^calca$"))
    app.add_handler(CallbackQueryHandler(calça.selecionar_calca, pattern="^(I[0-9]+|desequipar_calca)"))
    app.add_handler(CallbackQueryHandler(bota.mostrar_botas, pattern="^bota$"))
    app.add_handler(CallbackQueryHandler(bota.selecionar_bota, pattern="^(I[0-9]+|desequipar_bota)"))
    app.add_handler(CallbackQueryHandler(amuleto.mostrar_amuletos, pattern="^amuleto$"))
    app.add_handler(CallbackQueryHandler(amuleto.selecionar_amuleto, pattern="^(I[0-9]+|desequipar_amuleto)"))
    app.add_handler(CallbackQueryHandler(arena.menu_arena, pattern="^arena$"))
    #app.add_handler(CallbackQueryHandler(combate_rankeado.iniciar_arena_rankeada, pattern="^arena_rankeado$"))
    #app.add_handler(ConversationHandler(
    #entry_points=[CallbackQueryHandler(combate_amistoso.iniciar_combate_amistoso, pattern="^arena_amistoso$")],
    #states={
    #    combate_amistoso.BUSCA_OPONENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, combate_amistoso.resolver_combate)],
    #},
    #fallbacks=[],
#))
    #app.add_handler(CallbackQueryHandler(ranking.mostrar_ranking, pattern="^ranking_arena$"))
    #app.add_handler(CallbackQueryHandler(ferreiro.menu_ferreiro, pattern="^forja$"))
    #app.add_handler(CallbackQueryHandler(menu_forja.menu_forja_equipamento, pattern="^forjar_equipamento$"))
    #app.add_handler(CallbackQueryHandler(forja_armas.forja_armas_menu, pattern="^forjar_arma$"))
    #app.add_handler(CallbackQueryHandler(forja_armas.criar_arma, pattern="^criar_arma$"))
    app.run_polling()

if __name__ == "__main__":
    main()