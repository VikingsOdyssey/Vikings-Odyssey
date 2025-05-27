# reset_players_data.py
import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db

load_dotenv()

# Inicializa Firebase
firebase_cred = credentials.Certificate("firebase_config.json")
initialize_app(firebase_cred, {'databaseURL': os.getenv("FIREBASE_DB_URL")})

print(
    "\n🔧 Alterações em larga escala:\n"
    "1. Adicionar ou alterar valor de um campo\n"
    "2. Excluir campo\n"
)
acao = input("Digite o número da opção desejada: ")

# Referência raiz
root_ref = db.reference("/")
todos_os_players = root_ref.get()

if not todos_os_players:
    print("⚠️ Nenhum player encontrado no banco.")
    exit()
print(f"\n🎯 {len(todos_os_players)} jogadores serão afetados.")

match acao:
    case "1" | "2":
        caminho = input("Caminho do campo (ex: Inventario/Moedas): ")
        valor_raw = input("Valor a ser atribuído (int, str, bool): ")
        try:
            if valor_raw.isdigit():
                valor = int(valor_raw)
            elif valor_raw.lower() in ["true", "false"]:
                valor = valor_raw.lower() == "true"
            else:
                valor = valor_raw
        except:
            print("❌ Valor inválido.")
            exit()
        for chat_id in todos_os_players:
            db.reference(f"{chat_id}/{caminho}").set(valor)
            print(f"✔ {chat_id}: {caminho} = {valor}")
        print("\n✅ Atualização concluída.")

    case "2":
        caminho = input("Caminho do campo a ser excluído (ex: Inventario/Moedas): ")
        for chat_id in todos_os_players:
            db.reference(f"{chat_id}/{caminho}").delete()
            print(f"🗑 {chat_id}: {caminho} excluído.")
        print("\n✅ Campos removidos com sucesso.")

    case _:
        print("❌ Opção inválida ou ainda não implementada.")
