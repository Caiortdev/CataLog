"""
Preparação do texto antes de virar tag.

Por que esta etapa existe? Porque texto digitado por gente é bagunçado. O
mesmo produto pode chegar como "Tênis Azul", "tenis azul" ou "TÊNIS, azul."
Se jogarmos isso direto na tabela hash, cada variação vira uma chave
diferente, com um hash diferente, num balde diferente. O cliente que buscar
"tenis" não acharia o produto cadastrado como "Tênis".

Então o trabalho aqui é reduzir todas as variações a uma forma única. Em
processamento de texto isso se chama normalização, e é o que torna a busca
por hash viável: hash exige igualdade exata, então a gente garante a
igualdade antes.
"""

import unicodedata

# Palavras que aparecem em quase toda descrição e não ajudam a distinguir
# nada. "para corrida em asfalto" tem três palavras úteis e duas de ligação.
# Guardá-las como tag só encheria o índice de ruído: a tag "para" apontaria
# para metade do catálogo e não serviria para filtrar.
STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "pela", "pelo", "por", "que", "se", "sem", "sob", "sobre", "um", "uma",
    "uns", "umas",
}

TAMANHO_MINIMO_TOKEN = 2


def remover_acentos(texto):
    """
    Tira acentos preservando a letra base: "tênis" vira "tenis".

    Como funciona: a forma NFD do Unicode separa a letra do acento em dois
    caracteres distintos ("ê" vira "e" + um acento solto). Depois disso basta
    descartar os caracteres da categoria Mn (Mark, nonspacing), que é onde os
    acentos vivem.

    Sem isso, hash_djb2("tênis") e hash_djb2("tenis") dão números diferentes,
    porque ord("ê") não é ord("e"). Acento mudaria o balde.
    """
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def normalizar(texto):
    """
    Deixa o texto em minúsculas, sem acento e sem pontuação.

    A pontuação vira espaço em vez de ser apagada: "azul,corrida" precisa
    virar duas palavras, não a palavra "azulcorrida".

    O hífen é a exceção, e ele é apagado em vez de virar espaço. O motivo veio
    de um defeito real: "Guarda-chuva" virava as palavras "guarda" e "chuva", e
    o sistema passava a tratar "guarda" como se ela nomeasse o produto. Isso é
    um problema porque "guarda-roupa" também começa com "guarda" e é um móvel,
    não um acessório — as duas coisas colidiriam na mesma chave.

    Apagando o hífen, "guarda-chuva" vira "guardachuva" e "guarda-roupa" vira
    "guardaroupa": duas palavras distintas, como de fato são. A regra vale só
    entre letras, para não transformar "aro 15 - novo" em "15novo".
    """
    texto = remover_acentos(texto.lower())
    texto = _juntar_hifenizadas(texto)
    return "".join(c if c.isalnum() else " " for c in texto)


def _juntar_hifenizadas(texto):
    """Remove o hífen quando ele liga duas letras, preservando-o no resto."""
    resultado = []
    for i, caractere in enumerate(texto):
        if caractere == "-" and 0 < i < len(texto) - 1:
            if texto[i - 1].isalpha() and texto[i + 1].isalpha():
                continue
        resultado.append(caractere)
    return "".join(resultado)


def tokenizar(texto):
    """
    Quebra o texto em palavras aproveitáveis.

    A ordem das etapas importa:
      1. normalizar  — para "Tênis," e "tenis" virarem a mesma coisa
      2. separar     — split() já ignora espaços múltiplos
      3. filtrar     — fora stopwords e tokens curtos demais

    Devolve na ordem em que aparecem no texto, com repetições. Quem usa decide
    se liga para repetição; aqui a gente não descarta informação à toa.
    """
    palavras = normalizar(texto).split()
    return [
        palavra
        for palavra in palavras
        if palavra not in STOPWORDS and len(palavra) >= TAMANHO_MINIMO_TOKEN
    ]


def singularizar(palavra):
    """
    Tentativa ingênua de tirar o plural, só removendo o "s" final.

    Isto é uma heurística, e assumimos a limitação de frente: funciona para
    "camisas" -> "camisa", não funciona para "papéis" -> "papel" nem para
    "tênis", que já termina em "s" no singular.

    A proteção contra o caso do "tênis" não está aqui, e sim em quem chama:
    o gerador de tags só usa a forma singular se a palavra original não foi
    encontrada no vocabulário. Como "tenis" está lá, ele nunca chega a tentar
    "teni".

    Tratar plural de verdade exigiria um dicionário morfológico do português,
    que é um problema de outra disciplina.
    """
    if len(palavra) > 3 and palavra.endswith("s"):
        return palavra[:-1]
    return palavra
