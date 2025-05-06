import firebase_admin
from firebase_admin import credentials, db
import os

# Caminho do seu JSON de credenciais
cred_path = os.path.join(os.getcwd(), 'firebase_config.json')

# Inicializa o app do Firebase apenas uma vez
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vikingsodyssey-fa886-default-rtdb.firebaseio.com/'  # substitua pelo seu URL real do DB
    })

def get_db_ref(path="/"):
    """Retorna uma referência do caminho no Firebase."""
    return db.reference(path)
