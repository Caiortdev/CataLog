# Referência — Catálogo

Arquivos cobertos: `catalogo/produto.py`, `catalogo/catalogo.py` e
`catalogo/inferencia.py`.

É onde as três tabelas hash se encontram e onde as buscas acontecem.

---

## `catalogo/produto.py`

### `class Produto`

Agrupamento de dados, sem lógica.

```python
Produto(identificador, nome, descricao, tags)
```

| atributo | tipo | exemplo |
|---|---|---|
| `identificador` | `str` | `"P001"` |
| `nome` | `str` | `"Tênis azul"` |
| `descricao` | `str` | `"para corrida em asfalto"` |
| `tags` | `list[str]` | `["calcado", "esporte", "azul"]` |

#### `resumo()`

Uma linha legível, usada pelo menu:

```python
>>> produto.resumo()
'[P001] Tênis azul — calcado, esporte, azul, cor, corrida'
```

**O produto não sabe gerar as próprias tags**, e isso é intencional. Quem gera é
o `GeradorDeTags`, quem guarda é o `Catalogo`. Se o produto fizesse as três
coisas, trocar a estratégia de tags obrigaria a mexer na classe de dados.

Não é uma `dataclass` de propósito — o `__init__` escrito à mão deixa explícito
o que cada campo é.

---

## `catalogo/catalogo.py`

### `class Catalogo`

#### Construtor

```python
Catalogo(gerador_de_tags=None)
```

Sem argumento, cria um `GeradorDeTags()` padrão (só vocabulário).

#### As três tabelas

| atributo | chave | valor | responde a |
|---|---|---|---|
| `_produtos` | identificador | o `Produto` | "me mostre o P007" |
| `_indice_tags` | tag | lista de identificadores | "quais produtos são calçados?" |
| `_indice_texto` | palavra do texto | lista de identificadores | "quais produtos falam em cerâmica?" |

As duas últimas são **índices invertidos**: a chave deixou de ser o produto e
passou a ser aquilo por que se procura.

A diferença entre elas: o índice de tags é **semântico** — `tenis` vira
`calcado`, palavra que não está escrita em lugar nenhum. O índice de texto é
**literal** — guarda exatamente o que foi digitado. Nenhum encontra o que o
outro encontra.

#### `cadastrar(nome, descricao="")`

```python
>>> produto = catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
>>> produto.identificador
'P001'
```

| | |
|---|---|
| **Devolve** | o `Produto` criado |
| **Erro** | `ValueError` se o nome for vazio ou só espaços |
| **Custo** | O(t), com t = número de tags (um punhado) |

A ordem interna importa: gera o identificador, gera as tags, insere nas três
tabelas. As tags precisam existir antes de poderem ser indexadas.

#### `remover(identificador)`

```python
>>> catalogo.remover("P001")
Produto(P001, 'Tênis azul')
```

| | |
|---|---|
| **Devolve** | o `Produto` removido |
| **Erro** | `KeyError` se não existir |

**Limpa as três tabelas.** Esquecer os índices deixaria identificadores órfãos
apontando para um produto que não existe mais, e a busca quebraria depois —
longe de onde o erro foi cometido. Tags que ficam sem nenhum produto saem do
índice.

#### Os cinco jeitos de buscar

##### `obter(identificador)`

Busca direta pelo código. Devolve o `Produto` ou `None`. O(1).

##### `buscar_por_tag(tag)`

Produtos que têm a tag. O termo é normalizado, então `CALÇADO`, `calçado` e
`calcado` acham a mesma coisa.

```python
>>> catalogo.buscar_por_tag("calcado")
[Produto(P001, 'Tênis azul'), Produto(P004, 'Chuteira preta')]
```

| | |
|---|---|
| **Devolve** | lista de `Produto`, vazia se a tag não existir |
| **Custo** | O(1) para achar a lista, mais O(k) para montar o resultado |

Não há laço sobre o catálogo. Ter 10 ou 10 milhões de produtos não muda o tempo
de localizar a lista.

##### `buscar_por_tags(tags)`

Produtos que têm **todas** as tags — filtro, não soma.

