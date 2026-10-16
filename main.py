"""
Interface de terminal do catálogo.

Este arquivo não tem lógica de estrutura de dados nenhuma. Ele só lê o que a
pessoa digitou, chama o Catalogo e imprime o resultado. A separação é de
propósito: toda a parte avaliada na disciplina está no pacote `catalogo/`, e
pode ser testada sem nunca abrir um terminal. Os testes automatizados do
projeto rodam sem passar por uma linha deste arquivo.

Rodar com:  python3 main.py        (só o vocabulário; roda em qualquer máquina)
            python3 main.py --ia   (o modelo local da Apple analisa todo produto,
                                    como descreve o item 2 do enunciado)

Aviso importante: o catálogo vive só na memória. Fechar o programa apaga tudo.
Persistir em arquivo seria assunto de outra disciplina (banco de dados ou
serialização) e não acrescentaria nada ao que o enunciado pede.
"""

import sys

from catalogo.catalogo import Catalogo

EXEMPLOS = [
    ("Tênis azul", "para corrida em asfalto"),
    ("Tênis preto", "para trilha e caminhada"),
    ("Camisa azul", "de algodão, masculino"),
    ("Chuteira preta", "para futebol na grama"),
    ("Fone bluetooth", "wireless, preto"),
    ("Mochila de nylon", "para notebook"),
]

MENU = """
========================================
  CATÁLOGO DE PRODUTOS COM TAGS
========================================
  1) Cadastrar produto
  2) Listar todos os produtos
  3) Buscar por tag
  4) Buscar por várias tags (todas)
  5) Buscar escrevendo uma frase
  A) Buscar palavra literal (indice de texto)
  B) Inferir regras novas a partir do catalogo
  C) Revisar classificacoes instaveis do modelo
  6) Ver tags existentes no catálogo
  7) Ver estado interno das tabelas hash
  8) Carregar produtos de exemplo
  9) Remover produto
  0) Sair
"""


def mostrar_produtos(produtos):
    if not produtos:
        print("\nNenhum produto encontrado.")
        return
    print(f"\n{len(produtos)} produto(s):")
    for produto in produtos:
        print("  " + produto.resumo())


def mostrar_estatisticas(catalogo, professor=None):
    """
    Abre a caixa preta.

    Esta tela existe para a apresentação: ela mostra que a tabela realmente
    espalhou as chaves em vez de empilhar tudo em poucos baldes. O número mais
    importante é a maior corrente — se ele crescer junto com a quantidade de
    produtos, a busca deixou de ser O(1) na prática.
    """
    dados = catalogo.estatisticas()

    for titulo, chave in (("TABELA DE PRODUTOS", "produtos"),
                          ("ÍNDICE DE TAGS (semântico)", "indice_de_tags"),
                          ("ÍNDICE DE TEXTO (literal)", "indice_de_texto")):
        tabela = dados[chave]
        print(f"\n{titulo}")
        print(f"  capacidade (baldes)...: {tabela['capacidade']}")
        print(f"  elementos guardados...: {tabela['elementos']}")
        print(f"  fator de carga........: {tabela['fator_carga']}")
        print(f"  baldes ocupados.......: {tabela['baldes_ocupados']}")
        print(f"  baldes vazios.........: {tabela['baldes_vazios']}")
        print(f"  maior corrente........: {tabela['maior_corrente']}")
        print(f"  colisões registradas..: {tabela['colisoes']}")

    print(f"\nTermos no vocabulário...: {dados['termos_no_vocabulario']}")
    if professor is not None:
        print(f"Produtos aprendidos.....: {professor.aprendidos} "
              f"({professor.novidades} nesta execução)")
        # Esta linha é a que diz se o aprendizado está valendo a pena: são as
        # palavras que dispensam consultar o modelo em produtos parecidos.
        print(f"Palavras generalizadas..: {professor.palavras_aprendidas}")
        if professor.ambiguas:
            print(f"Palavras ambíguas.......: {', '.join(professor.ambiguas)}")


def mostrar_avisos(professor, ja_vistos):
    """
    Mostra o que apareceu de novo desde a última vez, e devolve o total visto.

    Duas correções vieram de assistir o programa rodando. A primeira: a lista
    de avisos acumula desde o início, e exibi-la inteira a cada operação fazia
    o mesmo aviso reaparecer depois de listar, de buscar e de abrir as
    estatísticas — operações que nem chegam perto do modelo. Agora só o que é
    novo é mostrado.

    A segunda é o texto. Havia um rótulo só, dizendo que o programa estava
    "seguindo só com o vocabulário", e ele aparecia também para avisos que não
    são falha nenhuma. Descobrir que uma palavra é ambígua é o sistema
    funcionando; anunciar isso como se fosse defeito confunde quem lê e
    esconde as falhas de verdade no meio do ruído.
    """
    if professor is None:
        return ja_vistos

    novos = professor.avisos[ja_vistos:]
    if not novos:
        return ja_vistos

    if professor.modelo_falhou:
        print("\nO modelo não respondeu; seguindo só com o vocabulário:")
    else:
        print("\nObservações do aprendizado:")
    for aviso in novos:
        print(f"  - {aviso}")

    return len(professor.avisos)


