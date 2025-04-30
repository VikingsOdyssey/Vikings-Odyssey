from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Elmo, Equipado
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

#-------------------------------------------------------------------
# Mostra a lista de elmos disponíveis
async def mostrar_elmos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    elmo = session.query(Elmo).filter_by(chat_id=chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/elmos.txt").format(
        elmo_1=elmo.Item1 or "Vazio",
        elmo_2=elmo.Item2 or "Vazio",
        elmo_3=elmo.Item3 or "Vazio",
        elmo_4=elmo.Item4 or "Vazio",
        elmo_5=elmo.Item5 or "Vazio",
        elmo_6=elmo.Item6 or "Vazio",
        elmo_7=elmo.Item7 or "Vazio",
        elmo_8=elmo.Item8 or "Vazio",
        elmo_9=elmo.Item9 or "Vazio",
        elmo_10=elmo.Item10 or "Vazio"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_elmo")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_elmo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    elmo = session.query(Elmo).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    # Desequipar
    if escolha == "desequipar_elmo":
        texto = mover_equipamento_para_inventario(jogador, elmo, equipado, "elmo")
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

    novo_item = getattr(elmo, slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(jogador, elmo, equipado, "elmo", slot_nome)

    session.commit()
    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
