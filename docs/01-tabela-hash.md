# A tabela hash

Documento 1 de 5. Trata da estrutura em si: por que ela existe, como a função de
dispersão funciona, o que acontece quando duas chaves brigam pelo mesmo lugar e
por que a tabela precisa crescer sozinha.

Código correspondente: `catalogo/hashtable.py`.

## O problema que ela resolve

Imagine o catálogo guardado em uma lista comum. Para achar o produto P347, o
computador começa no primeiro item e vai conferindo um por um até encontrar.
Com 10 produtos, tudo bem. Com 100 mil, são 100 mil comparações no pior caso.
Esse é o custo O(n): o tempo cresce junto com a quantidade de dados.

Dá para melhorar mantendo a lista ordenada e usando busca binária, que cai para
O(log n). Melhor, mas ainda depende do tamanho. E tem um custo escondido:
manter a ordem na hora de inserir exige empurrar elementos de lugar.

A tabela hash ataca o problema por outro ângulo. Em vez de procurar onde o
produto está, ela **calcula** onde ele deveria estar. Se existe uma conta que
transforma "P347" diretamente na posição 12 do vetor, não há procura nenhuma:
é um acesso direto, e o tempo não depende de ter 10 ou 10 milhões de produtos.

Essa conta é a função de dispersão, e é o coração de tudo.

## A função de dispersão

A função precisa pegar uma chave de tamanho qualquer (uma string) e devolver um
número. Usamos a djb2, criada por Daniel J. Bernstein:

```python
def hash_djb2(texto):
    h = 5381
    for caractere in texto:
        h = (h * 33 + ord(caractere)) & 0xFFFFFFFF
    return h
```

Ela percorre a string acumulando um número. A cada caractere, multiplica o
acumulado por 33 (embaralhando o que já tinha) e soma o código do caractere
novo. É isso.

Os valores 33 e 5381 não têm demonstração matemática elegante por trás. Foram
escolhidos empiricamente porque, testados com strings reais, espalham bem.
Admitir isso é mais honesto do que inventar uma justificativa: boa parte das
funções de dispersão usadas no mundo real tem essa mesma origem experimental.

O `& 0xFFFFFFFF` corta o resultado em 32 bits. Em C isso aconteceria sozinho,
por estouro do inteiro. Em Python os inteiros crescem sem limite, então sem esse
corte o número ficaria enorme e as multiplicações iriam ficando lentas a cada
caractere.

O número devolvido ainda é grande demais para ser uma posição do vetor. O resto
da divisão pela capacidade resolve: `hash % capacidade` sempre cai entre 0 e
capacidade-1.

### Por que não usar a função `hash()` que o Python já tem

Dois motivos, e o segundo surpreende.

O primeiro é o óbvio: a disciplina pede para implementar a estrutura, e usar a
função pronta esconde justamente o que está sendo estudado.

O segundo é prático. Desde o Python 3.3, o `hash()` de strings é **aleatorizado
a cada execução do interpretador**. Isso é uma proteção de segurança: sem ela,
alguém mal-intencionado poderia enviar milhares de chaves escolhidas a dedo para
cair todas no mesmo balde e derrubar o servidor. O efeito colateral é que
`hash("tenis")` devolve um número diferente cada vez que você roda o programa.
O produto cairia em um balde diferente a cada execução, e seria impossível
escrever um teste que verifica distribuição, ou demonstrar em sala que a chave X
vai para o balde Y.

Dá para conferir isso no terminal:

```bash
python3 -c "print(hash('tenis'))"
```

Rode duas vezes: dois números diferentes. A nossa função devolve sempre o mesmo.

### Por que a capacidade é sempre um número primo

A posição final é `hash % capacidade`. Se a capacidade for 12, por exemplo, e os
valores de hash tenderem a ser múltiplos de 4 (coisa que acontece quando as
chaves seguem um padrão), os restos só cairão em 0, 4 e 8. Oito dos doze baldes
ficariam vazios para sempre, e as chaves se amontoariam nos três restantes.

Um número primo não compartilha fatores com quase nada, então ele quebra esses
padrões e espalha os restos por toda a tabela. Por isso `_proximo_primo` existe,
e por isso a capacidade pula de 11 para 23, 47, 97, e não de 10 para 20, 40.

Isso é a teoria. Medindo, com as mesmas 5000 chaves em duas capacidades quase
iguais (`python3 ferramentas/benchmark_colisoes.py`):

