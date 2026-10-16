# Roteiro da apresentação — passo a passo

Siga de cima para baixo. Cada passo tem o comando exato e o que falar.

---

## As três frases que você vai usar

Deixe esta parte aberta no celular ou impressa. São só estas três, na ordem:

| # | Nome do produto | Descrição | Para que serve |
|---|---|---|---|
| 1 | `Tênis azul` | `para corrida em asfalto` | É o exemplo exato do slide |
| 2 | `Churrasqueira eletrica` | `portatil com tampa de vidro` | Nenhuma palavra está no vocabulário — a IA resolve sozinha |
| 3 | `Mesa de jantar` | `em madeira macica para seis lugares` | Idem, e deixa a palavra "madeira" para buscar depois |

> **Importante:** digite sem acento no nome dos produtos 2 e 3, exatamente como
> está na tabela. O sistema funciona com acento também, mas assim você evita
> errar a digitação na frente de todo mundo.

---

## Antes de entrar na sala

### 1. Teste se está tudo funcionando

```bash
cd /Users/caiotorres/P-SOFTWARES/FACULADE/CataLog
```

```bash
python3 -m unittest discover -s testes -t .
```

Tem que aparecer **OK** no final. Se aparecer FAILED, não apresente antes de ver o que é.

### 2. Se você ensaiou antes, rode isto

Quando você testa uma frase, o sistema **aprende** e não pergunta mais à IA.
Se ensaiar com as três frases acima, na hora da apresentação a IA não vai ser
acionada e você perde a melhor parte.

Este comando apaga o aprendizado e reconstrói só com os produtos oficiais
(demora uns 30 segundos):

```bash
rm dados/aprendido.json && python3 ferramentas/povoar_aprendizado.py
```

### 3. Deixe duas abas de terminal abertas

Uma para o programa, outra para os benchmarks. Trocar de aba é mais rápido e
menos arriscado que digitar comando na frente da turma.

### 4. Aumente a fonte do terminal

As tabelas dos benchmarks têm colunas. Se não couberem na largura da tela, elas
quebram e ficam ilegíveis.

---

## PARTE 1 — Abrir o programa (3 min)

### Passo 1. Rode o programa

```bash
python3 main.py --ia
```

Vai aparecer:

```
Gerando tags por: modelo local da Apple (categoria) + vocabulário (cor, material, uso)
```

**Fale:** *"O sistema usa um modelo de inteligência artificial que roda dentro
do próprio Mac. Sem internet, sem chave de API, sem custo."*

---

### Passo 2. Carregue os produtos de exemplo

Digite: **`8`** e aperte Enter.

Aparecem 6 produtos já com tags.

**Fale:** *"Ninguém digitou nenhuma dessas tags. O sistema leu o texto e
decidiu sozinho."*

---

### Passo 3. Cadastre a FRASE 1 (o exemplo do slide)

Digite: **`1`** e Enter.

| o que o programa pergunta | o que você digita |
|---|---|
| Nome do produto | `Tênis azul` |
| Descrição | `para corrida em asfalto` |

Vai aparecer:

```
Cadastrado: [P007] Tênis azul — esporte, calcado, azul, cor, corrida, asfalto, rua
```

**Fale:** *"Esse é o exemplo exato do enunciado. Ele pedia as tags calçado,
esporte, corrida e azul — as quatro estão aqui, mais três que o sistema deduziu
sozinho."*

---

### Passo 4. Cadastre a FRASE 2 (a IA trabalhando)

Digite: **`1`** e Enter.

| o que o programa pergunta | o que você digita |
|---|---|
| Nome do produto | `Churrasqueira eletrica` |
| Descrição | `portatil com tampa de vidro` |

Vai demorar meio segundo e aparecer:

```
Cadastrado: [P008] Churrasqueira eletrica — cozinha
```

**Fale:** *"Nenhuma dessas palavras está no vocabulário do sistema. Quem
classificou foi a inteligência artificial, agora, offline."*

---

### Passo 5. Cadastre a FRASE 3

Digite: **`1`** e Enter.

| o que o programa pergunta | o que você digita |
|---|---|
| Nome do produto | `Mesa de jantar` |
| Descrição | `em madeira macica para seis lugares` |

```
Cadastrado: [P009] Mesa de jantar — movel
```

---

## PARTE 2 — Mostrar as buscas (3 min)

### Passo 6. Busque por uma tag

Digite: **`3`** e Enter. Depois digite: **`esporte`** e Enter.

Aparecem **4 produtos**: dois tênis, uma chuteira e o tênis que você acabou de
cadastrar.

**Fale:** *"Repare que estou buscando por característica, não por nome. É o item
4 do enunciado."*

---

### Passo 7. Busque uma palavra que NÃO é tag

Digite: **`A`** e Enter. Depois digite: **`madeira`** e Enter.

Aparece **1 produto**: a mesa de jantar.

**Fale:** *"A mesa só tem a tag 'móvel'. A palavra madeira não é tag de nada —
mas está escrita no texto. São dois índices diferentes: um busca por
significado, o outro por palavra escrita. Nenhum dos dois acha o que o outro
acha."*

---

### Passo 8. Abra o estado interno das tabelas

Digite: **`7`** e Enter.

Deixe na tela enquanto fala. Aponte para a parte do **ÍNDICE DE TAGS**:

```
ÍNDICE DE TAGS (semântico)
  capacidade (baldes)...: 47
  elementos guardados...: 26
  maior corrente........: 3
  colisões registradas..: 5
```

