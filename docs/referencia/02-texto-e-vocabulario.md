# Referência — Texto e vocabulário

Arquivos cobertos: `catalogo/texto.py` e `catalogo/vocabulario.py`.

São a camada que prepara o texto antes de ele virar chave de hash, e a lista que
liga palavras a tags.

---

## `catalogo/texto.py`

Normalização e separação de texto. Esta camada existe porque tabela hash
funciona por **igualdade exata**: "Tênis" e "tenis" geram números diferentes,
caem em baldes diferentes, e quem busca um nunca acha o outro.

A solução é reduzir todas as variações a uma forma única antes de qualquer
coisa tocar o hash.

### Constantes

| nome | o que é |
|---|---|
| `STOPWORDS` | conjunto de palavras de ligação descartadas (`de`, `para`, `em`, `com`…) |
| `TAMANHO_MINIMO_TOKEN` | `2` — palavras menores que isso são ignoradas |

As stopwords existem porque um termo que aparece em quase toda descrição não
serve para distinguir nada. A tag `para` apontaria para metade do catálogo.

### Funções

#### `remover_acentos(texto)`

Tira acentos preservando a letra base.

```python
>>> remover_acentos("tênis")
'tenis'
>>> remover_acentos("calção")
'calcao'
```

**Como funciona:** usa `unicodedata.normalize("NFD", texto)`, que separa a letra
do acento em dois caracteres distintos ("ê" vira "e" + acento solto). Depois
descarta os caracteres da categoria `Mn` (*Mark, nonspacing*), onde os acentos
vivem.

#### `normalizar(texto)`

Aplica a limpeza completa: minúsculas, sem acento, sem pontuação.

```python
>>> normalizar("Tênis, Azul!")
'tenis  azul '
>>> normalizar("Guarda-chuva")
'guardachuva'
```

Três comportamentos que valem conhecer:

**A pontuação vira espaço**, não é apagada. Se fosse apagada, `azul,corrida`
viraria a palavra inexistente `azulcorrida`.

**O hífen é a exceção: ele é apagado.** `Guarda-chuva` vira `guardachuva`, uma
palavra só. Antes ele virava espaço, e isso fazia o sistema tratar "guarda" como
se nomeasse o produto — colidindo com "guarda-roupa", que é um móvel.

**A regra do hífen vale só entre letras.** `aro 15 - novo` não vira `15novo`.

#### `tokenizar(texto)`

Quebra o texto em palavras aproveitáveis.

```python
>>> tokenizar("Tênis azul para corrida em asfalto")
['tenis', 'azul', 'corrida', 'asfalto']
```

A ordem das etapas importa: normalizar, separar, filtrar. Devolve na ordem em
que aparecem no texto, com repetições — quem usa decide se liga para repetição.

| | |
|---|---|
| **Devolve** | lista de strings |
| **Descarta** | stopwords e palavras com menos de 2 caracteres |

#### `singularizar(palavra)`

Tentativa ingênua de tirar o plural, removendo o "s" final.

```python
>>> singularizar("camisas")
'camisa'
>>> singularizar("gas")      # curta demais, preservada
'gas'
>>> singularizar("tenis")    # limitação conhecida
'teni'
```

**É uma heurística, e a limitação é assumida.** Funciona para "camisas", não
funciona para "papéis", e produz "teni" para "tênis".

A proteção contra esse último caso não está aqui, e sim em quem chama: o
`GeradorDeTags` só usa a forma singular se a palavra original não foi encontrada
no vocabulário. Como "tenis" está lá, ele nunca chega a tentar "teni".

Tratar plural de verdade exigiria um dicionário morfológico do português.

---

## `catalogo/vocabulario.py`

Contém uma constante só: `VOCABULARIO`.

### Formato

Lista de tuplas `(termo, tags)`:

```python
VOCABULARIO = [
    ("tenis", ("calcado", "esporte")),
    ("azul", ("azul", "cor")),
    ("couro", ("couro", "material")),
    ...
]
```

São 76 termos, agrupados por seção: calçados, roupas, esporte, superfície,
cores, materiais, eletrônicos e público.

### Duas decisões que valem explicação

**As tags são escritas sem acento.** `calcado`, não `calçado`. A tag vira chave
de hash, e hash exige igualdade exata — guardar na forma canônica elimina na
origem uma categoria inteira de bug. A busca aceita acento porque normaliza o
termo digitado.

**É uma lista de tuplas, não um dicionário.** Quem faz o papel de dicionário
neste projeto é a `TabelaHash`. Aqui é só o dado bruto; o `GeradorDeTags`
carrega estas entradas na estrutura ao iniciar.

### As formas femininas

As cores que mudam de gênero estão listadas uma a uma:

```python
("preto", ("preto", "cor")),
("preta", ("preto", "cor")),
```

Isso veio de um defeito real: "Chuteira preta" saía sem nenhuma tag de cor,
porque a regra de singular não trata gênero e `preta` não estava na lista.

Dava para escrever uma regra trocando "a" final por "o", mas ela estragaria
palavras legítimas — `rosa` viraria `roso`, `marca` viraria `marco`. Uma regra
que erra em silêncio é pior que nenhuma regra.

### Como acrescentar termos

Basta adicionar uma linha na seção correspondente:

```python
("cafeteira", ("cozinha", "eletrodomestico")),
```

Não é preciso mexer em mais nada — o gerador recarrega a lista ao iniciar. Para
descobrir que termos faltam, o módulo `inferencia.py` analisa o catálogo e
sugere regras novas (veja a [referência 04](04-catalogo.md)).
