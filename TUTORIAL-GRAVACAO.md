# Tutorial para gravar o vídeo do projeto

Leia tudo uma vez antes de começar. Depois siga de cima para baixo, sem pular.

**Tempo estimado do vídeo:** 8 a 10 minutos.

---

# PARTE 0 — Preparar antes de ligar a gravação

Faça tudo desta parte **antes** de apertar o botão de gravar.

## Passo 0.1 — Abrir o Terminal

1. Aperte **Command + Barra de espaço** (abre a busca do Mac).
2. Digite: `Terminal`
3. Aperte **Enter**.

Uma janela preta ou branca vai abrir. É nela que tudo acontece.

## Passo 0.2 — Aumentar a letra do Terminal

Isso é importante: letra pequena fica ilegível no vídeo.

1. Com o Terminal aberto, aperte **Command + +** (tecla de mais).
2. Aperte umas **5 vezes**, até a letra ficar bem grande.
3. Olhe de longe. Se você não conseguir ler da distância de um braço, aumente mais.

## Passo 0.3 — Deixar a janela do tamanho certo

1. Arraste o canto da janela do Terminal até ela ocupar **mais ou menos 3/4 da tela**.
2. Não deixe em tela cheia — fica difícil de mostrar outras coisas depois.

## Passo 0.4 — Entrar na pasta do projeto

Digite exatamente isto e aperte **Enter**:

```
cd /Users/caiotorres/P-SOFTWARES/FACULADE/CataLog
```

> Se der erro, confira se a pasta é essa mesma. Você pode arrastar a pasta do
> Finder para dentro do Terminal, que ele escreve o caminho sozinho.

## Passo 0.5 — Preparar a inteligência artificial

Digite e aperte **Enter**:

```
python3 preparar_gravacao.py
```

Tem que aparecer **PRONTO PARA GRAVAR**.

**Por que isso é necessário:** o sistema aprende os produtos que você cadastra.
Se você ensaiar com as frases do vídeo, na hora de gravar ele vai responder
do que já aprendeu e a IA não será acionada — você perde a melhor parte.
Este comando faz as três frases voltarem a ser novidade.

> **Rode este comando de novo a cada nova tentativa de gravação.**

## Passo 0.6 — Limpar a tela

Digite e aperte **Enter**:

```
clear
```

A tela fica limpa. Agora sim, pode começar a gravar.

## Passo 0.7 — Conferir o que você vai ter em mãos

Deixe este tutorial aberto **no celular** ou em outra tela. Não deixe na mesma
tela que você vai gravar.

---

# PARTE 1 — A gravação

A partir daqui, a gravação está rodando. Cada cena tem o que fazer e o que falar.

> As falas são sugestões. Fale com suas palavras, mas mantenha os números —
> eles são o que dá credibilidade.

---

## CENA 1 — Abertura (30 segundos)

### O que fazer
Não digite nada ainda. Só fale, com a tela limpa.

### O que falar

> "Olá. Este é o Projeto 4 de Estrutura de Dados: um catálogo de produtos com
> tags automáticas.
>
> O problema é o seguinte: uma loja online com cem mil produtos precisa que o
> cliente ache o que quer rapidamente. Se o sistema tiver que olhar produto por
> produto, não funciona.
>
> Eu resolvi isso de duas formas. Primeiro, o sistema lê a descrição e
> categoriza o produto sozinho. Segundo, ele guarda tudo numa tabela de
> dispersão construída do zero, que faz a busca ser praticamente instantânea.
>
> Vou mostrar funcionando."

---

## CENA 2 — Mostrar que o projeto é sólido (40 segundos)

### O que fazer

Digite e aperte **Enter**:

```
python3 -m unittest discover -s testes -t .
```

Espere 2 segundos. Vai aparecer uma linha de pontinhos e no final:

```
Ran 123 tests in 0.04s

OK
```

### O que falar enquanto roda

