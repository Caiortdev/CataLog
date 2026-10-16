# Referência — Geração de tags

Arquivos cobertos: `catalogo/tagger.py`, `catalogo/professor.py` e
`ia/ClassificaProduto.swift`.

É a camada que transforma "Tênis azul para corrida em asfalto" numa lista de
tags. Envolve duas fontes de conhecimento — o vocabulário escrito à mão e um
modelo de linguagem — e as regras que decidem quando usar cada uma.

---

## `catalogo/tagger.py`

### `class GeradorDeTags`

#### Construtor

```python
GeradorDeTags(entradas=VOCABULARIO, professor=None, ia_primeiro=False)
```

| parâmetro | o que é |
|---|---|
| `entradas` | a lista de termos a carregar; útil nos testes para passar um vocabulário pequeno e controlado |
| `professor` | instância de `Professor`, ou `None` para funcionar só com o vocabulário |
| `ia_primeiro` | se `True`, o modelo analisa **todo** produto; se `False`, só os que o vocabulário não identificou |

O vocabulário é carregado numa `TabelaHash` no construtor, uma vez só. Se fosse
percorrido como lista a cada palavra, o custo seria O(V) por palavra em vez de
O(1).

#### `gerar(nome, descricao="")`

O método principal. Devolve a lista de tags do produto, sem repetição.

```python
>>> g = GeradorDeTags()
>>> g.gerar("Tênis azul", "para corrida em asfalto")
['calcado', 'esporte', 'azul', 'cor', 'corrida', 'asfalto', 'rua']
```

**A ordem é a de descoberta no texto**, não alfabética. Como o nome vem antes da
descrição, as tags do nome aparecem primeiro — e o nome costuma ser mais
importante para quem procura.

**Com `ia_primeiro=True`**, a categoria vinda do modelo encabeça a lista:

```python
>>> g = GeradorDeTags(professor=Professor(), ia_primeiro=True)
>>> g.gerar("Tênis azul", "para corrida em asfalto")
['esporte', 'calcado', 'azul', 'cor', 'corrida', 'asfalto', 'rua']
#  ^^^^^^^ do modelo
```

#### `termos_conhecidos()`

Quantos termos o vocabulário tem. Usado na tela de estatísticas.

#### Métodos internos que vale conhecer

**`_sabe_o_que_e(tags)`** — decide se as tags já dizem *que coisa* o produto é.
Procura alguma tag que esteja em `CATEGORIAS`.

A distinção veio de um defeito: "Violão acústico com cordas de nylon" recebia as
tags `nylon` e `material`, isso contava como "já temos tags", e o modelo nunca
era consultado. O produto ficava sem nada dizendo que era um instrumento. O
critério antigo era "tem alguma tag"; hoje é "tem alguma **categoria**".

**`_buscar_no_vocabulario(palavra)`** — procura a palavra, e só se não achar
tenta a forma singular. A ordem importa: "tenis" está no vocabulário e é achado
de primeira, então nunca chega a ser singularizado para "teni".

---

## `catalogo/professor.py`

O módulo mais longo do projeto (531 linhas). Faz a ponte com o modelo de
linguagem e guarda o que ele ensina.

### Constantes

| nome | o que é |
|---|---|
| `CACHE` | caminho de `dados/aprendido.json` |
| `BINARIO` | caminho do executável Swift compilado |
| `FONTE_SWIFT` | caminho de `ia/ClassificaProduto.swift` |
| `DESCONHECIDA` | `"desconhecida"` — a recusa do modelo; nunca vira tag |
| `CATEGORIAS` | conjunto das 18 categorias válidas |
| `TEMPO_LIMITE` | `60` segundos por consulta |

> `CATEGORIAS` espelha o enum declarado no arquivo Swift. O teste
> `test_categorias_batem_com_o_enum_do_swift` lê o arquivo Swift e compara, para
> os dois lados não se separarem.

### Função do módulo

#### `palavra_principal(texto)`

Devolve a palavra que nomeia o produto — a primeira palavra significativa.

```python
>>> palavra_principal("Frigideira antiaderente de cerâmica")
'frigideira'
>>> palavra_principal("Guarda-chuva dobrável")
'guardachuva'
```

Funciona porque, em português, nome de produto começa pelo substantivo.

**Esta regra substituiu o modelo nessa tarefa.** Pedindo ao modelo que apontasse
a palavra principal, ele devolveu a frase inteira em 7 de 8 casos. A regra
acertou 16 de 16.

---

### `class Professor`

#### Construtor

```python
Professor(caminho_cache=CACHE, consultar_modelo=True, amostras=1)
```

| parâmetro | o que é |
|---|---|
| `caminho_cache` | onde fica o arquivo de aprendizado; os testes passam um temporário |
| `consultar_modelo` | `False` simula uma máquina sem Apple Intelligence |
| `amostras` | quantas vezes perguntar a mesma coisa para medir a firmeza da resposta |

#### `categoria_de(texto, usar_generalizacao=True)`

O método principal. Devolve a categoria do produto, ou `None`.

A ordem das tentativas vai do mais específico ao mais caro:

