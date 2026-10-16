"""
Descobre regras de vocabulário olhando o catálogo que já existe.

Esta é a única parte do projeto que aprende sem consultar nada: nem modelo de
linguagem, nem internet, nem vocabulário. Ela usa só os dois índices
invertidos que o catálogo já mantém, e tira conclusões do que está lá.

O raciocínio é de estatística simples. Se existem seis produtos cujo texto
contém a palavra "chuteira", e todos os seis têm a tag "calcado", então é
razoável propor a regra:

    chuteira -> calcado

Ninguém precisou ensinar isso. A informação já estava no catálogo, espalhada
entre os produtos; faltava cruzar os dois índices para enxergá-la.

Vale notar de onde vem a capacidade de fazer isso. O índice de texto responde
"quais produtos contêm esta palavra" em O(1), e cada produto carrega suas
tags. Sem o índice invertido, a mesma pergunta exigiria varrer o catálogo
inteiro uma vez por palavra — o custo sairia do controle rápido. É um caso em
que a estrutura escolhida no começo do projeto habilitou um uso que não estava
previsto.
"""

from catalogo.texto import normalizar
from catalogo.vocabulario import VOCABULARIO

# Quantos produtos precisam concordar para a regra ser proposta.
#
# Com dois produtos, qualquer coincidência vira "regra": dois tênis azuis
# bastariam para o sistema concluir que "tenis" significa "azul". Três é o
# menor número em que a concordância começa a dizer alguma coisa, e ainda
# assim a decisão final é de quem lê a sugestão.
MINIMO_DE_PRODUTOS = 3


def termos_do_vocabulario():
    """As palavras que o vocabulário já conhece, na forma normalizada."""
    return {normalizar(termo).strip() for termo, _ in VOCABULARIO}


def inferir_regras(catalogo, minimo=MINIMO_DE_PRODUTOS, ignorar_conhecidas=True):
    """
    Propõe regras "palavra -> tag" a partir do catálogo.

    Devolve uma lista de tuplas (palavra, tag, quantidade), ordenada da
    sugestão mais sustentada para a menos.

    O critério é deliberadamente rígido: a tag precisa estar em TODOS os
    produtos que contêm a palavra, não na maioria. Uma regra que vale em nove
    de dez casos não é uma regra — é um palpite que vai classificar o décimo
    produto errado, e em silêncio.

    Por padrão, palavras que o vocabulário já conhece são omitidas: sugerir
    que "tenis" significa "calcado" não acrescenta nada a quem lê.

    Note que estas são sugestões, não aprendizado automático. A diferença é a
    mesma lição que o modelo de linguagem ensinou neste projeto: gravar
    sozinho uma conclusão errada é pior que não concluir nada, porque o erro
    fica e ninguém revisa.
    """
    conhecidas = termos_do_vocabulario() if ignorar_conhecidas else set()
    sugestoes = []

    for palavra in catalogo.palavras_indexadas():
        if palavra in conhecidas:
            continue

        produtos = catalogo.buscar_por_palavra(palavra)
        if len(produtos) < minimo:
            continue

        # Interseção das tags: o que TODOS esses produtos têm em comum.
        # Usamos conjuntos do Python aqui porque a operação é interseção, não
        # busca — nenhum deles faz o papel de índice.
        comuns = set(produtos[0].tags)
        for produto in produtos[1:]:
            comuns &= set(produto.tags)
            if not comuns:
                break

        for tag in comuns:
            # Uma palavra que já é a própria tag não ensina nada: "corrida"
            # aparecer em produtos marcados com "corrida" era de se esperar.
            if tag != palavra:
                sugestoes.append((palavra, tag, len(produtos)))

    # Mais produtos concordando primeiro; empate resolvido em ordem alfabética
    # só para a saída ser estável entre execuções.
    sugestoes.sort(key=lambda s: (-s[2], s[0], s[1]))
    return sugestoes


def formatar(sugestoes):
    """Transforma as sugestões em linhas prontas para o terminal."""
    if not sugestoes:
        return ["Nenhuma regra nova pôde ser inferida do catálogo atual."]

    linhas = ["Regras sugeridas pelo próprio catálogo:", ""]
    for palavra, tag, quantidade in sugestoes:
        linhas.append(f'  ("{palavra}", ("{tag}",)),'
                      f'   # {quantidade} produtos concordam')
    linhas.append("")
    linhas.append("Para adotar, copie as linhas acima para catalogo/vocabulario.py.")
    linhas.append("Nada é gravado automaticamente: a revisão é sua.")
    return linhas
