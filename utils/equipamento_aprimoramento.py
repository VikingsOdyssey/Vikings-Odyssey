import re
import random
from libs.emoji_atributos import EMOJIS_ATRIBUTOS
from firebase_admin import db

QUALIDADES = ["🔵", "🟠", "🔴", "🟢"]

def extrair_equipamento_formatado(equipamento: str):
    dur = re.search(r"\[(\d+)/\d+]", equipamento)
    qual = re.search(r"\[(🔵|🟠|🔴|🟢)]", equipamento)
    nome = re.search(r"\] (.+?) \[", equipamento)
    nivel = re.search(r"\[(\d+)]", equipamento)
    buffs = re.findall(r"(\S)\+(\d+)", equipamento)

    return {
        "durabilidade": int(dur.group(1)),
        "qualidade": qual.group(1),
        "nome": nome.group(1),
        "nivel": int(nivel.group(1)),
        "buffs": buffs
    }

def formatar_equipamento(dur, qualidade, nome, nivel, buffs):
    buffs_formatados = ", ".join(f"{emoji}+{val}" for emoji, val in buffs)
    return f"[{dur}/20] [{qualidade}] {nome} [{nivel}] [{buffs_formatados}]"

def tentar_aprimorar_nivel(chat_id, tipo):
    ref = db.reference(f"{chat_id}/Equipado/{tipo}")
    equipamento = ref.get()
    if not equipamento: return "❌ Nenhum equipamento equipado."

    inv_ref = db.reference(f"{chat_id}/Inventario")
    joias = inv_ref.child("Joia_Aperfeicoamento").get()
    if joias < 1: return "❌ Você precisa de uma Joia de Aprimoramento."

    data = extrair_equipamento_formatado(equipamento)
    data["nivel"] += 1
    data["buffs"] = [(emoji, str(int(val) + 1)) for emoji, val in data["buffs"]]

    novo = formatar_equipamento(data["durabilidade"], data["qualidade"], data["nome"], data["nivel"], data["buffs"])
    ref.set(novo)
    inv_ref.child("Joia_Aperfeicoamento").set(joias - 1)

    return f"✅ Aprimoramento concluído!\nNovo equipamento:\n{novo}"

def tentar_aprimorar_qualidade(chat_id, tipo):
    ref = db.reference(f"{chat_id}/Equipado/{tipo}")
    equipamento = ref.get()
    if not equipamento: return "❌ Nenhum equipamento equipado."

    inv_ref = db.reference(f"{chat_id}/Inventario")
    joias = inv_ref.child("Joia_Aperfeicoamento").get()
    if joias < 2: return "❌ Você precisa de 2 Joias de Aprimoramento."

    data = extrair_equipamento_formatado(equipamento)
    nivel = data["nivel"]
    qualidade = data["qualidade"]

    match qualidade:
        case "🔵" if nivel < 4: return "❌ Nível 4 necessário para aprimorar para 🟠"
        case "🟠" if nivel < 6: return "❌ Nível 6 necessário para aprimorar para 🔴"
        case "🔴" if nivel < 8: return "❌ Nível 8 necessário para aprimorar para 🟢"
        case "🟢": return "❌ Qualidade máxima atingida."

    nova_qualidade = QUALIDADES[QUALIDADES.index(qualidade) + 1]
    novo_atributo = random.choice(list(EMOJIS_ATRIBUTOS.values()))
    novos_buffs = [(emoji, "1") for emoji, _ in data["buffs"]] + [(novo_atributo, "1")]

    novo = formatar_equipamento(data["durabilidade"], nova_qualidade, data["nome"], 1, novos_buffs)
    ref.set(novo)
    inv_ref.child("Joia_Aperfeicoamento").set(joias - 2)

    return f"✨ Qualidade aprimorada para {nova_qualidade}!\nNovo equipamento:\n{novo}"