1. **a frase exata**, se já foi vista antes — O(1);
2. **a palavra** que nomeia o produto, se não for ambígua — O(1);
3. **o modelo**, que é a única etapa que custa tempo (~600 ms).

A frase vem antes da palavra porque é mais específica: uma correção feita à mão
precisa valer mesmo contra a regra genérica.

**Sobre `usar_generalizacao=False`:** pula a etapa 2 e vai direto ao modelo
quando a frase é nova. Parece desperdício e conserta um problema real — o atalho
responde antes de o modelo ser consultado, o que impede o sistema de descobrir
que o atalho está errado. Foi o que aconteceu com "jogo": o jogo de facas
ensinou que "jogo" é cozinha, e o jogo de chaves de fenda nunca chegou a ser
perguntado. Quem monta a base de aprendizado desliga o atalho.

#### `ensinar(texto, categoria)`

Grava uma categoria direto, sem perguntar ao modelo. É assim que uma pessoa
corrige o que ele errou.

| | |
|---|---|
| **Devolve** | `True` se algo mudou |
| **Efeito** | grava o arquivo e tira o produto da fila de revisão |

#### `marcar_revisado(texto)`

Tira um produto da fila de revisão sem mudar a categoria. Para quando a pessoa
olha e conclui que já estava certo.

#### `salvar()`

Grava o arquivo de aprendizado. É chamado automaticamente quando algo muda.

#### Propriedades de leitura

| propriedade | o que devolve |
|---|---|
| `aprendidos` | quantos produtos distintos já foram vistos |
| `palavras_aprendidas` | quantas palavras generalizam |
| `ambiguas` | lista de palavras que servem a mais de uma categoria |
| `para_revisar` | produtos cuja classificação o modelo deu de forma instável |
| `novidades` | quantas gravações aconteceram nesta execução |
| `avisos` | lista de mensagens acumuladas |
| `modelo_falhou` | se o modelo parou de responder |

> `avisos` e `modelo_falhou` são coisas diferentes. Descobrir que uma palavra é
> ambígua gera aviso e **não** é falha. Confundir os dois fez o script de
> povoamento parar na metade uma vez.

---

### O formato de `dados/aprendido.json`

```json
{
  "palavras": {
    "frigideira": "cozinha",
    "trena": "ferramenta"
  },
  "frases": {
    "jogo de chaves de fenda": "ferramenta",
    "jogo de facas de cozinha": "cozinha"
  },
  "ambiguas": ["jogo"],
  "revisar": ["tapete de sala antiderrapante"]
}
```

| seção | papel |
|---|---|
| `palavras` | o que generaliza — vale para qualquer produto que use a palavra |
| `frases` | o texto completo; tem precedência e é o recurso quando a palavra é ambígua |
| `ambiguas` | palavras que aparecem com mais de uma categoria |
| `revisar` | fila de trabalho humano |

**Na leitura, só `frases` é carregada.** As outras duas são derivadas dela. Ler
as três abriria espaço para o estado divergir — bastaria alguém corrigir uma
frase à mão e esquecer de ajustar a palavra.

**As chaves são renormalizadas ao ler.** Assim, qualquer ajuste futuro na
normalização migra o arquivo sozinho.

---

## `ia/ClassificaProduto.swift`

O programa que conversa com o modelo. Existe em Swift porque o framework
FoundationModels, que dá acesso ao Apple Intelligence, não tem interface Python.

### Protocolo

```
entrada:  uma linha de texto por produto, em stdin
saída:    uma linha JSON por produto, em stdout
```

```bash
$ echo "Guarda-chuva dobravel" | ./ia/classifica-produto
{"categoria":"acessorio"}
```

Com `--amostras N`, devolve também as respostas de N consultas extras:

```bash
$ echo "Colchao de solteiro" | ./ia/classifica-produto --amostras 3
{"categoria":"acessorio","amostras":["decoracao","movel","cozinha"]}
```

Em caso de problema: `{"erro": "descrição do que houve"}`.

### Compilação

```bash
swiftc -O ia/ClassificaProduto.swift -o ia/classifica-produto
```

Não é preciso fazer isso à mão — o `Professor` compila sozinho na primeira vez.
O binário não é versionado: executável de uma máquina pode não rodar em outra.

### Três decisões do programa

**A resposta é um enum, não uma string.** Pedindo texto livre, o modelo devolvia
`calcado` para um produto e `calcados` para outro — duas chaves sem relação para
a tabela hash. Declarando a resposta como um conjunto fechado, ele fica
estruturalmente incapaz de inventar uma variação.

**Temperatura zero.** Sem isso, a mesma entrada gerava saídas diferentes a cada
execução, e uma delas inventou a tag `esportividade`.

**Uma sessão por produto.** Reaproveitar a sessão faz o histórico crescer até
estourar a janela de contexto — vimos o erro "4091 de 4096 tokens" num texto de
dez palavras.

### Requisitos

| | |
|---|---|
| Sistema | macOS 26 ou mais novo |
| Processador | Apple Silicon |
| Ajuste | Apple Intelligence ligado nos Ajustes |
| Ferramenta | Xcode ou as ferramentas de linha de comando |

Faltando qualquer um, o programa devolve `{"erro": ...}` explicando qual, e o
sistema segue com o vocabulário.
