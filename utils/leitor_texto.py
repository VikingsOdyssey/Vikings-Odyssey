def ler_texto(caminho: str) -> str:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()