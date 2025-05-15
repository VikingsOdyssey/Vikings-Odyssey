from utils.extrator_buffs import extrair_buffs
from utils.equipamento_durabilidade import extrair_durabilidade, item_possui_durabilidade

def seguro_int(v):
    try:
        return int(v)
    except:
        return 0

def calcular_atributos(jogador_dict: dict, equipado_dict: dict) -> tuple[dict, int, int, int, int]:
    atributos_base = jogador_dict.get("Atributos", {})
    equipado = jogador_dict.get("Equipado", {}) if not equipado_dict else equipado_dict

    buffs = {}
    for tipo, item in equipado.items():
        if item and item_possui_durabilidade(item):
            atual, _ = extrair_durabilidade(item)
            if atual > 0:
                buffs_item = extrair_buffs(item)
                for atr, val in buffs_item.items():
                    buffs[atr] = buffs.get(atr, 0) + val

    atributos_finais = {}
    for atributo, valor in atributos_base.items():
        if atributo.lower() == "atributo_ataque":
            continue
        val_final = seguro_int(valor) + seguro_int(buffs.get(atributo.lower(), 0))
        atributos_finais[atributo.lower()] = val_final

    vida = atributos_finais.get("resistencia") * 3
    agilidade = int(atributos_finais.get("velocidade") * 1.5)
    critico = atributos_finais.get("bencao") * 1.5
    atributo_ataque = atributos_base.get("atributo_ataque", "forca").lower()
    dano = atributos_finais.get(atributo_ataque)
    return atributos_finais, vida, agilidade, critico, dano

def calcular_dano_com_reducao(base_dano, critado, atributo_ataque, atributos_defensor, classe_atacante, classe_defensor):
    dano = base_dano * 1.5 if critado else base_dano
    resistencia = atributos_defensor.get(f"/{chat_id}/Atributos/atributo_ataque")
    resistencia = atributos_defensor.get("resistencia", 0)
    dano_final = max(0, int(dano - (resistencia / 2)))
    return dano_final