**Fale:** *"Aqui dá para ver a estrutura funcionando por dentro. Houve 5
colisões: cinco vezes em que duas tags diferentes foram parar na mesma posição.
A maior corrente é 3, ou seja, no pior caso a busca compara 3 itens em vez de
26."*

**Se perguntarem quais colidiram:** `corrida`, `cozinha` e `trilha` caíram todas
no balde 41.

---

### Passo 9. Saia do programa

Digite: **`0`** e Enter.

---

## PARTE 3 — Os números (4 min)

### Passo 10. Por que o índice invertido

```bash
python3 ferramentas/benchmark.py
```

Espere uns 20 segundos. Aponte para a última linha da tabela:

```
50000 | 500 | 0.27 ms | 12.15 ms | 45x
```

**Fale:** *"Com 50 mil produtos, buscar pelo índice é 45 vezes mais rápido que
percorrer o catálogo. E o que importa não é o número: é que a coluna da
varredura cresce junto com o catálogo, e a do índice não."*

---

### Passo 11. Por que encadeamento (a parte mais forte)

```bash
python3 ferramentas/benchmark_colisoes.py
```

Role até o **experimento 5**, no final:

```
 ocupação   encadeamento   endereç. aberto
      0.1          1.00              1.01
      0.5          1.17              4.60
     0.95          1.28             61.68
```

**Fale:** *"Implementei as duas estratégias de tratar colisão. Com a tabela
vazia elas empatam. Conforme enche, a que escolhi quase não se mexe e a outra
vai para 62 comparações por busca. Quarenta e oito vezes pior."*

---

### Passo 12. Admita o erro (vale a nota)

Role para cima até o **experimento 3**:

```
encadeamento     antes: 1.21  depois: 1.21
endereç. aberto  antes: 3.33  depois: 3.33
```

**Fale:** *"Eu tinha escrito na documentação que a outra estratégia piora com
muitas remoções. Implementei, fiz vinte mil ciclos de remoção para comprovar, e
o desempenho não piorou nada. Eu tinha repetido teoria sem verificar. O motivo
real da desvantagem era outro, e corrigi o documento deixando registrado o que
eu havia escrito antes."*

Se der tempo, abra o arquivo e mostre:

```bash
open docs/01-tabela-hash.md
```

---

## PARTE 4 — Fechamento (1 min)

**Fale:** *"São 123 testes automatizados, e a maior parte deles nasceu de um
defeito real, não de caso imaginado. Uma chuteira que saía sem cor, uma palavra
de ligação virando tag, um violão classificado só pelo material das cordas."*

E termine com:

> *"A conclusão que eu levo é que medir mudou decisões. Duas afirmações que eu
> tinha escrito como verdade estavam erradas, e só apareceram porque implementei
> a alternativa e comparei."*

---

## Se algo der errado

**O modelo não responde / dá erro**
Saia com `0`, rode `python3 main.py` (sem o `--ia`) e diga: *"Sem a IA o sistema
funciona com o vocabulário e com tudo que já aprendeu antes, porque isso fica
gravado em arquivo."* Tudo continua funcionando.

**A IA demora muito**
É normal até 1 segundo por produto. Fale enquanto espera.

**Cadastrou errado**
Digite `9`, depois o código do produto (ex: `P008`), e cadastre de novo.

**Travou**
`Ctrl+C` e rode `python3 main.py --ia` de novo. Você perde os produtos
cadastrados, mas não o aprendizado da IA.

---

## Perguntas prováveis

**"Por que não usou o dicionário pronto do Python?"**
Porque ele já é uma tabela hash escondida. Usá-lo entregaria o uso da estrutura,
não a estrutura — função de dispersão, colisão e redimensionamento ficariam
invisíveis.

**"Por que a tag é 'calcado' e não 'calçado'?"**
Porque a tag é chave de hash, e hash exige igualdade exata. Guardo na forma
canônica e normalizo a busca. Digitar `CALÇADO`, `calçado` ou `calcado` acha o
mesmo produto — posso demonstrar.

**"Isso roda na minha máquina?"**
Sem o `--ia`, roda em qualquer lugar que tenha Python 3, sem instalar nada. O
modo com IA precisa de Mac com chip Apple. Mas o que a IA já aprendeu vai junto
no arquivo, então a busca continua funcionando.

**"Qual a complexidade?"**
Busca e inserção são O(1) no caso médio e O(n) no pior, quando todas as chaves
caem no mesmo balde. A busca por tag é O(1) para achar a lista mais O(k) para
montar o resultado.

**"E se duas chaves colidirem?"**
Elas convivem. Cada balde guarda uma lista encadeada e a busca percorre a
corrente. Posso mostrar: na opção 7, `corrida`, `cozinha` e `trilha` estão todas
no mesmo balde.

---

## Resumo de uma página

```
PREPARAÇÃO    rm dados/aprendido.json && python3 ferramentas/povoar_aprendizado.py
              python3 -m unittest discover -s testes -t .

PROGRAMA      python3 main.py --ia
   8          carregar exemplos
   1          Tênis azul / para corrida em asfalto
   1          Churrasqueira eletrica / portatil com tampa de vidro
   1          Mesa de jantar / em madeira macica para seis lugares
   3          buscar tag:     esporte
   A          buscar palavra: madeira
   7          ver as tabelas por dentro
   0          sair

NÚMEROS       python3 ferramentas/benchmark.py
              python3 ferramentas/benchmark_colisoes.py
```
