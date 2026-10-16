# Catálogo de Produtos com Tags Automáticas

Projeto 4 — Estrutura de Dados 1

---

## O que é este sistema

Imagine uma loja online com cem mil produtos. Alguém procura por "tênis azul de
corrida". Como o site encontra isso rápido?

O jeito óbvio seria o site abrir produto por produto, conferir se bate com o que
foi pedido, e montar a lista. Funciona com dez produtos. Com cem mil, o cliente
desiste antes de a página carregar.

Este sistema resolve esse problema de duas formas.

A primeira é **categorizar os produtos sozinho**. Quando alguém cadastra um
"Tênis azul para corrida em asfalto", o sistema lê esse texto e decide, por
conta própria, que aquilo é um calçado, é esportivo, serve para corrida e é
azul. Essas palavras são as *tags*, e ninguém precisa digitá-las.

A segunda é **guardar os produtos de um jeito que torne a busca instantânea**.
Em vez de uma lista que precisa ser percorrida, usei uma estrutura em que
encontrar algo não depende de quantas coisas existem guardadas. É a parte do
trabalho que a disciplina avalia, e é onde está o esforço maior.

O resultado é um catálogo onde cadastrar um produto leva menos de um décimo de
segundo e buscar leva menos de um milésimo — mesmo com cinquenta mil produtos
dentro.

---

## Como ele funciona, em uma olhada

Cadastrar um produto dispara esta sequência:

```
  "Tênis azul" + "para corrida em asfalto"
            |
            v
  1. O texto é limpo e separado em palavras
            |
            v
  2. As palavras viram tags: calçado, esporte, azul, corrida...
            |
            v
  3. O produto é guardado, e as tags viram "atalhos" até ele
```

Daí em diante, procurar por qualquer uma dessas tags leva direto ao produto, sem
olhar nenhum outro.

As quatro seções a seguir destrincham cada etapa: o que fiz, como fiz e —
principalmente — por que daquele jeito.

---

## Parte 1 — Receber o nome e a descrição

### O que fiz

O sistema recebe duas informações de cada produto: um nome ("Tênis azul") e uma
descrição ("para corrida em asfalto"). A partir daí, ele cuida de tudo sozinho:
gera um código de identificação (P001, P002...), cria as tags e guarda tudo.

### Por que separar nome e descrição

Poderia ser um texto só. Separei porque as duas coisas têm pesos diferentes: o
nome diz o que o produto **é**, a descrição diz como ele é. Quando o sistema
monta a lista de tags, as que vieram do nome aparecem primeiro, porque são as
mais importantes para quem procura.

### A parte invisível: arrumar o texto antes de usar

Esta é a primeira decisão que vale explicar, porque ela parece detalhe e é
fundamental.

As pessoas escrevem de formas diferentes. "Tênis Azul", "tenis azul" e "TÊNIS,
AZUL!" são a mesma coisa para um ser humano e três textos completamente
diferentes para um computador. Se guardasse do jeito que vem, quem cadastrasse
com acento nunca seria encontrado por quem buscasse sem.

Então, antes de qualquer coisa, todo texto passa por uma limpeza:

- vira minúsculo;
- perde os acentos ("tênis" vira "tenis");
- a pontuação vira espaço, para "azul,corrida" não virar a palavra inexistente
  "azulcorrida";
- palavras de ligação são descartadas — "para", "de", "em" aparecem em quase
  toda descrição e não ajudam a distinguir nada.

O mesmo tratamento é aplicado nos dois lados: na hora de cadastrar e na hora de
buscar. É isso que faz alguém digitar "CALÇADO" e encontrar um produto guardado
como "calcado".

---

## Parte 2 — A inteligência artificial gera as tags

### O que fiz

Cada produto cadastrado é analisado por um modelo de inteligência artificial que
roda **dentro do próprio computador**. Ele lê o nome e a descrição e responde a
que categoria o produto pertence: calçado, cozinha, ferramenta, eletrônico e
assim por diante.

