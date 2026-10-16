# O vocabulário que aprende com um modelo de linguagem

Documento 6 de 6. Como o projeto usa o modelo de linguagem local do Mac sem
abrir mão de nada que as tabelas hash precisam.

Código correspondente: `catalogo/professor.py`, `catalogo/tagger.py` e
`ia/ClassificaProduto.swift`.

Este documento é diferente dos outros. Os cinco primeiros explicam decisões
tomadas; este conta um experimento que deu errado três vezes antes de dar
certo, porque cada erro ensinou algo que o resultado final não mostra sozinho.

## O ponto de partida

O enunciado pede, no item 2, para "pedir à IA que analise a descrição". A
primeira versão do projeto não fazia isso — a análise era toda por regras, pelos
motivos do documento 2.

O Mac tem um modelo de linguagem rodando localmente, o do Apple Intelligence,
acessível pelo framework FoundationModels. Sem internet, sem chave de API, sem
custo por chamada e sem mandar dado nenhum para fora. A pergunta natural foi:
por que não usá-lo no lugar do vocabulário escrito à mão?

Tentamos. Três vezes.

## Tentativa 1: pedir tags em texto livre

A versão óbvia. Instrução no prompt: "responda com tags separadas por vírgula,
em minúsculas, sem acentos".

O modelo respondeu, e rápido — cerca de 400 ms por produto. Mas:

```
Tenis azul para corrida em asfalto
  [1] calçados; tênis; corrida; asfalto; azul; esportivo
  [2] calçados, tênis, corrida, asfalto, azul, esportivos
  [3] calçados, esportivos, corrida, azul, tênis, asfalto, esportividade
```

Três execuções, três respostas. A terceira inventou "esportividade". Uma delas
usou ponto e vírgula em vez de vírgula. Em outro produto, devolveu
`camisas-de-algodao-masculinas` como uma única tag. E ignorou a instrução sobre
acentos: veio "calçados", "tênis", "algodão".

Uma das nove chamadas falhou sozinha, com erro de janela de contexto — em um
texto de dez palavras.

**O que isso ensinou:** instrução em prompt é pedido, não garantia.

## Tentativa 2: restringir o formato

Duas correções.

A primeira foi declarar a saída como um **tipo**, usando `@Generable`, em vez de
pedir um formato no texto. O framework tem geração guiada: o modelo não escolhe
o formato, ele é obrigado a produzir a estrutura declarada.

A segunda foi **temperatura zero**. A temperatura controla o quanto o modelo
pode variar na escolha das palavras; com zero, ele escolhe sempre a opção mais
provável em vez de sortear entre as prováveis.

Funcionou para o que se propunha. As três execuções do mesmo produto passaram a
dar resultado idêntico, e nenhuma chamada falhou. O modelo virou testável.

Mas aí medimos a coisa certa. Cadastramos seis calçados e buscamos `calcado`:

```
REGRAS: 6 de 6
MODELO: 4 de 6
  ok  Tenis azul       [tenis, azul, corrida, asfalto, calcado, desporto, material]
      Tenis preto      [tenis, preto, trilha, material, cor, uso]
  ok  Chuteira preta   [futebol, chuteira, preta, material, calcado]
  ok  Sandalia marrom  [sandalia, marrom, couro, calcado, roupa, mulher, calcados, femininos]
      Bota de couro    [botas, couro, masculina, calcados, roupa, estilo]
  ok  Sapato social    [sapato, social, preto, calcado, casual, roupa, calcados]
```

Dois produtos sumiram da busca. A bota recebeu `calcados`, no plural. E a
sandália recebeu `calcado` **e** `calcados`, as duas, na mesma resposta.

Para a tabela hash isso é fatal, e o motivo é o conteúdo da disciplina:
`calcado` e `calcados` são strings diferentes, geram números de dispersão
diferentes e vão para baldes diferentes. São duas chaves sem relação nenhuma. O
índice invertido fica partido em dois e metade dos calçados some do filtro.

**O que isso ensinou:** existem duas propriedades diferentes, e é fácil
confundi-las.

- **Determinismo** — a mesma entrada produz sempre a mesma saída. O modelo
  passou a ter isso com temperatura zero.
- **Consistência entre produtos** — produtos da mesma categoria recebem a mesma
  tag. O modelo **não** tem isso, e temperatura zero não resolve, porque
  entradas diferentes continuam sendo entradas diferentes.

Para um índice invertido, a segunda é a que importa. Um índice só funciona se a
mesma categoria sempre virar a mesma chave. O vocabulário tem essa propriedade
por construção: `tenis`, `bota` e `sapato` apontam todos para `calcado` porque
está escrito assim no arquivo, e não há como variar.

É uma conclusão que inverte a intuição. O gerador "burro" é melhor justamente
por ser burro: ele não tem liberdade para ser criativo em um lugar onde
criatividade quebra a estrutura.

