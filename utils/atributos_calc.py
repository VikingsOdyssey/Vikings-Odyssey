from libs.emoji_atributos import EMOJIS_ATRIBUTOS # type: ignore
import re

EMOJI_PARA_ATRIBUTO = {v: k for k, v in EMOJIS_ATRIBUTOS.items()}
REGEX_BUFFS = r"(" + "|".join(map(re.escape, EMOJI_PARA_ATRIBUTO.keys())) + r")\+(\d+)"

def extrair_buffs(nome_item):
    atributos = {chave: 0 for chave in EMOJIS_ATRIBUTOS}
    if not nome_item:
        return atributos
    matches = re.findall(REGEX_BUFFS, nome_item)
    for emoji, valor in matches:
        chave = EMOJI_PARA_ATRIBUTO.get(emoji.strip())
        if chave:
            atributos[chave] += int(valor)
    return atributos

def calcular_atributos(jogador, equipado):
    atributos = {
        "forca": jogador.forca,
        "magia": jogador.magia,
        "precisao": jogador.precisao,
        "resistencia": jogador.resistencia,
        "velocidade": jogador.velocidade,
        "destreza": jogador.destreza,
        "furia": jogador.furia,
        "bencao": jogador.bencao,
        "dominio": jogador.dominio
    }

    equipamentos = [equipado.arma, equipado.elmo, equipado.armadura, equipado.calca, equipado.bota]
    if equipado.amuleto:
        equipamentos.append(equipado.amuleto)

    for item in equipamentos:
        buffs = extrair_buffs(item)
        for chave in atributos:
            atributos[chave] += buffs[chave]

    vida = atributos["resistencia"] * 3
    agilidade = int(atributos["velocidade"] * 1.5)
    critico = int(atributos["bencao"] * 1.5)
    dano = atributos.get(jogador.atributo_ataque, 0)

    return atributos, vida, agilidade, critico, dano

def calcular_dano_com_reducao(dano_base, critado, atributo_ataque, atributos_defensor):
    """Reduz o dano baseado nos pontos que o defensor tem no atributo de ataque do atacante."""
    dano_final = dano_base * (2 if critado else 1)
    resistencia_ao_ataque = atributos_defensor.get(atributo_ataque, 0)
    dano_reduzido = max(0, dano_final - resistencia_ao_ataque)
    return int(dano_reduzido)