Não é um serviço na internet. Não precisa de senha, não precisa de conexão, não
custa nada por uso e nenhum dado sai da máquina. É o modelo do Apple
Intelligence, que já vem instalado em Macs recentes.

### A IA de fábrica não serve: as sete melhorias que precisei fazer

Esta é a parte mais longa do documento, e é de propósito. Ligar a IA foi fácil.
Fazer com que ela entregasse algo aproveitável deu trabalho, e cada ajuste veio
de um problema concreto que apareceu testando.

**1. Impedir que ela inventasse palavras**

A primeira versão simplesmente pedia: "responda com as tags separadas por
vírgula". O resultado parecia bom e não era. Perguntei a mesma coisa três vezes
para o mesmo produto e recebi três respostas diferentes — uma delas inventou a
tag "esportividade", que não significa nada. Outra separou com ponto e vírgula
em vez de vírgula. Uma terceira devolveu tudo grudado com hífens.

Pedir educadamente no texto não garante nada. A solução foi mudar o tipo da
resposta: em vez de aceitar texto livre, declarei que a resposta **tem** que ser
uma opção de uma lista fechada. A IA deixou de poder inventar, porque não existe
onde escrever algo fora da lista.

Isso resolveu o problema mais grave que eu tinha. Antes, ela dizia "calcado"
para um produto e "calcados" para outro, e o sistema tratava os dois como
categorias sem relação nenhuma. Na prática: cadastrei seis calçados, busquei por
calçado, apareceram quatro. Depois da mudança, apareceram os seis.

**2. Tirar a aleatoriedade**

Modelos de linguagem têm um ajuste que controla o quanto eles podem variar na
escolha das palavras. No padrão, há variação — é o que os faz parecer criativos.

Num catálogo, isso é defeito. Se o mesmo produto pode receber categorias
diferentes dependendo do dia, não dá nem para escrever um teste automático.
Zerei esse ajuste, e a IA passou a responder sempre a mesma coisa para a mesma
entrada.

**3. Fazer a pergunta certa**

Aqui errei feio, e foi um teste barato que me salvou.

Minha ideia era perguntar palavra por palavra: "guarda-chuva é de que
categoria?", "dobrável é de que categoria?". Antes de implementar, testei. O
resultado foi assustador:

```
  guardachuva  ->  acessório   certo
  cafeteira    ->  cozinha     certo
  dobravel     ->  calçado     errado
  resistente   ->  calçado     errado
  xyzabc       ->  calçado     errado
```

"Xyzabc" não é palavra de idioma nenhum e virou calçado. Em treze palavras
testadas, a IA usou a opção "isto não é um produto" exatamente uma vez.

Se eu tivesse implementado assim, o sistema guardaria "dobrável significa
calçado" **para sempre**, e toda cadeira dobrável apareceria na busca por tênis.

O erro não era da IA, era da minha pergunta. "Dobrável" sozinho não quer dizer
nada — nem para ela, nem para uma pessoa. Perguntando sobre a frase inteira, com
contexto, ela acerta e sabe recusar:

```
  Guarda-chuva dobrável automático  ->  acessório
  xyzabc qwerty                     ->  desconhecida
```

**4. Deixar uma regra simples fazer o que ela fazia pior**

Eu queria que a IA apontasse qual palavra do texto nomeia o produto —
"frigideira" em "Frigideira antiaderente de cerâmica". Pedi isso junto com a
categoria, instruindo para copiar uma palavra só.

Ela devolveu a frase inteira em sete dos oito casos.

A solução não foi insistir com a IA, foi perceber que aquilo nem precisava dela.
Em português, nome de produto começa pelo substantivo: *Frigideira*
antiaderente, *Esteira* ergométrica, *Trena* a laser. Escrevi uma regra de três
linhas que pega a primeira palavra significativa.

A regra acertou dezesseis de dezesseis. A IA tinha acertado um de oito.

Vale guardar essa comparação: não é que a regra seja mais inteligente. É que ela
aproveita uma regularidade que existe no problema, e a IA não tinha motivo para
respeitar.

**5. Limpar o que ela devolve**

