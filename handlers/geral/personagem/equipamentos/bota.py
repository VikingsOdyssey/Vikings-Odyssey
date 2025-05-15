from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.equipamento_utils import mover_equipamento_para_inventario, equipar_item, teclado_pos_equipar
from utils.ler_texto import ler_texto

# -------------------------------------------------------------------
# Mostra a lista de botas disponíveis
async def mostrar_botas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.message.chat_id)
    ref_botas = db.reference(f"{chat_id}/Equipamentos/Botas")
    botas = ref_botas.get() or {}

    texto = ler_texto("../texts/midtheim/personagem/equipamentos/botas.txt").format(
        **{f"bota_{i}": botas.get(f"Item{i}", "Vazio") or "Vazio" for i in range(1, 11)}
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Item {i:02}", callback_data=f"Bota{i}")] for i in range(1, 11)
    ] + [[InlineKeyboardButton("Desequipar", callback_data="desequipar_bota")]])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")

# -------------------------------------------------------------------
# Trata a escolha de item OU retorno ao menu
async def selecionar_bota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data
    chat_id = str(query.message.chat_id)

    ref_base = db.reference(f"{chat_id}")
    ref_jogador = ref_base.child("Perfil")
    ref_botas = ref_base.child("Equipamentos/Botas")
    ref_equipado = ref_base.child("Equipado")

    botas = ref_botas.get() or {}
    equipado = ref_equipado.get() or {}

   # Desequipar
    if escolha == "desequipar_bota":
        texto = mover_equipamento_para_inventario(ref_botas, ref_equipado, "Bota")
        teclado = teclado_pos_equipar()
        await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
        return


    # Equipar novo item
    try:
        slot_index = int(escolha[4:])
        slot_nome = f"Item{slot_index}"
    except ValueError:
        await query.message.reply_text("❌ Seleção inválida.", parse_mode="HTML")
        return

    novo_item = botas.get(slot_nome)
    if not novo_item or novo_item.strip() == "":
        texto = "Este slot está vazio!"
    else:
        texto = equipar_item(ref_botas, ref_equipado, "Bota", slot_nome)

    teclado = teclado_pos_equipar()
    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
