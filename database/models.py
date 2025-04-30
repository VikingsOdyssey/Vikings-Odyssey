from sqlalchemy import Column, Integer, String, JSON
from database.config import Base # type: ignore

class Jogador(Base):
    __tablename__ = "jogadores"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    #Ficha
    nome = Column(String, default="A definir")
    classe = Column(String, default="A definir")
    nivel = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    nivel_foja = Column(Integer, default=1)
    xp_forja =Column(Integer, default=0)
    local_atual = Column(String, default="Midtheim ")
    rank = Column(Integer, default=0)
    # Atributos
    destreza = Column(Integer, default=0)
    dominio = Column(Integer, default=0)
    precisao = Column(Integer, default=0)
    magia = Column(Integer, default=0)
    furia = Column(Integer, default=0)
    forca = Column(Integer, default=0)
    resistencia = Column(Integer, default=0)
    bencao = Column(Integer, default=0)
    velocidade = Column(Integer, default=0)
    atributo_ataque = Column(String, default="")

class Inventario(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    # Inventário de recursos
    moedas = Column(Integer, default=0)
    diamantes = Column(Integer, default=0)
    madeira = Column(Integer, default=0)
    aco = Column(Integer, default=0)
    pedra = Column(Integer, default=0)
    linha = Column(Integer, default=0)
    couro = Column(Integer, default=0)
    joia_criacao = Column(Integer, default=0)
    joia_aperfeicoamento = Column(Integer, default=0)
    # Entradas diárias
    cacada = Column(Integer, default=0)
    caverna = Column(Integer, default=0)
    dungeon = Column(Integer, default=0)
    arena = Column(Integer, default=0)
    
class Arma(Base):
    __tablename__ = "arma"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Elmo(Base):
    __tablename__ = "elmo"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Armadura(Base):
    __tablename__ = "armadura"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Calca(Base):
    __tablename__ = "calca"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Bota(Base):
    __tablename__ = "bota"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Amuleto(Base):
    __tablename__ = "amuleto"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    Item1 = Column(String, default="")
    Item2 = Column(String, default="")
    Item3 = Column(String, default="")
    Item4 = Column(String, default="")
    Item5 = Column(String, default="")
    Item6 = Column(String, default="")
    Item7 = Column(String, default="")
    Item8 = Column(String, default="")
    Item9 = Column(String, default="")
    Item10 = Column(String, default="")

class Equipado(Base):
    __tablename__ = "equipado"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    arma = Column(String, default="")
    elmo = Column(String, default="")
    armadura = Column(String, default="")
    calca = Column(String, default="")
    bota = Column(String, default="")
    amuleto = Column(String, default="")