from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from firebase_admin import db
from utils.ler_texto import ler_texto
from utils.extrator_buffs import extrair_buffs

async def mostrar_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def seguro_int(v):
        try:
            return int(v)
        except:
            return 0

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    chat_id = str(query.from_user.id)

    perfil_ref = db.reference(f"{chat_id}/Perfil")
    atributos_ref = db.reference(f"{chat_id}/Atributos")
    equipado_ref = db.reference(f"{chat_id}/Equipado")

    perfil = perfil_ref.get()
    atributos_base = atributos_ref.get()
    equipado = equipado_ref.get()

    if not perfil or not atributos_base or not equipado:
        await query.message.reply_text("❌ Não foi possível carregar seus dados.")
        return

    # Inicializa os atributos com os valores salvos no banco
    atributos = {chave.lower(): seguro_int(atributos_base.get(chave, 0)) for chave in atributos_base}


    # Lista de itens equipados (podem ser vazios)
    equipamentos = [
        equipado.get("Arma"),
        equipado.get("Elmo"),
        equipado.get("Armadura"),
        equipado.get("Calca"),
        equipado.get("Bota"),
        equipado.get("Amuleto")
    ]

    # Aplica buffs de cada item
    for item in equipamentos:
        if item:
            buffs = extrair_buffs(item)
            for chave in atributos:
                atributos[chave] += buffs.get(chave, 0)


    # Define o atributo de ataque com base na classe
    atributo_ataque_por_classe = {
        "guardião": "forca",
        "bárbaro": "furia",
        "lanceiro": "dominio",
        "caçador": "precisao",
        "arcano": "magia",
        "espadachim": "destreza"
    }

    classe = perfil.get("Classe").lower()
    atributo_chave = atributo_ataque_por_classe.get(classe)
    atributo_ataque = atributos.get(atributo_chave) if atributo_chave else 0

    vida = atributos.get("resistencia") * 3
    agilidade = int(atributos.get("velocidade") * 1.5)
    critico = int(atributos.get("bencao") * 1.5)
    dano = atributo_ataque

    texto = ler_texto("../texts/midtheim/personagem/status.txt").format(
        vida=vida,
        agilidade=agilidade,
        critico=critico,
        dano=dano,
        forca=atributos.get("forca"),
        magia=atributos.get("magia"),
        precisao=atributos.get("precisao"),
        resistencia=atributos.get("resistencia"),
        velocidade=atributos.get("velocidade"),
        destreza=atributos.get("destreza"),
        furia=atributos.get("furia"),
        bencao=atributos.get("bencao"),
        dominio=atributos.get("dominio")
    )

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Voltar", callback_data="personagem")],
        [InlineKeyboardButton("Menu de Midtheim", callback_data="menu_midtheim")]
    ])

    await query.message.reply_text(text=texto, reply_markup=teclado, parse_mode="HTML")
