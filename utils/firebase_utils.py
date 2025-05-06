from firebase_admin import db

def criar_dados_iniciais(chat_id):
    base_ref = db.reference(f"{chat_id}")
    base_ref.set({
        "Perfil": {
            "Nome": "A definir",
            "Classe": "A definir",
            "Nivel": 1,
            "Xp": 0,
            "Nivel_Forja": 1,
            "Xp_Forja": 0,
            "Local_Atual": "Midtheim",
            "Rank": 0
        },
        "Atributos": {
            "Destreza": 0,
            "Dominio": 0,
            "Precisao": 0,
            "Magia": 0,
            "Furia": 0,
            "Forca": 0,
            "Resistencia": 0,
            "Bencao": 0,
            "Velocidade": 0,
            "Atributo_ataque": ""
        },
        "Inventario": {
            "Moedas": 0,
            "Diamantes": 0,
            "Madeira": 0,
            "Aco": 0,
            "Pedra": 0,
            "Linha": 0,
            "Couro": 0,
            "Joia_Criacao": 0,
            "Joia_Aperfeicoamento": 0
        },
        "Entradas": {
            "Cacada": 0,
            "Caverna": 0,
            "Dungeon": 0,
            "Arena": 0
        },
        "Equipamentos": {
            "Armas": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            },
            "Elmos": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            },
            "Armaduras": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            },
            "Calcas": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            },
            "Botas": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            },
            "Amuletos": {
                "Item1": "",
                "Item2": "",
                "Item3": "",
                "Item4": "",
                "Item5": "",
                "Item6": "",
                "Item7": "",
                "Item8": "",
                "Item9": "",
                "Item10": ""
            }
        },
        "Equipado": {
            "Arma": "",
            "Elmo": "",
            "Armadura": "",
            "Calca": "",
            "Bota": "",
            "Amuleto": ""
        }
    })
