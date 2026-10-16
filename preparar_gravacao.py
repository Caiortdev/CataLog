"""
Prepara o projeto para gravar a demonstração.

O problema que este script resolve: quando um produto é cadastrado, o sistema
aprende e guarda a resposta. Da próxima vez ele responde do cache, sem
consultar o modelo de linguagem.

Isso é ótimo em uso normal e ruim na gravação: se você ensaiar com as frases da
demonstração, na hora de gravar a IA não será acionada e a parte mais
interessante do vídeo não acontece.

Este script apaga do aprendizado apenas as três frases da demonstração, para
elas voltarem a ser novidade. O resto do que foi aprendido continua lá.

Rodar antes de cada gravação:

    python3 preparar_gravacao.py
"""

import json
import os
import sys

from catalogo.professor import CACHE
from catalogo.texto import normalizar

# As três frases do roteiro de gravação, exatamente como serão digitadas.
FRASES_DA_DEMONSTRACAO = [
    "Tênis azul para corrida em asfalto",
    "Churrasqueira eletrica portatil com tampa de vidro",
    "Mesa de jantar em madeira macica para seis lugares",
]


def main():
    if not os.path.exists(CACHE):
        print("Nenhum aprendizado encontrado. Rode antes:")
        print("  python3 povoar_aprendizado.py")
        return 1

    with open(CACHE, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    frases = dados.get("frases", {})
    removidas = []

    for texto in FRASES_DA_DEMONSTRACAO:
        chave = normalizar(texto).strip()
        if chave in frases:
            del frases[chave]
            removidas.append(texto)

    # As palavras generalizadas também precisam sair, senão elas respondem no
    # lugar do modelo. "churrasqueira" aprendida uma vez vale para qualquer
    # churrasqueira, e a demonstração perderia a graça.
    palavras = dados.get("palavras", {})
    palavras_removidas = []
    for texto in FRASES_DA_DEMONSTRACAO:
        primeira = normalizar(texto).strip().split()
        if primeira and primeira[0] in palavras:
            del palavras[primeira[0]]
            palavras_removidas.append(primeira[0])

    with open(CACHE, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
        arquivo.write("\n")

    print("PRONTO PARA GRAVAR\n")
    if removidas:
        print("Frases que voltaram a ser novidade:")
        for texto in removidas:
            print("  - %s" % texto)
    else:
        print("As três frases já estavam novas. Nada a fazer.")

    if palavras_removidas:
        print("\nPalavras removidas do atalho: %s" % ", ".join(palavras_removidas))

    print("\nAinda no aprendizado: %d produtos, %d palavras."
          % (len(frases), len(palavras)))
    print("\nNa gravação, a IA será consultada nos três cadastros.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
