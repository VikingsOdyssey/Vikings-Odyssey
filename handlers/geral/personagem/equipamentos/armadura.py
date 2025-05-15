from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

# -------------------------------------------------------------------
# Mostra a lista de armaduras disponíveis
async def mostrar_armaduras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    ref_armaduras = db.reference(f"{chat_id}/Equipamentos/Armaduras")
    armaduras = ref_armaduras.get() or {}

    texto = ler_texto("../texts/midtheim/personagem/equipamentos/armaduras.txt").format(
        **{f"armadura_{i}": armaduras.get(f"Item{i}", "Vazio") or "Vazio" for i in range(1, 11)}
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"Armadura{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_armadura")]])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")

# -------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_armadura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)

    ref_base = db.reference(f"{chat_id}")
    ref_jogador = ref_base.child("Perfil")
    ref_armaduras = ref_base.child("Equipamentos/Armaduras")
    ref_equipado = ref_base.child("Equipado")

    armaduras = ref_armaduras.get() or {}
    equipado = ref_equipado.get() or {}

   # Desequipar
    if escolha == "desequipar_armadura":
        texto = mover_equipamento_para_inventario(ref_armaduras, ref_equipado, "Armadura")
        teclado = teclado_pos_equipar()
        await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return


    # Equipar novo item
    try:
        slot_index = int(escolha[8:])
        slot_nome = f"Item{slot_index}"
    except ValueError:
        await query.message.reply_text("❌ Seleção inválida.", parse_mode="HTML")
        return

    novo_item = armaduras.get(slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(ref_armaduras, ref_equipado, "Armadura", slot_nome)

    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