| capacidade | baldes usados | baldes vazios | maior balde |
|---|---|---|---|
| 1024 (potência de dois) | 708 | 316 | 21 |
| 1031 (primo) | 1031 | 0 | 12 |

A diferença é maior do que a teoria sugeria. Com potência de dois, **31% dos
baldes nunca são usados** — eles existem, ocupam memória, e nenhuma chave cai
neles. As chaves se amontoam nos 69% restantes, e o maior balde fica quase o
dobro do tamanho.

O motivo é a nossa própria função de dispersão. A djb2 multiplica por 33 a cada
caractere, e `% 1024` só enxerga os dez bits mais baixos do resultado — que
carregam pouca variedade. O primo força a conta a depender do número inteiro.

## Colisões

Duas chaves diferentes podem cair no mesmo balde. Isso não é falha da função:
é matematicamente inevitável. Existem infinitas strings possíveis e um número
finito de baldes, então necessariamente várias strings vão para o mesmo lugar.
É o princípio da casa dos pombos.

A pergunta certa não é "como evitar colisões", é "o que fazer quando elas
acontecem". Existem duas famílias de resposta.

**Endereçamento aberto.** Deu colisão, procura outro balde livre (o próximo, ou
um calculado por outra fórmula). A tabela fica compacta, só com o vetor, sem
estruturas extras. Em troca, remover vira um problema sério: se você simplesmente
esvaziar um balde do meio de uma sequência de desvios, as buscas que dependiam
de passar por ali param de achar o que vinha depois. A solução é marcar a célula
como "apagada" em vez de vazia, e esses marcadores vão se acumulando e
degradando o desempenho. Além disso, a tabela tem um limite rígido: não cabe
mais elemento do que baldes.

**Encadeamento separado.** Cada balde guarda o início de uma lista encadeada.
Deu colisão, pendura o novo elemento na corrente. Foi o que escolhemos.

A escolha se justifica pelo uso: um catálogo de e-commerce tem produtos entrando
e saindo o tempo todo, e no encadeamento remover é só religar dois ponteiros.
A tabela também nunca "enche" — ela degrada suavemente conforme as correntes
crescem, em vez de travar.

### O que a medição mostrou, e onde este documento estava errado

A versão anterior deste texto dizia que o endereçamento aberto perde porque
"degrada com muitas remoções". Implementamos a alternativa
(`catalogo/hashtable_aberta.py`) e medimos. **A afirmação não se confirmou:**
depois de 20 mil ciclos de remoção e inserção, o custo de busca do
endereçamento aberto não subiu — ficou em 3,33 comparações antes e depois.

O que a medição mostrou é que ele já começava pior, e o motivo é outro:

| ocupação | encadeamento | endereçamento aberto |
|---|---|---|
| 0,1 | 1,00 | 1,01 |
| 0,5 | 1,17 | 4,60 |
| 0,8 | 1,20 | 22,01 |
| 0,95 | 1,28 | **61,68** |

Com a tabela quase cheia, cada busca no endereçamento aberto custa 62
comparações, contra 1,28 do encadeamento — quase cinquenta vezes mais.

O nome disso é **agrupamento primário**, e é consequência da sondagem linear.
Quando uma chave é desviada, ela ocupa a posição vizinha; a próxima chave que
quiser aquela posição também será desviada, e o bloco cresce. Blocos maiores
capturam mais chaves, que fazem os blocos crescerem mais. A desvantagem se
alimenta sozinha.

No encadeamento isso não acontece, e é essa a vantagem real: uma corrente longa
não contamina os baldes vizinhos, porque eles são independentes. Por isso a
curva dele é quase plana.

Sobre memória, a diferença é menor do que se costuma dizer: com 10 mil
elementos, o encadeamento mantém 55.717 referências contra 51.434 do
endereçamento aberto. **Oito por cento a mais de memória em troca de buscas
quase três vezes mais baratas** — e a vantagem aumenta conforme a tabela
enche.

```
índice 0  -> None
índice 1  -> ["azul" -> [P001, P003]] -> ["corrida" -> [P001]] -> None
índice 2  -> None
índice 3  -> ["calcado" -> [P001]] -> None
```

No índice 1, duas tags diferentes convivem porque a busca percorre a corrente
comparando a chave de cada nó.

Aqui aparece a parte sutil: a tabela hash **não elimina** a busca linear, ela a
reduz a um pedaço minúsculo. Em vez de varrer 100 mil produtos, você varre uma
corrente de dois ou três. O que garante que a corrente fique curta é o fator de
carga.

### Por que uma lista encadeada de verdade, e não uma lista do Python

