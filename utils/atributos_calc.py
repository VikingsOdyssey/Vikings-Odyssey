from utils.equipamento_durabilidade import extrair_buffs_com_durabilidade

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
        buffs = extrair_buffs_com_durabilidade(item)
        for chave in atributos:
            atributos[chave] += buffs[chave]

    vida = atributos["resistencia"] * 3
    agilidade = int(atributos["velocidade"] * 1.5)
    critico = int(atributos["bencao"] * 1.5)
    dano = atributos.get(jogador.atributo_ataque, 0)

    return atributos, vida, agilidade, critico, dano

def calcular_dano_com_reducao(dano_base, critado, atributo_ataque, atributos_defensor):
    dano_final = dano_base * (2 if critado else 1)
    reducao = atributos_defensor.get(atributo_ataque, 0)
    return max(0, int(dano_final - reducao))
