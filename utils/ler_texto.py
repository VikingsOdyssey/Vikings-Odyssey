import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

def ler_texto(caminho_relativo):
    base_dir = os.path.dirname(__file__)
    caminho_absoluto = os.path.join(base_dir, caminho_relativo)
    with open(caminho_absoluto, "r", encoding="utf-8") as f:
        return f.read()