# Complexidade

Documento 4 de 5. O custo de cada operação, por que o caso médio e o pior caso
são tão diferentes, e os tempos medidos de verdade.

## Tabela de custos

Na notação, `n` é a quantidade de produtos no catálogo, `t` é a quantidade de
tags de um produto (menos de dez, na prática) e `k` é a quantidade de produtos
que uma busca encontrou.

| Operação | Caso médio | Pior caso | Por quê |
|---|---|---|---|
| `inserir` na tabela hash | O(1) | O(n) | Média: calcula o balde e insere na frente da corrente. Pior: todas as chaves caíram no mesmo balde e a corrente tem n elementos |
| `buscar` na tabela hash | O(1) | O(n) | Mesmo raciocínio: percorre só a corrente do balde |
| `remover` na tabela hash | O(1) | O(n) | Idem, mais o religamento de dois ponteiros |
| `cadastrar` produto | O(t) | O(n·t) | Uma inserção na tabela de produtos e t inserções no índice |
| `obter` por identificador | O(1) | O(n) | Uma consulta direta |
| `buscar_por_tag` | O(k) | O(n) | O(1) para achar a lista, mais O(k) para montar o resultado |
| `buscar_por_tags` | O(k·m) | O(n·m) | k = tamanho da menor lista, m = quantidade de tags |
| `todos` | O(n) | O(n) | Percorre tudo mesmo; aqui não tem como escapar |
| redimensionar | O(n) | O(n) | Reinsere todos os elementos |

## Por que "médio" e não "garantido"

A tabela hash não promete O(1) sempre. Ela promete O(1) **em média**, com duas
condições:

1. a função de dispersão espalha bem as chaves;
2. o fator de carga fica baixo.

Se as duas valerem, cada corrente tem um ou dois elementos e percorrê-la é
praticamente instantâneo. Se qualquer uma falhar, as correntes crescem e a
tabela degrada até virar uma lista encadeada comum, com busca O(n).

É por isso que `estatisticas()` reporta a **maior corrente**. Esse número é o
termômetro: enquanto ele ficar pequeno, o O(1) médio está valendo. Nos testes
com 300 produtos, ele fica abaixo de 10.

### O caso em que a hash é derrotada

Vale saber que existe um cenário onde a tabela hash perde feio. Se alguém
souber qual função de dispersão você usa, pode construir milhares de chaves que
caem todas no mesmo balde de propósito. Todas as buscas viram O(n), e um serviço
que atendia milhões de requisições trava.

Esse ataque tem nome (*hash flooding*) e foi justamente o motivo de o Python
passar a aleatorizar o `hash()` de strings a partir da versão 3.3 — a mesma
aleatorização que nos obrigou a escrever a nossa própria função determinística
(documento 1). Num trabalho acadêmico isso não é um risco; num sistema exposto
à internet, seria.

### Redimensionamento e análise amortizada

Redimensionar custa O(n), e isso parece contradizer a promessa de inserção O(1).
Não contradiz, por dois motivos somados:

- acontece raramente, só quando o fator de carga passa de 0.75;
- a cada vez a capacidade dobra, então a próxima vez demora o dobro para chegar.

Inserindo n elementos do zero, o custo total de todos os redimensionamentos
somados é proporcional a n, não a n². Dividindo esse total pelas n inserções, dá
uma constante. Esse é o argumento da **análise amortizada**: não é que nenhuma
inserção seja cara, é que as poucas caras são diluídas entre muitas baratas.

## Os números medidos

Teoria é uma coisa; cronômetro é outra. O `ferramentas/benchmark.py` roda a busca com índice
e a busca por varredura no mesmo catálogo, procurando a tag `natacao`, que
aparece em 1% dos produtos.

```bash
python3 ferramentas/benchmark.py
```

Resultado em uma execução (média de 50 repetições cada):

| produtos | achados | com índice | varrendo tudo | diferença |
|---|---|---|---|---|
| 1.000 | 10 | 0,0064 ms | 0,1068 ms | 17x |
| 10.000 | 100 | 0,0485 ms | 1,1864 ms | 24x |
| 50.000 | 500 | 0,2524 ms | 6,9132 ms | 27x |

### Lendo os números com honestidade

A leitura preguiçosa seria "o índice é O(1), então o tempo dele deveria ser
constante". Mas ele não é constante: subiu de 0,0064 para 0,2524 ms. Ignorar
isso seria esconder um dado que não combina com a narrativa.

A explicação está na coluna que quase ninguém olha. O número de produtos
**encontrados** também cresceu: 10, depois 100, depois 500. A busca não só
localiza a lista, ela monta o resultado com todos os produtos achados — e isso é
o O(k) da tabela de custos.

Dividindo o tempo pelo número de achados:

| produtos | tempo por produto encontrado |
|---|---|
| 1.000 | 0,00064 ms |
| 10.000 | 0,00049 ms |
| 50.000 | 0,00050 ms |

Praticamente constante, mesmo com o catálogo crescendo 50 vezes. **O custo da
busca com índice depende de quantos produtos ela encontra, não de quantos
existem.** É isso que O(1) + O(k) significa na prática.

A mesma conta do outro lado confirma o O(n):

| produtos | tempo por produto do catálogo |
|---|---|
| 1.000 | 0,000107 ms |
| 10.000 | 0,000119 ms |
| 50.000 | 0,000138 ms |

Também praticamente constante — mas aqui a constante multiplica o **tamanho do
catálogo**. Por isso essa coluna cresce e a outra não.

### O que isso significa na escala real

Com 50 mil produtos a diferença é de 7 milissegundos, que ninguém percebe. A
questão é a direção da curva.

A varredura cresce em linha reta com o catálogo. Multiplicando por 20, para um
milhão de produtos, seriam cerca de 140 ms por busca. Multiplicando pelos
milhares de buscas simultâneas de um e-commerce de verdade, o servidor não
aguenta. A busca com índice, no mesmo cenário, continuaria dependendo apenas de
quantos produtos atendem ao filtro.

Esse é o argumento central do trabalho, e ele agora tem número medido por trás,
não só notação.

## Como reproduzir

```bash
python3 ferramentas/benchmark.py
```

Os tempos absolutos vão variar de máquina para máquina. O que não varia é o
formato: a coluna da varredura cresce proporcionalmente ao catálogo, a do índice
acompanha apenas a quantidade de produtos encontrados.
