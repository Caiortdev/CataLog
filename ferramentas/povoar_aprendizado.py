"""
Povoa o arquivo de aprendizado com produtos de categorias variadas.

Este script existe para que `dados/aprendido.json` seja auditável. Sem ele, o
arquivo seria uma caixa-preta: alguém abriria, veria dezenas de linhas e não
teria como saber de onde vieram nem como refazê-las. Com ele, a lista está à
vista e o arquivo pode ser reconstruído do zero a qualquer momento.

Rodar com:  python3 ferramentas/povoar_aprendizado.py

Precisa de Mac com Apple Intelligence ligado, porque é aqui que o modelo é
consultado. Depois disso o arquivo gerado funciona em qualquer máquina — essa é
justamente a ideia: o conhecimento fica no arquivo, não no modelo.

A lista abaixo foi escolhida com um critério: são produtos comuns em
e-commerce cujas palavras NÃO estão no vocabulário. Produtos que o vocabulário
já reconhece não aparecem aqui porque nunca chegariam ao modelo — o professor
só é consultado quando o produto ficaria sem nenhuma tag.
"""

import os
import sys

# Permite rodar este script direto, de qualquer lugar:
#     python3 ferramentas/benchmark.py
#
# Sem estas linhas o Python procuraria o pacote "catalogo" dentro de
# ferramentas/, porque é a pasta do script que entra no caminho de busca — não
# a pasta de onde o comando foi chamado.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalogo.professor import Professor
from catalogo.tagger import GeradorDeTags

PRODUTOS = [
    # Cozinha
    "Cafeteira eletrica italiana",
    "Panela de pressao de inox",
    "Chaleira eletrica com desligamento automatico",
    "Liquidificador de alta potencia",
    "Jogo de facas de cozinha",

    # Móveis e decoração
    "Cadeira de escritorio giratoria com rodinhas",
    "Luminaria de mesa articulada",
    "Colchao de solteiro de espuma",
    "Tapete de sala antiderrapante",
    "Cortina blackout para quarto",

    # Eletrodomésticos e eletrônicos fora do vocabulário
    "Ventilador de teto silencioso",
    "Aspirador de po portatil",
    "Micro-ondas com grill",

    # Ferramentas
    "Furadeira de impacto com maleta",
    "Jogo de chaves de fenda",
    "Trena a laser digital",

    # Papelaria
    "Caderno universitario espiral",
    "Caneta esferografica azul ponta fina",
    "Mochila escolar com rodinhas",

    # Pet
    "Racao para gatos adultos",
    "Coleira ajustavel para cachorro",
    "Arranhador para gatos",

    # Beleza e saúde
    "Shampoo anticaspa",
    "Escova de dentes eletrica recarregavel",
    "Secador de cabelo profissional",

    # Automotivo
    "Pneu aro 15 para carro de passeio",
    "Capa de volante em couro sintetico",

    # Brinquedos
    "Quebra-cabeca de mil pecas",
    "Carrinho de controle remoto",

    # Livros e alimentos
    "Livro de ficcao cientifica capa dura",
    "Cafe em graos torrado artesanal",
    "Barra de cereal integral",

    # Guarda-chuva: o caso que motivou tudo isto. O vocabulário não conhece a
    # palavra, então sem o modelo o produto fica invisível na busca.
    "Guarda-chuva dobravel automatico",

    # Guarda-roupa está aqui de propósito, ao lado do guarda-chuva. Enquanto o
    # hífen virava espaço, os dois começavam pela palavra "guarda" e colidiam:
    # um é acessório, o outro é móvel. Hoje viram "guardachuva" e "guardaroupa",
    # e este par serve de prova de que a correção funciona.
    "Guarda-roupa de 6 portas com espelho",

    # Produtos vindos das demonstrações. Entraram no arquivo durante o uso
    # normal do programa; estão listados aqui para que o arquivo possa ser
    # reconstruído por inteiro a partir deste script.
    "Frigideira antiaderente de ceramica com cabo de madeira",
    "Esteira ergometrica dobravel com inclinacao automatica",
    "Umidificador de ar ultrassonico para quarto de bebe",
]