Guardar uma `list` dentro de cada balde daria o mesmo resultado e seria menos
código. Mas uma lista do Python é um vetor dinâmico, não uma lista encadeada:
ela reserva memória contígua e redimensiona quando enche. O comportamento de
memória é diferente, e o encadeamento — que é conteúdo da disciplina — ficaria
escondido atrás da implementação do Python. Por isso a classe `_No` existe, com
seu campo `proximo` apontando para o próximo elo.

## Fator de carga e redimensionamento

O fator de carga é a conta mais simples do projeto:

```
fator de carga = elementos guardados / quantidade de baldes
```

Ele diz o tamanho médio das correntes. Com fator 0.5, metade dos baldes tem um
elemento. Com fator 5, as correntes têm cinco elementos em média, e cada busca
faz cinco comparações — a tabela está virando uma lista comum.

Adotamos o limite de 0.75, que é o mesmo usado pelo `HashMap` do Java. Passou
disso, a tabela dobra de tamanho (arredondando para o próximo primo) e reinsere
tudo.

Medindo esse limite, apareceu algo que a intuição não previa. Inserindo 20 mil
elementos com limites diferentes:

| limite | capacidade final | carga real | comparações por busca |
|---|---|---|---|
| 0,50 | 51.437 | 0,389 | 1,06 |
| 0,75 | 51.437 | 0,389 | 1,06 |
| 1,00 | 25.717 | 0,778 | 1,67 |
| 2,00 | 12.853 | 1,556 | 1,63 |
| 5,00 | 6.421 | 3,115 | 2,29 |

**Escolher 0,5 ou 0,75 dá exatamente o mesmo resultado.** As duas primeiras
linhas são idênticas, e o motivo é que a tabela dobra de tamanho ao
redimensionar: a carga cai pela metade logo depois de cruzar o limite, e passa
a oscilar entre 0,375 e 0,75 em ambos os casos. A carga real média é a mesma,
então o limite escolhido dentro dessa faixa não muda nada.

A outra surpresa é como a degradação é suave. Mesmo com carga 3,1 — correntes
de três elementos em média —, a busca custa 2,29 comparações. O encadeamento
aguenta maus limites muito melhor do que se imagina, o que reforça a conclusão
da seção anterior: a estratégia que sofre com ocupação alta é a outra.

**Por que reinserir, e não só copiar para um vetor maior?** Porque a posição de
cada chave é `hash % capacidade`. Mudou a capacidade, mudou o resto, mudou o
balde. Se copiássemos as correntes para as mesmas posições em um vetor maior, os
dados continuariam na memória, mas a busca iria procurá-los em outro lugar e não
acharia nada. É um bug traiçoeiro porque a inserção parece ter funcionado; só a
busca falha. O teste `test_nenhum_elemento_se_perde_no_redimensionamento` existe
exatamente para pegá-lo.

Redimensionar é caro: O(n), porque toca em todos os elementos. Mas acontece
raramente, e quando acontece a tabela dobra — então a próxima vez demora o dobro
para chegar. Diluindo esse custo entre todas as inserções, o custo médio de
inserir continua sendo O(1). Esse raciocínio tem nome: **análise amortizada**.
Não é que a inserção seja sempre rápida; é que as poucas inserções caras são
compensadas pelas muitas baratas.

## Vendo tudo isso rodar

A opção 7 do `main.py` abre o estado interno das duas tabelas:

```
TABELA DE PRODUTOS
  capacidade (baldes)...: 11
  elementos guardados...: 6
  fator de carga........: 0.545
  baldes ocupados.......: 6
  baldes vazios.........: 5
  maior corrente........: 1
  colisões registradas..: 0
```

O número que mais importa é a **maior corrente**. Enquanto ele ficar em 1 ou 2,
a busca é praticamente um acesso direto. Se ele começar a crescer junto com a
quantidade de produtos, significa que a função de dispersão está concentrando
chaves e a estrutura está deixando de ser O(1) na prática — é o sintoma que
denuncia uma hash mal feita.

No teste com 300 produtos (`test_catalogo_grande_continua_consistente`), a maior
corrente fica abaixo de 10, o que confirma que a djb2 está espalhando bem.

## Como reproduzir

```bash
python3 ferramentas/benchmark_colisoes.py
```

Os cinco experimentos do arquivo correspondem às afirmações deste documento.
Duas delas precisaram ser corrigidas depois de medidas, e ficam registradas
acima como foram encontradas — a versão errada e o que os números mostraram.
