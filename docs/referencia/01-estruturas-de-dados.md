# Referência — Estruturas de dados

Arquivos cobertos: `catalogo/hashtable.py` e `catalogo/hashtable_aberta.py`.

São o núcleo do projeto: duas implementações de tabela de dispersão, escritas do
zero, com a mesma interface pública. A primeira é usada pelo catálogo; a segunda
existe para comparação e está documentada no [documento 1](../01-tabela-hash.md).

---

## `catalogo/hashtable.py`

Tabela de dispersão com tratamento de colisão por **encadeamento separado**:
cada posição do vetor guarda o início de uma lista encadeada, e chaves que caem
no mesmo lugar são penduradas uma na outra.

### Funções do módulo

#### `hash_djb2(texto)`

A função de dispersão. Converte uma string em um número inteiro de 32 bits.

| | |
|---|---|
| `texto` | a string a ser convertida |
| **Devolve** | inteiro entre 0 e 4.294.967.295 |
| **Custo** | O(c), com c = número de caracteres |

```python
>>> from catalogo.hashtable import hash_djb2
>>> hash_djb2("tenis")
2090640929
>>> hash_djb2("tenis")      # sempre o mesmo valor
2090640929
```

É determinística de propósito. O `hash()` embutido do Python muda de resultado a
cada execução do interpretador, o que tornaria impossível testar a distribuição.

#### `_proximo_primo(n)` e `_e_primo(n)`

Auxiliares internos. `_proximo_primo` devolve o menor primo maior ou igual a
`n`, e é o que garante que a capacidade da tabela seja sempre prima.

---

### `class TabelaHash`

#### Construtor

```python
TabelaHash(capacidade_inicial=11)
```

`capacidade_inicial` é arredondada para cima até o próximo primo.

#### Constante de classe

| nome | valor | o que é |
|---|---|---|
| `FATOR_CARGA_MAXIMO` | `0.75` | ocupação a partir da qual a tabela dobra de tamanho |

#### Métodos de escrita

##### `inserir(chave, valor)`

Insere um par, ou atualiza o valor se a chave já existir.

| | |
|---|---|
| **Devolve** | nada |
| **Custo** | O(1) em média, O(n) no pior caso |
| **Efeito** | pode disparar redimensionamento se o fator de carga passar de 0.75 |

##### `remover(chave)`

Remove a chave e devolve o valor que estava guardado.

| | |
|---|---|
| **Devolve** | o valor removido |
| **Erro** | `KeyError` se a chave não existir |
| **Custo** | O(1) em média |

#### Métodos de leitura

##### `buscar(chave, padrao=None)`

| | |
|---|---|
| **Devolve** | o valor da chave, ou `padrao` se ela não existir |
| **Custo** | O(1) em média |

##### `chaves()` e `itens()`

Geradores que percorrem toda a tabela. `chaves()` devolve as chaves, `itens()`
devolve pares `(chave, valor)`. A ordem depende da distribuição interna e não é
a ordem de inserção.

| | |
|---|---|
| **Custo** | O(n + m), com m = número de baldes |

##### `fator_carga()`

Devolve `elementos / capacidade`. É o número que o redimensionamento vigia.

##### `custo_de_busca(chave)`

Quantos nós a busca precisaria examinar para responder sobre essa chave.

Existe para comparar esta estratégia com o endereçamento aberto, e é usado pelo
`ferramentas/benchmark_colisoes.py`. Não faz parte do funcionamento normal — é um método de
medição.

##### `estatisticas()`

Fotografia do estado interno. Devolve um dicionário:

```python
{
    "capacidade": 47,        # quantos baldes existem
    "elementos": 26,         # quantos pares estão guardados
    "fator_carga": 0.553,    # elementos / capacidade
    "baldes_ocupados": 20,
    "baldes_vazios": 27,
    "maior_corrente": 3,     # o número mais revelador
    "colisoes": 5,
}
```