Mesmo acertando a categoria, a IA entrega o texto fora do padrão que o sistema
precisa. Observando a saída real, encontrei: acentos onde não deveria ter
("calçado"), a mesma tag repetida duas vezes na mesma resposta, tags com duas
palavras ("roupa interior") e até português de Portugal ("desporto" em vez de
"esporte").

Nada disso pode entrar direto. Então tudo que a IA responde passa pela mesma
limpeza que o resto do sistema usa: minúsculas, sem acento, uma palavra por tag,
sem repetição.

A conclusão disso merece registro, porque contraria a expectativa: **usar
inteligência artificial não dispensou nenhuma das decisões de estrutura de dados
do projeto.** Ela substituiu o vocabulário, não a disciplina de organizar.

**6. Não perguntar duas vezes a mesma coisa**

Cada consulta à IA leva cerca de meio segundo. Numa loja real, isso é lento
demais para fazer sempre.

Então o sistema passou a anotar o que aprendeu. E a melhoria que fez diferença
foi anotar a **palavra**, não o produto. Quando a IA classifica uma "Frigideira
antiaderente de cerâmica" como cozinha, o sistema guarda que "frigideira"
significa cozinha. Qualquer frigideira futura — de teflon, de ferro, grande,
pequena — já sai classificada sem consultar nada.

Medi: cadastrei quinze produtos novos que usavam palavras já conhecidas.
**Nenhum** precisou da IA. Levaram menos de um milésimo de segundo somados,
contra os nove segundos que custariam em consultas.

Mas generalizar é perigoso, e precisei de uma defesa. "Jogo de chaves de fenda"
é ferramenta e "jogo de facas" é cozinha. Se o sistema decidisse que "jogo" é
uma das duas, erraria a outra. Hoje ele percebe sozinho quando a mesma palavra
aparece ligada a categorias diferentes, marca a palavra como ambígua e para de
usá-la como atalho.

**7. Saber quando não consultá-la, e quando não confiar nela**

Duas descobertas tardias, as duas vindas de ver o programa rodando.

A primeira: o sistema só chamava a IA quando o produto não gerava nenhuma tag.
Parecia razoável e estava errado. Um "Violão acústico com cordas de nylon"
recebia as tags "nylon" e "material" do vocabulário, o sistema achava que já
sabia o suficiente, e a IA nunca era consultada. O produto ficava no catálogo
sem nada dizendo que era um instrumento.

Medindo, o problema era maior: **quatro em cada dez produtos** estavam assim.
Uma cadeira de couro não era móvel; um tapete não era decoração. O critério
confundia "ter alguma tag" com "saber o que o produto é". Hoje a IA é consultada
sempre que falta a categoria, mesmo que já existam outras tags.

A segunda: tentei medir o quanto a IA estava segura de cada resposta,
perguntando várias vezes e vendo se ela mudava de ideia. A ideia era bonita. Os
números foram modestos — detectou três dos sete erros que eu já conhecia, deixou
quatro passar e ainda acusou uma resposta certa.

Descobri que **estabilidade não é o mesmo que acerto**: a IA pode estar
consistentemente errada. Mantive o recurso, mas com o papel que ele merece:
ajuda a decidir o que revisar primeiro, não decide o que está certo.

### O que ela continua fazendo mal

Uma limitação não teve conserto: **a IA não sabe dizer "não sei"**.

Perguntei a cor de uma "Camisa de algodão", texto que não menciona cor nenhuma.
Ela respondeu "azul". Inventou. Tentei deixar o campo opcional e instruir
explicitamente para só responder se a cor estivesse escrita — ela preencheu
igual.

Num catálogo isso é grave: o cliente filtra por azul e recebe uma camisa branca.

Por isso o trabalho ficou dividido assim, e essa divisão é a conclusão de todas
as melhorias acima:

| quem decide | o quê | por quê |
|---|---|---|
| a IA | a categoria do produto | acerta até em produtos que ninguém cadastrou antes |
| o vocabulário | cor, material, uso | só informa o que está escrito, nunca inventa |

