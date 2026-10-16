"""
Põe à prova as afirmações estruturais do documento 1.

O projeto inteiro adotou o hábito de medir em vez de assumir: o modelo de
linguagem foi testado em três desenhos diferentes, o índice invertido foi
cronometrado, a medida de confiança foi avaliada e descartada como sinal fraco.
Mas as decisões sobre a própria tabela hash continuavam sustentadas por teoria
repetida de livro:

  1. capacidade em número primo espalha melhor que potência de dois;
  2. fator de carga 0.75 é um bom limite;
  3. endereçamento aberto degrada com muitas remoções;
  4. encadeamento gasta mais memória.

Era a parte mais importante do trabalho e a única sem número. Este arquivo
corrige isso.

Rodar com:  python3 ferramentas/benchmark_colisoes.py
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

from catalogo.hashtable import TabelaHash, hash_djb2
from catalogo.hashtable_aberta import TabelaHashAberta


def titulo(texto):
    print()
    print("=" * 72)
    print(texto)
    print("=" * 72)


def chaves(quantidade, prefixo="produto"):
    return [f"{prefixo}-{i}" for i in range(quantidade)]


# ----------------------------------------------------------------------
# 1. Capacidade prima contra potência de dois
# ----------------------------------------------------------------------

def distribuicao(capacidade, lista_de_chaves):
    """Quantas chaves caem em cada posição, para uma dada capacidade."""
    contagem = [0] * capacidade
    for chave in lista_de_chaves:
        contagem[hash_djb2(chave) % capacidade] += 1
    return contagem


def resumo_da_distribuicao(contagem, total):
    ocupados = sum(1 for c in contagem if c)
    return {
        "baldes_usados": ocupados,
        "baldes_vazios": len(contagem) - ocupados,
        "maior_balde": max(contagem),
        "media_por_balde_usado": round(total / ocupados, 2) if ocupados else 0,
    }


def experimento_primo_vs_potencia():
    titulo("1. Capacidade prima contra potência de dois")
    print("A afirmação: primo evita que as chaves se concentrem em poucos baldes.")
    print("Teste: as mesmas 5000 chaves, duas capacidades quase iguais.\n")

    lista = chaves(5000)
    for rotulo, capacidade in (("potência de dois", 1024), ("primo", 1031)):
        r = resumo_da_distribuicao(distribuicao(capacidade, lista), len(lista))
        print(f"  {rotulo:18} (m={capacidade})  "
              f"usados: {r['baldes_usados']:5}  vazios: {r['baldes_vazios']:4}  "
              f"maior balde: {r['maior_balde']:3}  média: {r['media_por_balde_usado']}")

    print("\nE agora com chaves que seguem um padrão forte (múltiplos de 16),")
    print("que é o caso em que a teoria diz que a diferença aparece:\n")

    padronizadas = [f"id{i * 16:08d}" for i in range(5000)]
    for rotulo, capacidade in (("potência de dois", 1024), ("primo", 1031)):
        r = resumo_da_distribuicao(distribuicao(capacidade, padronizadas), 5000)
        print(f"  {rotulo:18} (m={capacidade})  "
              f"usados: {r['baldes_usados']:5}  vazios: {r['baldes_vazios']:4}  "
              f"maior balde: {r['maior_balde']:3}  média: {r['media_por_balde_usado']}")


# ----------------------------------------------------------------------
# 2. Qual fator de carga vale a pena
# ----------------------------------------------------------------------

def custo_medio(tabela, lista_de_chaves):
    return sum(tabela.custo_de_busca(c) for c in lista_de_chaves) / len(lista_de_chaves)


def experimento_fator_de_carga():
    titulo("2. O limite de 0.75 se justifica?")
    print("A afirmação: 0.75 equilibra memória e velocidade (é o do HashMap do Java).")
    print("Teste: a mesma carga com limites diferentes, medindo comparações por busca.\n")

    lista = chaves(20000)
    print(f"  {'limite':>8} {'capacidade':>11} {'carga real':>11} "
          f"{'comparações/busca':>18} {'maior corrente':>15}")
    print("  " + "-" * 68)

    for limite in (0.5, 0.75, 1.0, 2.0, 5.0):
        class Variante(TabelaHash):
            FATOR_CARGA_MAXIMO = limite

        tabela = Variante(capacidade_inicial=11)
        for chave in lista:
            tabela.inserir(chave, 1)

        e = tabela.estatisticas()
        print(f"  {limite:>8} {e['capacidade']:>11} {e['fator_carga']:>11} "
              f"{custo_medio(tabela, lista):>18.2f} {e['maior_corrente']:>15}")


# ----------------------------------------------------------------------
# 3. O que acontece com muitas remoções
# ----------------------------------------------------------------------

def experimento_remocoes():
    titulo("3. Encadeamento contra endereçamento aberto, sob remoções")
    print("A afirmação: endereçamento aberto degrada porque as lápides se acumulam.")
    print("Teste: inserir 10000, depois alternar remoção e inserção 20000 vezes.\n")

    total = 10000
    lista = chaves(total)

    for rotulo, Classe in (("encadeamento", TabelaHash),
                           ("endereç. aberto", TabelaHashAberta)):
        tabela = Classe(capacidade_inicial=11)
        for chave in lista:
            tabela.inserir(chave, 1)

        antes = custo_medio(tabela, lista)

        inicio = time.perf_counter()
        for ciclo in range(20000):
            alvo = f"produto-{ciclo % total}"
            try:
                tabela.remover(alvo)
            except KeyError:
                pass
            tabela.inserir(f"extra-{ciclo}", 1)
            tabela.remover(f"extra-{ciclo}")
            tabela.inserir(alvo, 1)
        duracao = time.perf_counter() - inicio

        depois = custo_medio(tabela, lista)
        extra = tabela.estatisticas().get("lapides", "-")
        print(f"  {rotulo:16} comparações/busca antes: {antes:.2f}  "
              f"depois: {depois:.2f}  lápides: {extra}  tempo: {duracao:.2f}s")


# ----------------------------------------------------------------------
# 4. Memória
# ----------------------------------------------------------------------

def memoria_aproximada(tabela):
    """
    Estimativa do espaço ocupado, em "posições de ponteiro".

    Não usamos `sys.getsizeof` porque ele não acompanha os objetos apontados,
    e o encadeamento guarda justamente objetos. A conta aqui é estrutural:
    quantas referências cada estratégia precisa manter.
    """
    estatisticas = tabela.estatisticas()
    capacidade = estatisticas["capacidade"]
    elementos = estatisticas["elementos"]

    if isinstance(tabela, TabelaHashAberta):
        # Dois vetores do tamanho da capacidade: chaves e valores.
        return capacidade * 2
    # Um vetor de baldes, mais um nó por elemento. Cada nó guarda chave, valor
    # e o ponteiro para o próximo.
    return capacidade + elementos * 3


def experimento_memoria():
    titulo("4. Quanto cada estratégia gasta de memória")
    print("A afirmação: encadeamento gasta mais, porque cria um objeto por elemento.")
    print("Medida: referências mantidas pela estrutura, com 10000 elementos.\n")

    lista = chaves(10000)
    for rotulo, Classe in (("encadeamento", TabelaHash),
                           ("endereç. aberto", TabelaHashAberta)):
        tabela = Classe(capacidade_inicial=11)
        for chave in lista:
            tabela.inserir(chave, 1)
        e = tabela.estatisticas()
        print(f"  {rotulo:16} capacidade: {e['capacidade']:6}  "
              f"referências: {memoria_aproximada(tabela):7}  "
              f"comparações/busca: {custo_medio(tabela, lista):.2f}")


def experimento_agrupamento():
    """
    O experimento que explica os outros.

    Ele foi acrescentado depois, porque o teste de remoções deu um resultado
    que não batia com a explicação do documento 1: o endereçamento aberto não
    degradou com as remoções, mas já começava quase três vezes pior. Faltava
    entender de onde vinha essa desvantagem inicial.

    A resposta é o agrupamento primário da sondagem linear. Quando uma chave é
    desviada, ela ocupa a posição vizinha; a próxima chave que quiser aquela
    posição também será desviada, e o bloco cresce. Blocos maiores capturam
    mais chaves, que fazem os blocos crescerem mais — a desvantagem se
    alimenta sozinha.

    No encadeamento isso não acontece: uma corrente longa não contamina os
    baldes vizinhos, porque eles são independentes.
    """
    titulo("5. Por que o endereçamento aberto perde: agrupamento")
    print("Teste: mesma capacidade, ocupação crescente, sem redimensionar,")
    print("medindo quantas comparações cada busca custa.\n")

    capacidade = 10007
    print(f"  {'ocupação':>9} {'encadeamento':>14} {'endereç. aberto':>17}")
    print("  " + "-" * 42)

    for carga in (0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95):
        lista = chaves(int(capacidade * carga))

        # O limite alto desliga o redimensionamento, para a ocupação ser
        # exatamente a que queremos testar.
        class Encadeada(TabelaHash):
            FATOR_CARGA_MAXIMO = 99

        class Aberta(TabelaHashAberta):
            FATOR_CARGA_MAXIMO = 99

        encadeada, aberta = Encadeada(capacidade), Aberta(capacidade)
        for chave in lista:
            encadeada.inserir(chave, 1)
            aberta.inserir(chave, 1)

        print(f"  {carga:>9} {custo_medio(encadeada, lista):>14.2f} "
              f"{custo_medio(aberta, lista):>17.2f}")

    print("\nO encadeamento cresce devagar e de forma previsível. O endereçamento")
    print("aberto desanda: com a tabela quase cheia, cada busca custa dezenas de")
    print("comparações, e a estrutura deixa de ser O(1) na prática.")


def main():
    experimento_primo_vs_potencia()
    experimento_fator_de_carga()
    experimento_remocoes()
    experimento_memoria()
    experimento_agrupamento()
    print()


if __name__ == "__main__":
    main()
