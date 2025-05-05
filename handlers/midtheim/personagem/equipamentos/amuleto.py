from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Amuleto, Equipado
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

#-------------------------------------------------------------------
# Mostra a lista de amuletos disponíveis
async def mostrar_amuletos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    amuleto = session.query(Amuleto).filter_by(chat_id=chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/amuletos.txt").format(
        amuleto_1=amuleto.Item1 or "Vazio",
        amuleto_2=amuleto.Item2 or "Vazio",
        amuleto_3=amuleto.Item3 or "Vazio",
        amuleto_4=amuleto.Item4 or "Vazio",
        amuleto_5=amuleto.Item5 or "Vazio",
        amuleto_6=amuleto.Item6 or "Vazio",
        amuleto_7=amuleto.Item7 or "Vazio",
        amuleto_8=amuleto.Item8 or "Vazio",
        amuleto_9=amuleto.Item9 or "Vazio",
        amuleto_10=amuleto.Item10 or "Vazio"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_amuleto")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_amuleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    amuleto = session.query(Amuleto).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    # Desequipar
    if escolha == "desequipar_amuleto":
        texto = mover_equipamento_para_inventario(jogador, amuleto, equipado, "amuleto")
        session.commit()
        teclado = teclado_pos_equipar()
        await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        session.close()
        return

    # Equipar novo item
    try:
        slot_index = int(escolha[1:])
        slot_nome = f"Item{slot_index}"
    except ValueError:
        await query.message.reply_text("❌ Seleção inválida.", parse_mode="HTML")
        session.close()
        return

    novo_item = getattr(amuleto, slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(jogador, amuleto, equipado, "amuleto", slot_nome)

    session.commit()
    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