O "vocabulário" é uma lista que escrevi, ligando palavras a tags: "azul" é uma
cor, "couro" é um material, "corrida" é um uso. É burro, mas é exato. Cada um
cuida do que faz bem.

### O resultado final

Depois das sete melhorias, a IA deixou de ser um gerador imprevisível e virou
uma peça confiável do sistema:

- responde sempre a mesma coisa para a mesma entrada;
- não consegue inventar uma categoria que não existe;
- sabe recusar quando não reconhece o produto;
- é consultada uma vez por palavra nova, e nunca mais;
- o que ela ensina fica num arquivo de texto comum, que pode ser lido, conferido
  e corrigido à mão por uma pessoa.

Esse último ponto é o que mais me convenceu de que o caminho estava certo.
Revisando o que a IA tinha classificado, achei sete erros — ela colocou uma
trena a laser em artigos de esporte e um colchão em acessórios. Corrigi os sete
editando um arquivo de texto, em um minuto. Se esse conhecimento estivesse
dentro de um modelo treinado, não haveria o que revisar nem como corrigir um
caso específico.

## Parte 3 — Guardar na tabela de dispersão

### O problema, em termos simples

Imagine um armário com mil gavetas numeradas e você precisa guardar mil papéis.
Se guardar na ordem que chegam, achar um papel específico depois exige abrir uma
gaveta por vez.

A tabela de dispersão — ou *hash table* — resolve isso de um jeito diferente:
ela faz uma conta com o conteúdo do papel e essa conta diz em qual gaveta ele
deve ficar. Para achar depois, basta refazer a conta. Você vai direto à gaveta
certa, sem abrir nenhuma outra. Não importa se o armário tem mil ou um milhão de
gavetas: o tempo é o mesmo.

Essa conta se chama função de dispersão, e eu a escrevi do zero.

### Por que não usei o que a linguagem já oferece

O Python, linguagem que usei, já vem com uma estrutura pronta que faz exatamente
isso. Usá-la seria uma linha de código.

Não usei de propósito. A disciplina é sobre entender a estrutura, e a versão
pronta esconde justamente o que está sendo estudado. Construí a minha: a conta
que decide a gaveta, o que fazer quando dois itens caem na mesma, quando o
armário precisa crescer.

Há ainda um motivo prático. A função pronta do Python muda de resultado a cada
vez que o programa roda — é uma proteção de segurança da linguagem. Isso
tornaria impossível demonstrar em sala que determinado produto vai para
determinada gaveta, porque na próxima execução iria para outra.

### O que acontece quando dois produtos querem a mesma gaveta

Isso tem nome — colisão — e não é falha: é inevitável. Existem infinitos textos
possíveis e um número limitado de gavetas, então necessariamente alguns vão
disputar o mesmo lugar.

A pergunta certa não é como evitar, é o que fazer quando acontece. Existem duas
respostas possíveis, e eu testei as duas.

**A que escolhi:** cada gaveta guarda uma corrente. Se dois produtos caem na
mesma, o segundo é pendurado no primeiro, e a busca percorre a correntinha.
Normalmente ela tem um ou dois itens.

**A outra:** o segundo produto procura a próxima gaveta livre.

Implementei as duas e medi. Com o armário quase cheio, a primeira estratégia
custava **1,3 comparações** por busca e a segunda custava **62**. Quase
cinquenta vezes pior.

O motivo é que, na segunda estratégia, um produto deslocado ocupa a gaveta do
vizinho, que desloca o próximo, e forma-se um bloco que cresce sozinho. Na
primeira, uma corrente longa não atrapalha as gavetas vizinhas.

### Como o sistema cresce sozinho

Quanto mais cheio o armário, mais longas as correntes e mais lenta a busca. Por
isso o sistema vigia a própria ocupação: quando passa de 75%, ele dobra de
tamanho e redistribui tudo.

A redistribuição é obrigatória, não um capricho. A gaveta de cada item depende
do número total de gavetas; mudando esse número, muda a conta. Se eu copiasse os
itens para as mesmas posições em um armário maior, eles continuariam lá, mas a
busca passaria a procurar no lugar errado e não acharia nada. É um erro
traiçoeiro porque tudo parece funcionar — só a busca falha.