### Por que fine-tuning não resolveria isso

Vale registrar, porque foi uma ideia considerada a sério.

Treinar um adaptador para o modelo mudaria *o que* ele tende a responder, mas
não a natureza dele: continuaria escolhendo a próxima palavra por
probabilidade. Dá para fazer `calcados` ficar 2% provável em vez de 30%, mas
não para torná-lo impossível. E um produto em cada cinquenta caindo na variante
errada já fura o índice.

Além disso, o que se quer aqui — "tenis sempre vira calcado" — é um mapeamento
fixo de entrada para saída. Isso tem nome nesta disciplina: é uma tabela de
lookup. Treinar uma rede neural de bilhões de parâmetros para memorizar um
mapeamento determinístico é usar a ferramenta errada com muito esforço, e no
fim ela ainda erra às vezes, enquanto a tabela nunca erra.

No aspecto prático, o adaptador da Apple exige PyTorch, dataset de treino, horas
de processamento, tem centenas de megabytes e precisa ser retreinado a cada
atualização do modelo base.

## Tentativa 3: restringir também o conteúdo

Se o problema é o modelo inventar variações, por que não fechar o conjunto de
respostas possíveis? Em vez de aceitar qualquer texto, declarar as categorias
como um enum:

```swift
@Generable
enum Categoria: String {
    case calcado, vestuario, acessorio, eletronico, cozinha, ...
}
```

Agora o modelo é **estruturalmente incapaz** de responder `calcados`: esse valor
não existe no tipo.

Funcionou:

```
Tenis azul para corrida  -> calcado
Tenis preto para trilha  -> calcado
Chuteira preta futebol   -> calcado
Sandalia marrom de couro -> calcado
Bota de couro masculina  -> calcado
Sapato social preto      -> calcado
Guarda-chuva dobravel    -> acessorio
```

Seis de seis. E o guarda-chuva virou `acessorio` sem a palavra estar cadastrada
em lugar nenhum — a vantagem real do modelo, preservada.

Mas apareceu outro problema. Pedindo também a cor:

```
Bota de couro masculina  -> cor = preto
Guarda-chuva dobravel    -> cor = preto
Camisa de algodao        -> cor = azul
```

Nenhum desses textos diz a cor. O modelo inventou. Tornar o campo opcional e
instruir "SOMENTE se estiver escrita no texto" não mudou nada: ele preencheu
igual.

**O que isso ensinou:** o modelo não sabe dizer "não sei". Ele é treinado para
produzir resposta, não para se abster. Num catálogo isso é grave — o cliente
filtra por azul e recebe uma camisa branca.

## A tentativa que falhou mais feio

Com o enum funcionando, veio a ideia de deixar o vocabulário aprender sozinho:
palavra desconhecida, pergunta ao modelo a que categoria pertence, grava.

Testamos antes de implementar. Ainda bem:

```
guardachuva  -> acessorio      certo
chuteira     -> calcado        certo
cafeteira    -> cozinha        certo

dobravel     -> calcado        errado
automatico   -> eletronico     errado
resistente   -> calcado        errado
couro        -> calcado        errado
masculino    -> calcado        errado
xyzabc       -> calcado        errado
```

`xyzabc` não é palavra de idioma nenhum e virou calçado. Das treze palavras, o
modelo usou a opção "não é um produto" exatamente uma vez.

Um vocabulário que aprendesse assim ia acumular lixo **permanente**, gravado em
arquivo: `dobravel` viraria calçado para sempre, e toda cadeira dobrável
apareceria na busca por tênis.

**O que isso ensinou:** o erro estava na pergunta, não no modelo. Repare no
padrão — ele acerta quando a palavra **é** um produto e erra quando precisa
julgar se ela é um produto. `dobravel` sozinho não quer dizer nada; a pergunta
não tinha resposta.

Perguntando sobre a frase inteira, o modelo tem contexto:

```
Guarda-chuva dobravel automatico -> acessorio
Cafeteira eletrica               -> eletronico
xyzabc qwerty                    -> desconhecida
```

Ele soube recusar.

## O desenho final

Tudo que foi aprendido acima, junto:

```
produto chega
   |
   v
vocabulário local  ---- achou tags? ----> pronto, O(1), determinístico
   |
   | não achou nada
   v
cache em disco  ---- já perguntamos antes? ----> pronto, O(1)
   |
   | nunca visto
   v
modelo (frase inteira, categoria de um enum fechado)
   |
   v
grava no cache  ->  nunca mais pergunta
```

Quatro regras, cada uma vinda de um erro medido:

