from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

# -------------------------------------------------------------------
# Mostra a lista de calcas disponíveis
async def mostrar_calcas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    ref_calcas = db.reference(f"{chat_id}/Equipamentos/Calcas")
    calcas = ref_calcas.get() or {}

    texto = ler_texto("../texts/midtheim/personagem/equipamentos/calcas.txt").format(
        **{f"calca_{i}": calcas.get(f"Item{i}", "Vazio") or "Vazio" for i in range(1, 11)}
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"Calca{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_calca")]])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")

# -------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_calca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)

    ref_base = db.reference(f"{chat_id}")
    ref_jogador = ref_base.child("Perfil")
    ref_calcas = ref_base.child("Equipamentos/Calcas")
    ref_equipado = ref_base.child("Equipado")

    calcas = ref_calcas.get() or {}
    equipado = ref_equipado.get() or {}

   # Desequipar
    if escolha == "desequipar_calca":
        texto = mover_equipamento_para_inventario(ref_calcas, ref_equipado, "Calca")
        teclado = teclado_pos_equipar()
        await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return


    # Equipar novo item
    try:
        slot_index = int(escolha[5:])
        slot_nome = f"Item{slot_index}"
    except ValueError:
        await query.message.reply_text("❌ Seleção inválida.", parse_mode="HTML")
        return

    novo_item = calcas.get(slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(ref_calcas, ref_equipado, "Calca", slot_nome)

    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
