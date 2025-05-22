MOBS = {
    "Solvindr": {
        "Espadachim": {
            "nome": "Alrek Vindsverd", "classe": "Espadachim", "atributo_ataque": "destreza", "atributos": {
                "destreza": 5, "dominio": 0, "precisao": 0, "magia": 0,
                "furia": 3, "forca": 0, "resistencia": 2, "bencao": 2, "velocidade": 3
            }
        },
        "Lanceiro": {
            "nome": "Gunnar Spydstorm", "classe": "Lanceiro", "atributo_ataque": "dominio", "atributos": {
                "destreza": 3, "dominio": 5, "precisao": 0, "magia": 0,
                "furia": 0, "forca": 0, "resistencia": 2, "bencao": 2, "velocidade": 3
            }
        },
        "Caçador": {
            "nome": "Yrsa Skyggepil", "classe": "Caçador", "atributo_ataque": "precisao", "atributos": {
                "destreza": 0, "dominio": 3, "precisao": 5, "magia": 0,
                "furia": 0, "forca": 0, "resistencia": 2, "bencao": 2, "velocidade": 3
            }
        },
        "Arcano": {
            "nome": "Hervor Trolldom", "classe": "Arcano", "atributo_ataque": "magia", "atributos": {
                "destreza": 0, "dominio": 0, "precisao": 0, "magia": 5,
                "furia": 0, "forca": 3, "resistencia": 2, "bencao": 2, "velocidade": 3
            }
        },
        "Bárbaro": {
            "nome": "Bjorn Ulvhammer", "classe": "Bárbaro", "atributo_ataque": "furia", "atributos": {
                "destreza": 0, "dominio": 0, "precisao": 0, "magia": 3,
                "furia": 5, "forca": 0, "resistencia": 3, "bencao": 2, "velocidade": 2
            }
        },
        "Guardião": {
            "nome": "Sigurd Jernskjegg", "classe": "Guardião", "atributo_ataque": "forca", "atributos": {
                "destreza": 0, "dominio": 0, "precisao": 3, "magia": 0,
                "furia": 0, "forca": 5, "resistencia": 3, "bencao": 2, "velocidade": 2
            }
        },
    },
    # Repita a mesma estrutura para Modrheim, Yggdreth, Aska, Skjovik, Hrimgard
    # com os nomes nórdicos já definidos e as distribuições equivalentes acima
    # substituindo apenas os campos "nome"
}

# Você pode duplicar o bloco da região "Solvindr" e ajustar apenas os nomes dos mobs para as demais regiões,
# pois os atributos são os mesmos por classe em todas as regiões (nível 1)
# Conforme o nível dos mobs evoluir futuramente, os atributos podem ser escalados proporcionalmente.