> "Antes de mostrar o programa, os testes. São 123 verificações automáticas, e
> todas passam.
>
> A maior parte delas não veio de casos que eu imaginei: veio de defeitos reais
> que eu encontrei usando o sistema. Uma chuteira que saía sem cor, uma palavra
> de ligação virando tag, um violão classificado só pelo material das cordas.
> Cada um virou um teste para não voltar."

### Depois
Digite e aperte **Enter**:

```
clear
```

---

## CENA 3 — Abrir o programa (30 segundos)

### O que fazer

Digite e aperte **Enter**:

```
python3 main.py --ia
```

Espere. Vai aparecer uma linha escrita **"Gerando tags por: modelo local da
Apple..."** e logo abaixo o menu com as opções de 1 a 9, A, B, C e 0.

### O que falar

> "Este é o programa. Repare na primeira linha: ele está usando um modelo de
> inteligência artificial que roda dentro do próprio Mac.
>
> Não é um serviço na internet. Não precisa de senha, não precisa de conexão,
> não custa nada por uso, e nenhum dado sai da máquina."

---

## CENA 4 — Carregar os produtos de exemplo (40 segundos)

### O que fazer

Digite: **`8`** e aperte **Enter**.

Vão aparecer 6 produtos, cada um com uma lista de tags.

### O que falar

> "Carreguei seis produtos de exemplo. Olhem as tags ao lado de cada um:
> calçado, esporte, azul, corrida.
>
> Ninguém digitou nenhuma dessas palavras. O sistema leu o nome e a descrição e
> decidiu sozinho."

---

## CENA 5 — Cadastrar o produto do enunciado (1 minuto)

Esta é a cena mais importante do começo.

### O que fazer

**1.** Digite: **`1`** e aperte **Enter**.

**2.** O programa pergunta **"Nome do produto:"**. Digite exatamente:

```
Tênis azul
```

e aperte **Enter**.

**3.** Ele pergunta **"Descrição......:"**. Digite exatamente:

```
para corrida em asfalto
```

e aperte **Enter**.

**4.** Espere meio segundo. Vai aparecer:

```
Cadastrado: [P007] Tênis azul — esporte, calcado, azul, cor, corrida, asfalto, rua
```

### O que falar

> "Esse é o exemplo exato que está no enunciado do projeto.
>
> O enunciado pedia as tags calçado, esporte, corrida e azul. As quatro estão
> aqui — e mais três que o sistema deduziu sozinho: cor, asfalto e rua.
>
> A primeira tag da lista, 'esporte', veio da inteligência artificial. As outras
> vieram do vocabulário do sistema. Daqui a pouco explico por que os dois
> trabalham juntos."

---

## CENA 6 — Cadastrar algo que o sistema não conhece (1 minuto)

### O que fazer

**1.** Digite: **`1`** e aperte **Enter**.

**2.** Em **"Nome do produto:"** digite exatamente (sem acento):

```
Churrasqueira eletrica
```

e aperte **Enter**.

**3.** Em **"Descrição......:"** digite exatamente:

```
portatil com tampa de vidro
```

e aperte **Enter**.

**4.** Vai demorar **meio segundo a mais** que o anterior. É a IA trabalhando.

```
Cadastrado: [P008] Churrasqueira eletrica — cozinha
```

### O que falar

> "Agora um produto que o sistema nunca viu. Nenhuma dessas palavras está no
> vocabulário: churrasqueira, portátil, tampa, vidro. Nenhuma.
>
> Repare que demorou um pouquinho mais. Foi a inteligência artificial sendo
> consultada agora, offline, e ela classificou como cozinha.
>
> Sem ela, esse produto ficaria sem tag nenhuma e seria invisível na busca."

---

## CENA 7 — Mais um produto novo (30 segundos)

### O que fazer

**1.** Digite: **`1`** e aperte **Enter**.

**2.** Em **"Nome do produto:"**:

```
Mesa de jantar
```

**3.** Em **"Descrição......:"**:

```
em madeira macica para seis lugares
```

**4.** Resultado:

```
Cadastrado: [P009] Mesa de jantar — movel
```

### O que falar

