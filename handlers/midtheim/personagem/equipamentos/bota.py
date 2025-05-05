from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.config import SessionLocal
from database.models import Jogador, Bota, Equipado
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

#-------------------------------------------------------------------
# Mostra a lista de botas disponíveis
async def mostrar_botas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    chat_id = str(query.message.chat_id)
    session = SessionLocal()
    bota = session.query(Bota).filter_by(chat_id=chat_id).first()
    texto = ler_texto("../texts/midtheim/personagem/equipamentos/botas.txt").format(
        bota_1=bota.Item1 or "Vazio",
        bota_2=bota.Item2 or "Vazio",
        bota_3=bota.Item3 or "Vazio",
        bota_4=bota.Item4 or "Vazio",
        bota_5=bota.Item5 or "Vazio",
        bota_6=bota.Item6 or "Vazio",
        bota_7=bota.Item7 or "Vazio",
        bota_8=bota.Item8 or "Vazio",
        bota_9=bota.Item9 or "Vazio",
        bota_10=bota.Item10 or "Vazio"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"I{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_bota")]])
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()

#-------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_bota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data

    chat_id = str(query.message.chat_id)
    session = SessionLocal()

    jogador = session.query(Jogador).filter_by(chat_id=chat_id).first()
    bota = session.query(Bota).filter_by(chat_id=chat_id).first()
    equipado = session.query(Equipado).filter_by(chat_id=chat_id).first()

    # Desequipar
    if escolha == "desequipar_bota":
        texto = mover_equipamento_para_inventario(jogador, bota, equipado, "bota")
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

    novo_item = getattr(bota, slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(jogador, bota, equipado, "bota", slot_nome)

    session.commit()
    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
    session.close()
