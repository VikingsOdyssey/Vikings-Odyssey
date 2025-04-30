from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Armadura, Equipado
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

#-------------------------------------------------------------------
# Mostra a lista de armaduras disponíveis
async def mostrar_armaduras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    armadura = session.query(Armadura).filter_by(chat_id=chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/armaduras.txt").format(
        armadura_1=armadura.Item1 or "Vazio",
        armadura_2=armadura.Item2 or "Vazio",
        armadura_3=armadura.Item3 or "Vazio",
        armadura_4=armadura.Item4 or "Vazio",
        armadura_5=armadura.Item5 or "Vazio",
        armadura_6=armadura.Item6 or "Vazio",
        armadura_7=armadura.Item7 or "Vazio",
        armadura_8=armadura.Item8 or "Vazio",
        armadura_9=armadura.Item9 or "Vazio",
        armadura_10=armadura.Item10 or "Vazio"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_armadura")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_armadura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    armadura = session.query(Armadura).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    # Desequipar
    if escolha == "desequipar_armadura":
        texto = mover_equipamento_para_inventario(jogador, armadura, equipado, "armadura")
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

    novo_item = getattr(armadura, slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(jogador, armadura, equipado, "armadura", slot_nome)

    session.commit()
    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