> "Mais um que o sistema não conhecia. A IA classificou como móvel.
>
> Guardem a palavra 'madeira' — eu vou usar ela daqui a pouco."

---

## CENA 8 — Buscar por categoria (40 segundos)

### O que fazer

**1.** Digite: **`3`** e aperte **Enter**.

**2.** Ele pergunta **"Tag:"**. Digite:

```
esporte
```

e aperte **Enter**.

**3.** Vão aparecer **4 produtos**.

### O que falar

> "Busquei por 'esporte' e vieram quatro produtos: dois tênis, uma chuteira e o
> tênis que acabei de cadastrar.
>
> Repare que eu não busquei pelo nome de nenhum deles. Busquei por uma
> característica. É isso que o item quatro do enunciado pede."

---

## CENA 9 — A busca por palavra escrita (1 minuto)

Esta cena mostra algo que impressiona. Não corra.

### O que fazer

**1.** Digite a letra: **`A`** (maiúscula ou minúscula, tanto faz) e aperte **Enter**.

**2.** Ele pergunta **"Palavra:"**. Digite:

```
madeira
```

e aperte **Enter**.

**3.** Aparece **1 produto**: a mesa de jantar.

### O que falar

> "Agora olhem isto. A mesa de jantar só tem uma tag: 'móvel'. A palavra
> 'madeira' não é tag de nada no sistema.
>
> Mas ela está escrita na descrição. E eu encontrei o produto por ela.
>
> São dois índices diferentes funcionando ao mesmo tempo. Um busca por
> significado — foi assim que 'esporte' achou o tênis, mesmo essa palavra não
> estando escrita nele. O outro busca por palavra literal.
>
> Nenhum dos dois acha o que o outro acha. Por isso os dois existem."

---

## CENA 10 — Abrir a estrutura por dentro (1 minuto e meio)

Esta é a cena que mostra o conteúdo da disciplina.

### O que fazer

Digite: **`7`** e aperte **Enter**.

Vai aparecer uma tela com três blocos: **TABELA DE PRODUTOS**, **ÍNDICE DE TAGS**
e **ÍNDICE DE TEXTO**.

### O que falar

> "Aqui dá para ver a estrutura por dentro. São três tabelas de dispersão, todas
> escritas do zero — eu não usei o dicionário pronto do Python.
>
> Olhem o índice de tags. Ele tem 47 gavetas e 26 tags guardadas."

**Aponte com o mouse para a linha "colisões registradas":**

> "Cinco colisões. Colisão é quando duas tags diferentes são mandadas para a
> mesma gaveta. Isso não é falha, é inevitável: existem infinitas palavras
> possíveis e um número limitado de gavetas.
>
> No meu caso, as tags 'corrida', 'cozinha' e 'trilha' caíram todas na mesma.
> Elas convivem porque cada gaveta guarda uma correntinha, e a busca percorre
> essa corrente."

**Aponte para "maior corrente":**

> "E esta linha é a mais importante: a maior corrente é 3. Significa que, no
> pior caso, a busca compara três itens em vez de vinte e seis. É isso que faz a
> estrutura ser rápida."

### Depois
Digite: **`0`** e aperte **Enter** para sair do programa.

---

## CENA 11 — A prova de velocidade (1 minuto)

### O que fazer

**1.** Digite e aperte **Enter**:

```
clear
```

**2.** Digite e aperte **Enter**:

```
python3 benchmark.py
```

**3.** Espere uns **20 segundos**. Vai montando uma tabela com três linhas.

### O que falar enquanto roda

> "Agora a prova de que valeu a pena. Este teste compara duas formas de buscar:
> usando o índice que eu criei, ou percorrendo o catálogo inteiro."

**Quando terminar, aponte para a última linha:**

> "Com cinquenta mil produtos, a busca pelo índice levou zero vírgula vinte e
> sete milissegundos. Percorrendo tudo, doze milissegundos. Quarenta e cinco
> vezes mais rápido.
>
> Mas o número não é o mais importante. O importante é que a coluna da
> varredura cresce junto com o catálogo, e a do índice não. Quanto maior a
> loja, maior a diferença."