```python
>>> catalogo.buscar_por_tags(["azul", "calcado"])
[Produto(P001, 'Tênis azul')]
```

Duas otimizações emprestadas de motores de busca: se qualquer tag não existe, o
resultado é vazio e devolve na hora; e a busca começa pela tag mais rara, porque
procurar "azul" dentro dos resultados de "natacao" é mais barato que o
contrário.

##### `buscar_por_palavra(palavra)`

Produtos cujo texto contém literalmente essa palavra.

```python
>>> catalogo.buscar_por_palavra("ceramica")
[Produto(P007, 'Frigideira antiaderente')]
```

Complementa a busca por tag. A frigideira pode ter só a tag `cozinha`, mas
"cerâmica" está escrita nela.

##### `buscar_por_texto(texto)`

Busca escrevendo uma frase. A frase passa pelo **mesmo gerador de tags** usado
no cadastro — é o que faz os dois lados falarem a mesma língua.

```python
>>> catalogo.buscar_por_texto("tenis para corrida")
[Produto(P001, 'Tênis azul')]
```

#### Listagens

| método | devolve |
|---|---|
| `todos()` | todos os produtos — O(n), inevitável aqui |
| `tags_conhecidas()` | as tags em uso, ordenadas |
| `palavras_indexadas()` | as palavras do índice literal, ordenadas |

#### `estatisticas()`

```python
{
    "produtos": {...},          # estatisticas() da tabela de produtos
    "indice_de_tags": {...},    # idem
    "indice_de_texto": {...},   # idem
    "termos_no_vocabulario": 76,
}
```

Cada bloco interno tem o formato descrito na
[referência 01](01-estruturas-de-dados.md).

### Exemplo completo

```python
from catalogo.catalogo import Catalogo

catalogo = Catalogo()
catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
catalogo.cadastrar("Camisa azul", "de algodão")

catalogo.buscar_por_tag("azul")          # os dois
catalogo.buscar_por_tags(["azul", "calcado"])  # só o tênis
catalogo.buscar_por_palavra("algodao")   # só a camisa
len(catalogo)                            # 2
```

---

## `catalogo/inferencia.py`

A única parte do projeto que aprende **sem consultar nada** — nem modelo, nem
internet, nem vocabulário. Usa só os dois índices invertidos que o catálogo já
mantém.

### Constante

| nome | valor | o que é |
|---|---|---|
| `MINIMO_DE_PRODUTOS` | `3` | quantos produtos precisam concordar para a regra ser proposta |

Com dois produtos qualquer coincidência vira "regra": dois tênis azuis bastariam
para o sistema concluir que "tenis" significa "azul".

### `inferir_regras(catalogo, minimo=3, ignorar_conhecidas=True)`

Propõe regras "palavra → tag" olhando o catálogo.

```python
>>> inferir_regras(catalogo)
[('inox', 'cozinha', 3)]
```

| | |
|---|---|
| **Devolve** | lista de `(palavra, tag, quantidade)`, da sugestão mais sustentada para a menos |
| `minimo` | quantos produtos precisam concordar |
| `ignorar_conhecidas` | omite palavras que o vocabulário já tem |

**O critério é rígido:** a tag precisa estar em **todos** os produtos que contêm
a palavra, não na maioria. Uma regra que vale em nove de dez casos não é regra —
é um palpite que vai errar o décimo em silêncio.

**E ela erra pelo mesmo motivo que o modelo.** O primeiro teste real sugeriu
`inox → cozinha` com três produtos concordando. A regra é ruim: inox é material,
e um parafuso de inox não é cozinha. Os três produtos eram todos de cozinha,
então qualquer palavra comum viraria "cozinha".

A diferença é que a evidência fica à vista e **nada é gravado**. A pessoa
decide.

### `formatar(sugestoes)`

Transforma as sugestões em linhas prontas para o terminal, já no formato que se
cola no `vocabulario.py`:

```
  ("inox", ("cozinha",)),   # 3 produtos concordam
```

### `termos_do_vocabulario()`

Conjunto das palavras que o vocabulário já conhece, normalizadas. Usado para
filtrar sugestões óbvias.