### Um detalhe que rendeu uma surpresa

A quantidade de gavetas é sempre um número primo. A teoria diz que isso espalha
melhor os itens, e eu confirmei medindo — com uma diferença maior do que
esperava.

Testei as mesmas cinco mil chaves com 1024 gavetas e com 1031. Com 1024, **316
gavetas nunca receberam nada**. Quase um terço do armário ficou vazio enquanto o
resto se amontoava. Com 1031, nenhuma sobrou vazia.

---

## Parte 4 — Buscar pelas tags

### A armadilha em que quase caí

Guardar o produto na tabela resolve "me mostre o produto P007". Mas o enunciado
pede outra coisa: achar produtos **pelas tags**.

Com uma tabela só, isso significaria abrir cada produto e conferir as tags de
cada um. Ou seja, eu voltaria a percorrer o catálogo inteiro — exatamente o
problema que a estrutura deveria resolver. A estrutura estaria certa,
respondendo à pergunta errada.

### A solução: virar a chave do avesso

Criei uma segunda tabela, construída ao contrário. Na primeira, o produto é a
chave. Na segunda, a **tag** é a chave, e o conteúdo é a lista de produtos que a
possuem.

```
  tabela de produtos            tabela de tags
  P001 -> Tênis azul            calçado -> P001, P003
  P002 -> Camisa azul           azul    -> P001, P002
  P003 -> Chuteira              corrida -> P001
```

Agora buscar por "azul" é uma consulta direta que já devolve a resposta pronta.

É a mesma ideia do índice remissivo no fim de um livro técnico: em vez de ler o
livro inteiro procurando uma palavra, você olha a palavra no índice e ela te diz
as páginas.

Medi o ganho: com cinquenta mil produtos, buscar pelo índice é **45 vezes mais
rápido** que percorrer o catálogo. E o número cresce junto com o catálogo —
quanto maior a loja, maior a vantagem.

### O preço, e por que vale

A mesma informação fica guardada em dois lugares. Isso gasta mais memória e cria
uma obrigação: ao remover um produto, é preciso limpar os dois lugares. Esquecer
o segundo deixa a tag apontando para um produto que não existe mais, e a busca
quebra depois — longe de onde o erro foi cometido.

Vale a pena porque, numa loja, busca acontece milhares de vezes para cada
cadastro. Gastar um pouco mais na hora de guardar para economizar muito na hora
de procurar é uma troca óbvia.

### Uma terceira tabela, para o que as tags não cobrem

Percebi um problema testando: produtos classificados pela IA recebiam uma única
tag. Uma "Frigideira antiaderente de cerâmica" ficava só com "cozinha", e quem
procurasse "cerâmica" não achava — apesar de a palavra estar escrita ali.

Criei então um terceiro índice, que guarda as palavras literalmente escritas no
produto. Os dois convivem e fazem coisas diferentes:

- procurar "calçado" acha o tênis, **mesmo a palavra não estando escrita nele** —
  isso exige entender que tênis é um calçado;
- procurar "cerâmica" acha a frigideira, mesmo "cerâmica" não sendo categoria de
  nada — isso exige apenas que a palavra esteja no texto.

Nenhum dos dois encontra o que o outro encontra.

---

## Os erros que cometi, e o que eles mudaram

Esta seção existe porque, para mim, foi a parte mais valiosa do trabalho.

Em vários momentos escrevi uma afirmação que parecia óbvia, fui medir, e o
resultado foi diferente. Em três casos, isso mudou uma decisão do projeto.

**Escrevi que a estratégia de colisão que descartei "piora com muitas
remoções".** Era o que eu tinha lido. Implementei a alternativa e fiz vinte mil
ciclos de remoção para comprovar: o desempenho não piorou nada. A afirmação
estava errada — eu tinha repetido teoria sem verificar. O motivo real da
desvantagem era outro, os blocos que crescem sozinhos, e corrigi a documentação
deixando registrado o que eu havia escrito antes.