---

## CENA 12 — Onde eu errei (1 minuto e meio)

**Esta é a cena que mais vale a nota.** Fale com calma.

### O que fazer

**1.** Digite e aperte **Enter**:

```
clear
```

**2.** Digite e aperte **Enter**:

```
python3 benchmark_colisoes.py
```

**3.** Vai aparecer bastante coisa. **Role a tela para cima** até achar o bloco
que começa com **"3. Encadeamento contra endereçamento aberto"**.

> Para rolar: use a rodinha do mouse ou dois dedos no trackpad.

### O que falar

Mostrando o experimento 3:

> "Eu tinha escrito na documentação que a estratégia que descartei piora quando
> há muitas remoções. Era o que eu tinha lido.
>
> Então eu implementei a alternativa e fiz vinte mil ciclos de remoção para
> comprovar. Olhem o resultado: antes, 3 vírgula 33 comparações. Depois, 3
> vírgula 33. Não piorou nada.
>
> Eu estava errado. Tinha repetido teoria sem verificar."

**Agora role para baixo, até o experimento 5 (o último):**

> "O motivo real da desvantagem era outro, e aparece aqui. Com a tabela vazia,
> as duas estratégias empatam. Conforme enche, a que escolhi quase não se mexe,
> e a outra vai para sessenta e duas comparações por busca. Quarenta e oito
> vezes pior.
>
> Corrigi a documentação e deixei registrado o que eu tinha escrito antes."

---

## CENA 13 — Fechamento (40 segundos)

### O que fazer

Digite e aperte **Enter**:

```
clear
```

Fale com a tela limpa.

### O que falar

> "Resumindo o que foi feito: três tabelas de dispersão construídas do zero, com
> função de hash própria, tratamento de colisão e crescimento automático. Um
> índice invertido que torna a busca por característica quase instantânea. E uma
> inteligência artificial rodando localmente, que categoriza produtos que o
> sistema nunca viu.
>
> A conclusão que eu levo deste projeto é que medir mudou decisões. Duas coisas
> que eu tinha escrito como verdade estavam erradas, e só descobri porque
> implementei a alternativa e comparei.
>
> Obrigado."

---

# PARTE 2 — Se algo der errado durante a gravação

## A IA não respondeu / deu erro

Não se desespere, isso está previsto no sistema. Fale:

> "O modelo não está disponível agora. O sistema continua funcionando com o
> vocabulário e com tudo que já aprendeu antes, porque esse conhecimento fica
> gravado em arquivo."

E continue normalmente. Tudo funciona.

## Digitei o nome errado do produto

1. Digite: **`9`** e aperte **Enter**.
2. Digite o código do produto (por exemplo `P008`) e aperte **Enter**.
3. Cadastre de novo com a opção `1`.

## O programa travou

1. Aperte **Control + C**.
2. Digite `python3 main.py --ia` e comece de novo.

Você perde os produtos cadastrados, mas não o aprendizado da IA.

## Quero regravar do zero

1. Aperte **Control + C** se o programa estiver aberto.
2. Digite:

```
python3 preparar_gravacao.py
```

```
clear
```

3. Comece de novo da CENA 1.

---

# Cola rápida

Imprima só esta parte e deixe do lado do teclado.

```
ANTES          cd /Users/caiotorres/P-SOFTWARES/FACULADE/CataLog
               python3 preparar_gravacao.py
               clear

CENA 2         python3 -m unittest discover -s testes -t .
               clear

CENA 3         python3 main.py --ia

CENA 4         8

CENA 5         1  ->  Tênis azul
                  ->  para corrida em asfalto

CENA 6         1  ->  Churrasqueira eletrica
                  ->  portatil com tampa de vidro

CENA 7         1  ->  Mesa de jantar
                  ->  em madeira macica para seis lugares

CENA 8         3  ->  esporte

CENA 9         A  ->  madeira

CENA 10        7
               0

CENA 11        clear
               python3 benchmark.py

CENA 12        clear
               python3 benchmark_colisoes.py

CENA 13        clear
```
