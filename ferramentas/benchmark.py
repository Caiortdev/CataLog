"""
Mede, na prática, a diferença entre buscar com índice e buscar varrendo tudo.

O relatório poderia só afirmar "o índice invertido é O(1) e a varredura é
O(n)". Mas afirmar não é demonstrar. Este script roda as duas buscas no mesmo
catálogo, com o mesmo resultado esperado, e mostra o tempo de cada uma
enquanto o catálogo cresce.

O que observar na saída: o tempo da busca com índice praticamente não muda
quando o catálogo cresce, enquanto o da varredura cresce junto. Isso é a
definição de O(1) contra O(n) aparecendo em milissegundos.

Rodar com:  python3 ferramentas/benchmark.py
"""

import time

import os
import sys

# Permite rodar este script direto, de qualquer lugar:
#     python3 ferramentas/benchmark.py
#
# Sem estas linhas o Python procuraria o pacote "catalogo" dentro de
# ferramentas/, porque é a pasta do script que entra no caminho de busca — não
# a pasta de onde o comando foi chamado.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalogo.catalogo import Catalogo

TAMANHOS = [1000, 10000, 50000]
REPETICOES = 50
TAG_PROCURADA = "natacao"


def montar_catalogo(quantidade):
    """
    Monta um catálogo onde a tag procurada é rara.

    A raridade é proposital: ela representa o caso realista de um e-commerce,
    em que o cliente filtra por algo específico dentro de um catálogo enorme.
    É também o caso em que a diferença entre as duas abordagens fica mais
    visível, porque a varredura precisa olhar tudo para achar pouca coisa.
    """
    catalogo = Catalogo()
    for i in range(quantidade):
        if i % 100 == 0:
            catalogo.cadastrar(f"Tenis modelo {i}", "para natacao")
        else:
            catalogo.cadastrar(f"Camisa modelo {i}", "de algodao")
    return catalogo


def busca_com_indice(catalogo):
    """O que o projeto faz: uma consulta direta no índice invertido."""
    return catalogo.buscar_por_tag(TAG_PROCURADA)


def busca_por_varredura(catalogo):
    """
    O que o projeto FARIA sem o índice invertido: abrir produto por produto e
    conferir a lista de tags de cada um.

    Esta é a implementação ingênua, e ela está aqui só para comparação. Note
    que ela nem é mal escrita — o problema não é a qualidade do código, é a
    estrutura que ele é obrigado a percorrer.
    """
    return [p for p in catalogo.todos() if TAG_PROCURADA in p.tags]


def cronometrar(funcao, catalogo):
    inicio = time.perf_counter()
    for _ in range(REPETICOES):
        resultado = funcao(catalogo)
    duracao = (time.perf_counter() - inicio) / REPETICOES
    return duracao, len(resultado)


def main():
    print(f"Cada medição é a média de {REPETICOES} execuções.")
    print(f"Tag procurada: {TAG_PROCURADA!r}\n")
    print(f"{'produtos':>10} | {'achados':>8} | {'indice (ms)':>12} | "
          f"{'varredura (ms)':>15} | {'quantas vezes':>14}")
    print("-" * 72)

    for quantidade in TAMANHOS:
        catalogo = montar_catalogo(quantidade)

        tempo_indice, achados = cronometrar(busca_com_indice, catalogo)
        tempo_varredura, achados_varredura = cronometrar(busca_por_varredura, catalogo)

        # As duas buscas precisam achar exatamente a mesma coisa, senão a
        # comparação de tempo não significa nada.
        assert achados == achados_varredura, "as duas buscas discordaram"

        vezes = tempo_varredura / tempo_indice if tempo_indice else float("inf")
        print(f"{quantidade:>10} | {achados:>8} | {tempo_indice * 1000:>12.4f} | "
              f"{tempo_varredura * 1000:>15.4f} | {vezes:>13.0f}x")

    print("\nO tempo da coluna 'indice' depende de quantos produtos foram")
    print("ACHADOS, nao de quantos existem no catalogo. O da varredura depende")
    print("de quantos existem. E essa a diferenca entre O(k) e O(n).")


if __name__ == "__main__":
    main()