**Achava que o limite de ocupação da tabela importava muito.** Testei com 50% e
com 75%, esperando ver diferença, e os resultados vieram idênticos — porque a
tabela dobra de tamanho ao crescer, e a ocupação acaba oscilando na mesma faixa
nos dois casos. A escolha que eu julgava importante não mudava nada.

**Tentei medir o quanto a IA estava segura** de cada resposta, perguntando
várias vezes e vendo se ela mudava de ideia. Parecia elegante. Na prática
detectou só três dos sete erros que eu já conhecia, e ainda acusou uma resposta
certa. Mantive o recurso, mas com o papel que os números sustentam: serve para
decidir o que revisar primeiro, não para julgar o que está certo.

Houve também os defeitos que só apareceram **usando** o programa, nunca nos
testes automáticos:

- uma chuteira preta saía sem nenhuma tag de cor, porque a regra de plural não
  trata gênero e "preta" não estava no vocabulário;
- a palavra "de" virou tag, porque eu filtrava as palavras inúteis antes de
  separar as compostas, e "de homem" passava inteira pelo filtro;
- um violão foi classificado apenas pelo material das cordas, porque o sistema
  considerava que já tinha tags suficientes e nem consultava a IA.

Esse último era maior do que parecia. Medindo, descobri que **quatro em cada dez
produtos** estavam no catálogo sem nada que dissesse o que eram: uma cadeira de
couro não era móvel, um tapete não era decoração. O problema estava escondido
atrás de uma lista de tags que parecia preenchida.

Cada um desses defeitos virou uma verificação automática, para não voltar sem
ninguém perceber. É daí que vem a maior parte dos 123 testes do projeto: não de
casos que imaginei, mas de erros que cometi.

---

## O que o sistema não faz

Listar limitações não é modéstia — é saber onde o sistema termina.

**Os dados somem ao fechar.** O catálogo vive na memória. Salvar em arquivo ou
banco de dados é assunto de outra disciplina e não acrescentaria nada ao que o
trabalho se propõe.

**O vocabulário é limitado.** Palavras que não estão nele não geram tags de cor
ou material. A IA cobre a categoria, mas não os atributos.

**As categorias são uma lista fechada.** Um violão é classificado como "áudio",
porque não existe categoria para instrumento musical. A lista é fechada de
propósito — é o que impede a IA de inventar variações —, e o preço é que
produtos fora dela caem na opção menos ruim.

**A IA precisa de um Mac recente.** O modo com inteligência artificial exige Mac
com chip Apple e sistema atualizado. Sem isso, o sistema funciona normalmente
com o vocabulário e com tudo o que já foi aprendido antes, porque esse
conhecimento está gravado em arquivo.

**O sistema não entende frases.** Ele reconhece palavras. "Mochila para
notebook" recebe a marcação de informática porque a palavra "notebook" está lá,
mesmo a mochila não sendo um equipamento. É defensável — quem procura acessório
de informática provavelmente quer ver essa mochila —, mas é bom saber que não há
compreensão de verdade acontecendo.

---

## Como usar

O sistema não precisa de instalação nem de bibliotecas externas. Só do Python.

```
python3 main.py        # só com o vocabulário, funciona em qualquer computador
python3 main.py --ia   # com a inteligência artificial analisando cada produto
```

O programa abre um menu de terminal com as opções de cadastrar, listar, buscar
por tag, buscar por várias tags ao mesmo tempo, buscar por palavra escrita e ver
o estado interno das tabelas.

Para conferir que tudo funciona:

```
python3 -m unittest discover -s testes -t .
```

São 123 verificações automáticas. A maior parte delas nasceu de um defeito real
encontrado durante o desenvolvimento, e existe para impedir que ele volte.

Para ver as medições de desempenho citadas neste documento:

```
python3 ferramentas/benchmark.py            # busca com índice contra busca percorrendo tudo
python3 ferramentas/benchmark_colisoes.py   # as duas estratégias de colisão comparadas
```
