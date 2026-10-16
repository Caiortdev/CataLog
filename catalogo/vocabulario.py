"""
O vocabulário que o gerador de tags consulta.

Este arquivo é o "conhecimento" do sistema: ele diz que a palavra "tenis"
indica um calçado esportivo, que "azul" é uma cor, e assim por diante. É um
mapeamento de termo -> tags que ele dispara.

Duas observações importantes:

Sobre a forma das tags. Todas são escritas em minúsculas e sem acento. Isso
não é descuido. A tag vai virar chave da tabela hash, e hash só acha o que é
exatamente igual. Se guardássemos "calçado" e o cliente digitasse "calcado",
os dois textos teriam hashes diferentes e a busca falharia. Guardando já na
forma canônica, o problema some na origem.

Sobre a escolha do formato. É uma lista de tuplas, e não um dicionário do
Python, porque quem faz o papel de dicionário neste projeto é a nossa
TabelaHash. Aqui isto é só o dado bruto; o tagger carrega estas entradas na
tabela ao iniciar.
"""

VOCABULARIO = [
    # ---- Calçados ----
    ("tenis", ("calcado", "esporte")),
    ("sapato", ("calcado",)),
    ("sandalia", ("calcado",)),
    ("chinelo", ("calcado",)),
    ("bota", ("calcado",)),
    ("sapatilha", ("calcado",)),
    ("chuteira", ("calcado", "futebol", "esporte")),

    # ---- Roupas ----
    ("camisa", ("vestuario",)),
    ("camiseta", ("vestuario",)),
    ("blusa", ("vestuario",)),
    ("calca", ("vestuario",)),
    ("bermuda", ("vestuario",)),
    ("short", ("vestuario",)),
    ("jaqueta", ("vestuario", "agasalho")),
    ("moletom", ("vestuario", "agasalho")),
    ("casaco", ("vestuario", "agasalho")),
    ("vestido", ("vestuario",)),
    ("saia", ("vestuario",)),
    ("meia", ("vestuario",)),
    ("bone", ("acessorio",)),
    ("mochila", ("acessorio",)),
    ("bolsa", ("acessorio",)),

    # ---- Esporte e uso ----
    ("corrida", ("corrida", "esporte")),
    ("correr", ("corrida", "esporte")),
    ("caminhada", ("caminhada", "esporte")),
    ("treino", ("treino", "esporte")),
    ("academia", ("treino", "esporte")),
    ("futebol", ("futebol", "esporte")),
    ("basquete", ("basquete", "esporte")),
    ("ciclismo", ("ciclismo", "esporte")),
    ("natacao", ("natacao", "esporte")),
    ("trilha", ("trilha", "aventura")),

    # ---- Superfície / ambiente ----
    ("asfalto", ("asfalto", "rua")),
    ("rua", ("rua",)),
    ("quadra", ("quadra",)),
    ("grama", ("grama",)),
    ("praia", ("praia",)),

    # ---- Cores ----
    #
    # As formas femininas estão listadas uma a uma de propósito. A regra de
    # singular do módulo de texto só remove o "s" final; ela não sabe nada
    # sobre gênero, então "preta" nunca viraria "preto" sozinha. Descobrimos
    # isso testando o programa: "Chuteira preta" saía sem nenhuma tag de cor.
    #
    # Dava para escrever uma regra trocando "a" final por "o", mas ela
    # estragaria palavras legítimas ("rosa" viraria "roso", "marca" viraria
    # "marco"). Listar as poucas cores que mudam de gênero é mais honesto e
    # mais previsível do que inventar uma regra que erra em silêncio.
    ("azul", ("azul", "cor")),
    ("vermelho", ("vermelho", "cor")),
    ("vermelha", ("vermelho", "cor")),
    ("verde", ("verde", "cor")),
    ("preto", ("preto", "cor")),
    ("preta", ("preto", "cor")),
    ("branco", ("branco", "cor")),
    ("branca", ("branco", "cor")),
    ("amarelo", ("amarelo", "cor")),
    ("amarela", ("amarelo", "cor")),
    ("cinza", ("cinza", "cor")),
    ("rosa", ("rosa", "cor")),
    ("roxo", ("roxo", "cor")),
    ("roxa", ("roxo", "cor")),
    ("laranja", ("laranja", "cor")),
    ("marrom", ("marrom", "cor")),
    ("bege", ("bege", "cor")),

    # ---- Materiais ----
    ("couro", ("couro", "material")),
    ("algodao", ("algodao", "material")),
    ("poliester", ("poliester", "material")),
    ("jeans", ("jeans", "material")),
    ("nylon", ("nylon", "material")),
    ("borracha", ("borracha", "material")),

    # ---- Eletrônicos ----
    ("celular", ("eletronico", "telefonia")),
    ("smartphone", ("eletronico", "telefonia")),
    ("notebook", ("eletronico", "informatica")),
    ("computador", ("eletronico", "informatica")),
    ("teclado", ("eletronico", "informatica")),
    ("mouse", ("eletronico", "informatica")),
    ("monitor", ("eletronico", "informatica")),
    ("fone", ("eletronico", "audio")),
    ("headphone", ("eletronico", "audio")),
    ("bluetooth", ("bluetooth", "wireless")),
    ("wireless", ("wireless",)),
    ("usb", ("usb",)),

    # ---- Público ----
    ("masculino", ("masculino",)),
    ("feminino", ("feminino",)),
    ("infantil", ("infantil",)),
    ("unissex", ("unissex",)),
]