# Correções humanas às respostas do modelo.
#
# Esta tabela é o ponto mais importante do script, e a razão pela qual este
# desenho é melhor que treinar o modelo.
#
# Rodando a lista acima, o modelo errou de duas maneiras. Houve erro simples —
# classificou uma trena a laser como artigo de esporte e um colchão como
# acessório. E houve algo mais sutil: cafeteira e chaleira foram para
# "eletronico" enquanto micro-ondas foi para "cozinha". São três
# eletrodomésticos de cozinha em duas categorias diferentes, o que significa
# que buscar "cozinha" não acharia dois deles.
#
# Esse segundo caso é a mesma inconsistência entre produtos que já tínhamos
# medido com as tags em texto livre (documento 6). O conjunto fechado de
# categorias impede o modelo de inventar a palavra "calcados", mas não o impede
# de achar que produtos parecidos pertencem a categorias diferentes.
#
# A diferença é que agora dá para consertar. O que o modelo ensinou é um
# arquivo JSON de poucas dezenas de linhas, que uma pessoa lê em um minuto e
# corrige com um editor de texto. Se o conhecimento estivesse dentro dos pesos
# de um modelo ajustado, não haveria o que revisar nem como corrigir um caso
# específico — só retreinar tudo e esperar que melhorasse.
#
# Decisões tomadas aqui, cada uma com um motivo:
CORRECOES = {
    # Erros claros.
    "trena a laser digital": "ferramenta",
    "colchao de solteiro de espuma": "movel",

    # Consistência: se micro-ondas é cozinha, cafeteira e chaleira também são.
    # O critério adotado foi "onde o produto é usado", e não "do que ele é
    # feito" — quem procura uma cafeteira está pensando em cozinha, não em
    # eletrônica.
    "cafeteira eletrica italiana": "cozinha",
    "chaleira eletrica com desligamento automatico": "cozinha",

    # Pelo mesmo critério de uso.
    "carrinho de controle remoto": "brinquedo",
    "secador de cabelo profissional": "beleza",

    # Ração é alimento, mas quem busca está procurando coisa de animal. A tag
    # mais útil para encontrar o produto é "pet".
    "racao para gatos adultos": "pet",
}


def main():
    # Cinco amostras por produto. Custa cinco vezes mais tempo, e por isso
    # só é feito aqui: montar a base é uma vez na vida, usar é todo dia.
    # Em troca, os produtos que o modelo classificou de forma hesitante
    # ficam marcados para alguém olhar.
    professor = Professor(amostras=5)
    vocabulario = GeradorDeTags()

    print(f"{len(PRODUTOS)} produtos na lista. "
          f"{professor.aprendidos} já estavam no arquivo.\n")

    ignorados = 0
    for texto in PRODUTOS:
        # Reproduz a mesma condição do gerador: se o vocabulário já resolve,
        # o modelo não é consultado. Perguntar aqui o que não seria perguntado
        # em uso real encheria o arquivo de entradas que nunca serão lidas.
        if vocabulario.gerar(texto, ""):
            ignorados += 1
            continue

        # A generalização por palavra é desligada aqui de propósito.
        #
        # Montar a base não é a mesma coisa que usá-la. No uso normal, o atalho
        # responder sem consultar o modelo é exatamente o que se quer. Aqui ele
        # atrapalha: o jogo de facas ensinaria que "jogo" é cozinha e, quando o
        # jogo de chaves de fenda chegasse, o atalho responderia "cozinha" sem
        # perguntar nada. A frase nunca seria gravada e a ambiguidade entre os
        # dois nunca apareceria — todo jogo viraria cozinha, inclusive os de
        # tabuleiro. Foi exatamente o que aconteceu antes desta linha existir.
        categoria = professor.categoria_de(texto, usar_generalizacao=False)
        print(f"  {texto:48} -> {categoria or '(nao reconhecido)'}")

        # Só falha do modelo interrompe o lote. Avisos de ambiguidade são
        # informativos — são o sistema percebendo que uma palavra serve a
        # categorias diferentes — e interrompem nada.
        if professor.modelo_falhou:
            print("\nO modelo parou de responder:")
            for aviso in professor.avisos:
                print(f"  - {aviso}")
            break

    print()
    if ignorados:
        print(f"{ignorados} produto(s) ignorado(s): o vocabulário já os reconhece.\n")

    corrigidos = 0
    for texto, categoria in sorted(CORRECOES.items()):
        if professor.ensinar(texto, categoria):
            print(f"  corrigido: {texto:48} -> {categoria}")
            corrigidos += 1

    if corrigidos:
        print(f"\n{corrigidos} correção(ões) humana(s) aplicada(s).")

    ambiguidades = [a for a in professor.avisos if "generalizar" in a]
    if ambiguidades:
        print("\nAmbiguidades detectadas durante a construção:")
        for aviso in ambiguidades:
            print(f"  - {aviso}")

    if professor.para_revisar:
        print("\nClassificacoes instaveis, que valem uma revisao humana:")
        for frase in professor.para_revisar:
            print(f"  - {frase}")
        print("(o modelo deu respostas diferentes ao ser perguntado varias vezes;")
        print(" isso aponta hesitacao, nao erro: medindo contra sete correcoes")
        print(" reais, a instabilidade apontou tres e deixou quatro passar)")

    print(f"\nTotal no arquivo agora: {professor.aprendidos} produtos, "
          f"{professor.palavras_aprendidas} palavras que generalizam.")
    if professor.ambiguas:
        print("Palavras descartadas por ambiguidade: "
              + ", ".join(professor.ambiguas))
        print("(apareceram com mais de uma categoria, entao nao servem de atalho)")


if __name__ == "__main__":
    main()