**O vocabulário manda.** O modelo só é chamado quando o produto ficaria sem
nenhuma tag, ou seja, quando ele seria invisível na busca de qualquer jeito.
Nunca para completar tags que já existem — misturar as duas fontes é o que
criava `calcado` de um lado e `calcados` do outro.

**A pergunta é sobre a frase, não sobre a palavra.** É a diferença entre uma
pergunta sem resposta e uma com.

**A resposta é um enum, não um texto.** O modelo não pode inventar variação.

**Tudo vai para cache em disco.** Cada produto é perguntado uma vez na vida.

## Uma quarta melhoria: aprender a palavra, não a frase

O desenho acima funcionava, mas tinha um desperdício que só aparece olhando o
arquivo gerado:

```json
"frigideira antiaderente de ceramica com cabo de madeira": "cozinha"
```

O que foi guardado é **um produto**, não a palavra "frigideira". Cadastrar uma
"Frigideira de teflon" seria uma entrada totalmente nova: outra consulta ao
modelo, outros 600 ms, outra linha no arquivo. O sistema não generalizava nada.

### A tentativa de pedir a palavra ao modelo

O caminho óbvio era pedir junto da categoria: qual palavra do texto nomeia o
produto? Testamos. O modelo devolveu a **frase inteira** em sete de oito casos,
mesmo com a instrução "copie a palavra exatamente como ela aparece no texto,
sem traduzir nem flexionar".

É o mesmo padrão da tentativa 1, em outra roupa: o campo era do tipo `String`,
e `String` não restringe nada. Instrução em prompt continua sendo pedido, não
garantia. Diferente da categoria, que é um enum e por isso não tem como sair
errada.

### A regra que ganhou do modelo

A observação que resolveu: em português, nome de produto começa pelo
substantivo. *Frigideira* antiaderente, *Esteira* ergométrica, *Trena* a laser,
*Panela* de pressão. A palavra principal é simplesmente a primeira, depois de
descartar as palavras de ligação — coisa que o tokenizador do projeto já fazia.

```python
def palavra_principal(texto):
    palavras = tokenizar(texto)
    return palavras[0] if palavras else None
```

Medindo em dezesseis nomes de produto: **dezesseis acertos**. O modelo tinha
acertado um em oito.

Vale parar nesse contraste, porque ele é o resumo do projeto inteiro: numa
tarefa de extração, três linhas de regra determinística bateram um modelo de
bilhões de parâmetros. A regra não é mais "inteligente" — ela só está explorando
uma estrutura que existe no problema e que o modelo não tem motivo para
respeitar.

A divisão final ficou assim: **a regra escolhe a palavra, o modelo diz a
categoria.** Cada um na parte em que é melhor.

### O problema que a generalização cria

Generalizar é perigoso quando a palavra serve a coisas diferentes. Dois
produtos que já estavam no arquivo mostram isso:

```
"jogo de chaves de fenda": "ferramenta"
"jogo de facas de cozinha": "cozinha"
```

Aprender que "jogo" é ferramenta faria o jogo de facas ser classificado errado.
E "guarda" tem o mesmo defeito: guarda-chuva é acessório, guarda-roupa é móvel.

A defesa não precisa de lista escrita à mão, porque o conflito é detectável
sozinho: se a mesma palavra aparece com duas categorias, ela não serve de
atalho. Ela é removida das generalizações e marcada como ambígua; aqueles
produtos voltam a depender da frase inteira, que continua guardada.

Rodando sobre os 32 produtos já aprendidos, o sistema avisou sem ninguém
mandar:

```
a palavra 'jogo' aparece como 'ferramenta' e como 'cozinha';
deixou de ser usada para generalizar
```

E o resultado fica correto dos dois lados:

```
Jogo de chaves de fenda  -> ferramenta
Jogo de facas de cozinha -> cozinha
Jogo de tabuleiro        -> (nenhuma categoria; seria chute)
```

A última linha é deliberada. Um "jogo" desconhecido não herda nenhuma das duas
categorias, porque herdar seria adivinhar.

### O ganho, medido

Com 32 produtos e 30 palavras aprendidas, cadastramos quinze produtos
**nunca vistos**, todos usando palavras já conhecidas:

```
15 produtos novos
  resolvidos sem o modelo : 15
  precisariam do modelo   : 0
  tempo total             : 0,175 ms
```

Antes da generalização, os quinze exigiriam uma consulta cada: cerca de nove
segundos. O arquivo também cresceria quinze linhas, em vez de nenhuma.

É a mesma ideia de cache que aparece no resto do projeto, só que num nível
acima: em vez de lembrar respostas, o sistema passou a lembrar **regras**.

## O que isso resolve

| | só vocabulário | só modelo | desenho final |
|---|---|---|---|
| consistência entre produtos | sim | não | sim |
| reconhece palavra nova | não | sim | sim |
| nunca inventa atributo | sim | não | sim |
| velocidade por produto | 0,0068 ms | ~600 ms | 0,0068 ms depois da 1ª vez |
| produto parecido com um já visto | — | ~600 ms | 0,012 ms, sem consultar |
| roda sem Apple Intelligence | sim | não | sim |