`maior_corrente` é o que diz se a estrutura está saudável. Se ele crescer junto
com a quantidade de elementos, a função de dispersão está concentrando chaves e
a busca deixou de ser O(1) na prática.

#### Operadores suportados

```python
len(tabela)           # quantos elementos
"chave" in tabela     # se a chave existe
repr(tabela)          # "TabelaHash(elementos=26, capacidade=47)"
```

### Exemplo completo

```python
from catalogo.hashtable import TabelaHash

tabela = TabelaHash()
tabela.inserir("P001", {"nome": "Tênis azul"})
tabela.inserir("P002", {"nome": "Camisa branca"})

tabela.buscar("P001")              # {'nome': 'Tênis azul'}
tabela.buscar("P999")              # None
tabela.buscar("P999", "não achei") # 'não achei'

"P001" in tabela                   # True
len(tabela)                        # 2

tabela.remover("P001")             # {'nome': 'Tênis azul'}
tabela.estatisticas()["maior_corrente"]
```

### Como o redimensionamento funciona

Quando `fator_carga()` passa de `FATOR_CARGA_MAXIMO`, o método interno
`_redimensionar()` é chamado. Ele:

1. guarda o vetor antigo;
2. cria um vetor novo com o dobro da capacidade, arredondado para primo;
3. **reinsere** cada elemento, recalculando a posição.

A reinserção é obrigatória: a posição de uma chave é `hash % capacidade`, então
mudar a capacidade muda a posição. Copiar as correntes de lugar deixaria os
dados na memória mas a busca procurando no lugar errado.

---

## `catalogo/hashtable_aberta.py`

Mesma interface, estratégia diferente: **endereçamento aberto com sondagem
linear**. Achando a posição ocupada, procura a seguinte.

Não é usada pelo catálogo. Existe para a comparação do `ferramentas/benchmark_colisoes.py`.

### Constante do módulo

| nome | o que é |
|---|---|
| `REMOVIDO` | marcador de posição esvaziada (lápide) |

A lápide é o que torna esta estratégia mais complicada. A busca para quando
encontra uma posição vazia, porque vazia significa "não está aqui nem adiante".
Se a remoção esvaziasse de verdade, cortaria o caminho de sondagem e esconderia
as chaves que vieram depois. A lápide diz "aqui teve alguém, continue
procurando".

### `class TabelaHashAberta`

A interface pública é idêntica à `TabelaHash` — `inserir`, `buscar`, `remover`,
`fator_carga`, `custo_de_busca`, `chaves`, `itens`, `estatisticas`, `len()`,
`in`. As duas podem ser trocadas uma pela outra sem mudar mais nada, que é o que
torna a comparação honesta.

#### Diferenças no comportamento

**`fator_carga()` conta as lápides.** Elas ocupam posição e atrapalham a
sondagem, então entram na conta. Sem isso, uma tabela cheia de marcadores de
remoção pareceria vazia e nunca seria reorganizada.

**`estatisticas()` tem campos diferentes:**

```python
{
    "capacidade": 47,
    "elementos": 26,
    "fator_carga": 0.553,
    "lapides": 7,          # em vez de baldes_ocupados/vazios
    "maior_sondagem": 4,   # em vez de maior_corrente
    "colisoes": 5,
}
```

**`_redimensionar()` também limpa as lápides.** Elas só somem aqui, o que
significa que um uso com muitas remoções e poucas inserções pode ficar bastante
tempo com a tabela suja.

### Qual é mais rápida

Medido pelo `ferramentas/benchmark_colisoes.py`, comparações por busca:

| ocupação | encadeamento | endereçamento aberto |
|---|---|---|
| 0,1 | 1,00 | 1,01 |
| 0,5 | 1,17 | 4,60 |
| 0,95 | **1,28** | **61,68** |

O endereçamento aberto desanda por causa do agrupamento primário: uma chave
desviada ocupa a posição vizinha, que desvia a próxima, e o bloco cresce
sozinho. No encadeamento isso não acontece, porque baldes vizinhos são
independentes.

Em memória, o encadeamento gasta cerca de 8% a mais.
