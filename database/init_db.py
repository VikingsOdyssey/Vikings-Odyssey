from .config import Base, engine
from .models import Jogador

def init_db():
    Base.metadata.create_all(bind=engine)