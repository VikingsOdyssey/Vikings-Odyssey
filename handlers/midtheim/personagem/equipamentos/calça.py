from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Calca, Equipado
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

#-------------------------------------------------------------------
# Mostra a lista de calcas disponíveis
async def mostrar_calcas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    calca = session.query(Calca).filter_by(chat_id=chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/calças.txt").format(
        calca_1=calca.Item1 or "Vazio",
        calca_2=calca.Item2 or "Vazio",
        calca_3=calca.Item3 or "Vazio",
        calca_4=calca.Item4 or "Vazio",
        calca_5=calca.Item5 or "Vazio",
        calca_6=calca.Item6 or "Vazio",
        calca_7=calca.Item7 or "Vazio",
        calca_8=calca.Item8 or "Vazio",
        calca_9=calca.Item9 or "Vazio",
        calca_10=calca.Item10 or "Vazio"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_calca")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_calca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    calca = session.query(Calca).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    # Desequipar
    if escolha == "desequipar_calca":
        texto = mover_equipamento_para_inventario(jogador, calca, equipado, "calca")
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

    novo_item = getattr(calca, slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(jogador, calca, equipado, "calca", slot_nome)

    session.commit()
    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
