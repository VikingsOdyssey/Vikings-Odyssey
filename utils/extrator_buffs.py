# utils/extrator_buffs.py

from libs.emoji_atributos import EMOJIS_ATRIBUTOS  # type: ignore
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