A última linha é a que fecha a questão da portabilidade, e vale explicar.

O que foi aprendido fica em `dados/aprendido.json`, versionado junto com o
projeto:

```json
{
  "palavras": {
    "cafeteira": "cozinha",
    "frigideira": "cozinha",
    "trena": "ferramenta"
  },
  "frases": {
    "jogo de chaves de fenda": "ferramenta",
    "jogo de facas de cozinha": "cozinha"
  },
  "ambiguas": ["jogo"]
}
```

As três seções têm papéis distintos. `palavras` é o que generaliza e torna o
aprendizado útil. `frases` guarda o texto completo, tem precedência sobre a
palavra (uma correção feita à mão precisa valer contra a regra genérica) e é o
único recurso quando a palavra é ambígua. `ambiguas` registra os conflitos
detectados.

Uma máquina sem Apple Intelligence não aprende nada novo, mas aproveita tudo que
já foi aprendido em outra. **O conhecimento mora no arquivo, não no modelo.**
É o que permite que o trabalho seja avaliado em qualquer computador sem perder
o que o modelo ensinou.

Note que até a resposta "desconhecida" é guardada. Lembrar que o modelo não
soube evita perguntar de novo, toda vez, sobre o mesmo produto — mas ela nunca
vira tag, porque uma tag "desconhecida" apontaria para todos os produtos
estranhos do catálogo e não ajudaria ninguém a achar nada.

## Como usar

```bash
python3 main.py              # só o vocabulário
python3 main.py --aprender   # consulta o modelo para produtos desconhecidos
```

Na primeira vez, a ponte Swift é compilada sozinha. Se o modelo não estiver
disponível, o programa explica o motivo e segue só com o vocabulário, em vez de
encerrar. Se ele falhar no meio do uso, o programa desiste de consultá-lo pelo
resto da execução e avisa na tela — sem isso, cada produto esperaria o tempo
limite inteiro e cadastrar dez produtos levaria minutos para não aprender nada.

## A conclusão que vale levar para a apresentação

A expectativa era que usar inteligência artificial dispensasse parte do trabalho
de estrutura de dados. Aconteceu o contrário: **o modelo não dispensou nenhuma
decisão deste projeto.**

A saída dele veio com acento, repetida, com tags de duas palavras, em português
de Portugal, e com atributos inventados. Tudo isso teve que passar pela mesma
normalização que o vocabulário já usava, pelo mesmo cuidado com forma canônica,
e acabou guardado na mesma estrutura — uma tabela hash.

O modelo resolveu um problema real, que era o vocabulário fechado. Ele não
resolveu, e não poderia resolver, o problema de garantir que a mesma categoria
sempre vire a mesma chave. Isso continua sendo trabalho de estrutura de dados.

## Decisão final: o modelo no caminho principal

Depois de tudo acima, o modo `--ia` passou a consultar o modelo para **todo**
produto, e não só para os que o vocabulário não reconhece. É o que o item 2 do
enunciado descreve, e vale explicar por que isso deixou de ser arriscado.

O problema que motivava manter o modelo de fora era a inconsistência: ele dizia
`calcado` para um produto e `calcados` para outro, e as duas viravam chaves
diferentes na tabela hash. Mas esse defeito era da **primeira tentativa**, com
tags em texto livre. Desde que a resposta passou a ser um enum fechado, o modelo
é estruturalmente incapaz de produzir uma variação — `calcados` não existe no
tipo. A objeção caiu junto com a causa dela.

O que não mudou foi a outra limitação medida: o modelo inventa atributos. Por
isso a divisão de trabalho continua, só que com os papéis invertidos na ordem:

```
Tênis azul para corrida em asfalto
  -> esporte, calcado, azul, cor, corrida, asfalto, rua
     ^^^^^^^ do modelo        ^^^^^^^^^^^^^^^^^^^^^^^^ do vocabulário
```

A categoria encabeça a lista e vem do modelo; cor, material e uso continuam
vindo do vocabulário, que só reporta o que está escrito no texto.

O custo ficou menor do que a estimativa inicial sugeria:

```
só vocabulário.........:   0,0115 ms por produto
--ia, primeira vez.....: 178,9    ms por produto
--ia, com cache........:   0,0185 ms por produto
```

A terceira linha é o ponto. Depois que um produto foi visto, ou que a palavra
que o nomeia foi aprendida, o modo com modelo custa praticamente o mesmo que o
vocabulário puro. O preço é pago uma vez, e as duas evoluções anteriores — o
cache e a generalização por palavra — é que o amortizam.