def mostrar_revisao(professor):
    """
    Lista os produtos que o modelo classificou de forma hesitante.

    A hesitação é medida perguntando a mesma coisa várias vezes com o modelo
    livre para variar: se as respostas divergem, ele não estava seguro. O sinal
    é fraco — contra sete correções feitas à mão, apontou três e deixou quatro
    passar —, então isto é uma ordem de prioridade para revisar, não um
    veredito sobre o que está errado.
    """
    if professor is None:
        print("\nEsta tela só existe no modo --aprender.")
        return
    pendentes = professor.para_revisar
    if not pendentes:
        print("\nNenhuma classificação pendente de revisão.")
        return
    print(f"\n{len(pendentes)} classificação(ões) para revisar:")
    for frase in pendentes:
        print(f"  - {frase}")
    print("\nPara corrigir, edite dados/aprendido.json ou acrescente a correção")
    print("em CORRECOES, no povoar_aprendizado.py, e rode o script de novo.")


def mostrar_inferencias(catalogo):
    """
    Mostra regras que o próprio catálogo sugere, sem consultar nada.

    É a única forma de aprendizado do projeto que não depende de modelo, de
    internet nem de vocabulário: ela cruza os dois índices invertidos e procura
    palavras cujos produtos concordam todos na mesma tag.
    """
    from catalogo.inferencia import formatar, inferir_regras

    print()
    for linha in formatar(inferir_regras(catalogo)):
        print(linha)


def cadastrar(catalogo):
    nome = input("Nome do produto: ").strip()
    descricao = input("Descrição......: ").strip()
    try:
        produto = catalogo.cadastrar(nome, descricao)
    except ValueError as erro:
        print(f"\nNão deu para cadastrar: {erro}")
        return
    print(f"\nCadastrado: {produto.resumo()}")
    if not produto.tags:
        print("Atenção: nenhuma palavra conhecida foi encontrada, então este")
        print("produto não vai aparecer em buscas por tag.")


def remover(catalogo):
    identificador = input("Identificador (ex: P001): ").strip().upper()
    try:
        produto = catalogo.remover(identificador)
    except KeyError:
        print("\nNão existe produto com esse identificador.")
        return
    print(f"\nRemovido: {produto.resumo()}")


def carregar_exemplos(catalogo):
    for nome, descricao in EXEMPLOS:
        catalogo.cadastrar(nome, descricao)
    print(f"\n{len(EXEMPLOS)} produtos de exemplo cadastrados.")
    mostrar_produtos(catalogo.todos())


def montar_gerador(argumentos):
    """
    Monta o gerador de tags conforme a linha de comando.

    Existe um gerador só. A diferença que `--aprender` faz é dar a ele um
    professor: alguém a quem recorrer quando o vocabulário não reconhece nada
    em um produto.

    O aprendizado fica em `dados/aprendido.json`, que é versionado junto com o
    projeto. Esse detalhe é o que resolve a portabilidade: quem roda em uma
    máquina sem Apple Intelligence não aprende nada novo, mas aproveita tudo
    que já foi aprendido em outra. O conhecimento mora no arquivo, não no
    modelo.
    """
    from catalogo.tagger import GeradorDeTags

    # "--aprender" continua aceito porque era o nome anterior deste modo.
    if not {"--ia", "--aprender"} & set(argumentos):
        return GeradorDeTags(), None, "vocabulário próprio"

    from catalogo.professor import Professor

    professor = Professor()
    gerador = GeradorDeTags(professor=professor, ia_primeiro=True)
    modo = (f"modelo local da Apple (categoria) + vocabulário (cor, material, uso) "
            f"— {professor.aprendidos} produtos e "
            f"{professor.palavras_aprendidas} palavras já aprendidos")
    return gerador, professor, modo


def main():
    gerador, professor, descricao_do_modo = montar_gerador(sys.argv[1:])
    catalogo = Catalogo(gerador_de_tags=gerador)
    # Quantos avisos já foram mostrados, para não repetir os antigos.
    avisos_vistos = 0
    print(f"\nGerando tags por: {descricao_do_modo}")

    acoes = {
        "1": lambda: cadastrar(catalogo),
        "2": lambda: mostrar_produtos(catalogo.todos()),
        "3": lambda: mostrar_produtos(
            catalogo.buscar_por_tag(input("Tag: "))
        ),
        "4": lambda: mostrar_produtos(
            catalogo.buscar_por_tags(input("Tags separadas por espaço: ").split())
        ),
        "5": lambda: mostrar_produtos(
            catalogo.buscar_por_texto(input("Digite o que procura: "))
        ),
        # Busca pelo índice literal. Serve para quando a pessoa procura uma
        # palavra que está escrita no produto mas não é tag de nada, como o
        # material de uma frigideira classificada só como "cozinha".
        "A": lambda: mostrar_produtos(
            catalogo.buscar_por_palavra(input("Palavra: "))
        ),
        "B": lambda: mostrar_inferencias(catalogo),
        "C": lambda: mostrar_revisao(professor),
        "6": lambda: print("\nTags no catálogo: " + (
            ", ".join(catalogo.tags_conhecidas()) or "nenhuma ainda"
        )),
        "7": lambda: mostrar_estatisticas(catalogo, professor),
        "8": lambda: carregar_exemplos(catalogo),
        "9": lambda: remover(catalogo),
    }

    while True:
        print(MENU)
        try:
            opcao = input("Escolha: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C ou Ctrl+D não deveriam despejar um traceback na tela.
            print("\nAté mais.")
            return

        if opcao == "0":
            print("\nAté mais.")
            return

        acao = acoes.get(opcao)
        if acao is None:
            print("\nOpção inválida.")
            continue

        try:
            acao()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais.")
            return

        avisos_vistos = mostrar_avisos(professor, avisos_vistos)


if __name__ == "__main__":
    main()
