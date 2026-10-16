# Quatro evoluções, e o que cada uma ensinou

Documento 7 de 7. Depois que o sistema de aprendizado estava funcionando, um
diagnóstico do estado dele apontou fraquezas concretas. Este documento conta o
que foi feito sobre cada uma — incluindo duas em que o resultado contrariou a
expectativa, e dois defeitos sérios que só apareceram porque medimos em vez de
confiar.

## O diagnóstico que começou tudo

Três medições sobre o catálogo já construído:

```
PRODUTO DO VOCABULARIO
  Tenis azul para corrida em asfalto   7 tags: calcado, esporte, azul, cor, ...
  Camisa branca de algodao             5 tags: vestuario, branco, cor, ...

PRODUTO APRENDIDO PELO MODELO
  Frigideira antiaderente de ceramica  1 tag:  cozinha
  Furadeira de impacto com maleta      1 tag:  ferramenta
```

Produto aprendido era cidadão de segunda classe: sete tags contra uma. A
frigideira perdia "ceramica", "madeira" e "antiaderente", e quem filtrasse por
cerâmica não a encontrava.

As outras duas: quatro categorias nunca usadas (que acabaram se revelando um
bom sinal, não um defeito — são exatamente as que o vocabulário já cobre, então
nunca chegam ao modelo) e três palavras truncadas por nome composto.

## Evolução 1: nomes compostos

A regra que escolhe a palavra principal pegava a primeira palavra do nome. Como
o hífen virava espaço, "Guarda-chuva" virava "guarda".

O problema não é estético. "Guarda-roupa" também começa com "guarda" e é um
móvel, não um acessório. Os dois colidiriam na mesma chave, a detecção de
ambiguidade marcaria "guarda" como ambígua, e **as duas** perderiam a
generalização — por um defeito de normalização, não por serem de fato ambíguas.

A correção foi apagar o hífen em vez de transformá-lo em espaço, mas só entre
letras, para "aro 15 - novo" não virar "15novo":

```
Guarda-chuva  -> guardachuva
Guarda-roupa  -> guardaroupa
Micro-ondas   -> microondas
```

Duas palavras distintas, como de fato são. O par guarda-chuva / guarda-roupa
ficou no script de povoamento como prova permanente de que convivem.

### O efeito colateral: entradas órfãs

A mudança quebrou o arquivo existente. "Guarda-chuva" tinha sido gravado como
"guarda chuva", e a consulta passou a gerar "guardachuva" — chave diferente, e
a entrada deixou de ser encontrada apesar de continuar lá.

Daí uma decisão que vale além deste caso: o professor **renormaliza as chaves
ao ler o arquivo**, em vez de usá-las como estão. Assim qualquer ajuste futuro
na normalização migra o arquivo sozinho, na primeira abertura.

## Evolução 2: um terceiro índice, literal

A lacuna das sete tags contra uma pedia uma solução que não dependesse do
modelo acertar mais coisas.

A resposta foi um segundo índice invertido, com um critério diferente: em vez
de guardar as tags (que são significado), guardar as palavras que estão
literalmente escritas no produto.

```
cozinha    indice de tags: 1   indice de texto: 0
ceramica   indice de tags: 0   indice de texto: 1
calcado    indice de tags: 1   indice de texto: 0
corrida    indice de tags: 1   indice de texto: 1
```

A tabela resume por que os dois precisam existir. Achar "calcado" no tênis
exige **saber** que tênis é um calçado — só o índice semântico faz. Achar
"ceramica" na frigideira exige apenas que a palavra esteja lá — só o literal
faz, e sem depender de vocabulário nenhum. "Corrida" cai nos dois.

O custo é o de sempre em índice invertido: mais memória e mais um lugar para
manter coerente na remoção. O teste
`test_remocao_limpa_o_indice_literal` existe porque esquecer o segundo índice
ao remover deixaria identificadores órfãos — o mesmo bug que o documento 3
descreve, agora com uma chance a mais de acontecer.

## Evolução 3: inferir regras do próprio catálogo

Esta é a única parte do projeto que aprende sem consultar nada: nem modelo, nem
internet, nem vocabulário.

O raciocínio é estatístico. Se existem três produtos cujo texto contém "inox" e
todos os três têm a tag "cozinha", propõe-se a regra `inox -> cozinha`. A
informação já estava no catálogo, espalhada entre os produtos; faltava cruzar
os dois índices invertidos para enxergá-la.

Vale notar de onde vem a capacidade de fazer isso. O índice literal responde
"quais produtos contêm esta palavra" em O(1). Sem ele, a mesma pergunta
exigiria varrer o catálogo inteiro uma vez por palavra. É um caso em que a
estrutura escolhida no começo do projeto habilitou um uso que não estava
previsto quando ela foi criada.

O critério é rígido de propósito: a tag precisa estar em **todos** os produtos,
não na maioria. Uma regra que vale em nove de dez casos não é regra, é um
palpite que vai errar o décimo em silêncio.

### E ela erra pelo mesmo motivo que o modelo

O primeiro teste real sugeriu `inox -> cozinha`, com três produtos
concordando. A regra é ruim: inox é um material, e um parafuso de inox não é
cozinha. Os três produtos eram todos de cozinha, então qualquer palavra comum a
eles viraria "cozinha".

É exatamente o erro que o modelo cometeu ao classificar "dobravel" como
calçado: generalizar a partir de evidência enviesada. A diferença é que aqui a
evidência fica à vista — a sugestão informa quantos produtos concordam — e nada
é gravado. A pessoa decide.

## Evolução 4: medir a confiança do modelo

Temperatura zero esconde uma informação. Ela faz o modelo responder sempre
igual, mas não diz nada sobre o quanto ele estava seguro: uma classificação
óbvia e um chute entre duas opções parecidas saem com a mesma cara de certeza.

A ideia foi perguntar a mesma coisa cinco vezes, com o modelo livre para variar.
Se as respostas concordam mesmo assim, a classificação é firme; se se espalham,
ele estava em cima do muro. É uma medida indireta, porque o framework não expõe
as probabilidades internas — a estabilidade da resposta é o que dá para medir
de fora.

### O resultado contrariou a expectativa

Testamos contra as sete classificações que uma pessoa teve de corrigir à mão,
mais cinco que o modelo acertou:

```
erros do modelo detectados pela instabilidade: 3 de 7
erros que passaram despercebidos............: 4
alarmes falsos (certo mas instavel).........: 1 de 5
```

E na reconstrução seguinte da base, a instabilidade marcou quatro produtos —
caderno, micro-ondas, quebra-cabeça e tapete. **Os quatro estavam
classificados corretamente.**

A conclusão é desconfortável e vale registrar como ela é: **estabilidade não é
correção**. O modelo estava consistentemente errado em cafeteira, chaleira,
carrinho e secador, e repetir a pergunta não ajuda quando ele tem uma convicção
equivocada.

O recurso ficou, mas com o papel que os números sustentam: ele roda só na
construção da base (não no uso normal, onde custaria cinco vezes mais tempo) e
serve para **ordenar o que revisar primeiro**, nunca para decidir o que está
certo. Um sinal fraco bem compreendido é mais útil que um sinal forte
imaginado.

## Os dois defeitos que a verificação pegou

Nenhum dos dois apareceria sem olhar o resultado. Os dois são do tipo que faz um
sistema parecer funcionar enquanto erra.

### A correção humana virando ambiguidade

Depois de implementar a generalização, o relatório do povoamento mostrou:

```
Palavras descartadas por ambiguidade: cafeteira, carrinho, chaleira,
colchao, racao, secador, trena
```

São exatamente as sete que uma pessoa tinha corrigido. O modelo gravara
`cafeteira -> eletronico`; a correção dizia `cozinha`; e o código leu isso como
"a palavra aparece com duas categorias" em vez de "alguém consertou esta
frase".

Faltava uma distinção: a **mesma frase** mudando de categoria é correção e deve
substituir; **frases diferentes** com a mesma palavra e categorias distintas é
ambiguidade e deve descartar.

Dava para remendar com um caso especial, mas a causa raiz era a lógica acumular
estado em vez de derivá-lo. A solução foi recalcular todas as generalizações a
partir das frases, do zero, a cada mudança. Custa O(n) sobre algumas dezenas de
entradas — irrelevante — e em troca o resultado passou a depender só do
conteúdo atual, nunca da ordem em que as coisas aconteceram.

### A otimização que cegava a detecção do próprio erro

Este é o mais interessante dos dois.

Depois do conserto acima, a ambiguidade de "jogo" **desapareceu**, e todo jogo
virou cozinha — inclusive os de tabuleiro. A ordem da lista de produtos
explicava:

1. "Jogo de facas de cozinha" é processado primeiro, o modelo diz `cozinha`, e
   o sistema aprende que "jogo" é cozinha;
2. "Jogo de chaves de fenda" chega depois, e **a generalização responde
   `cozinha` antes de o modelo ser consultado**. A frase nunca é gravada, e a
   contradição entre os dois nunca aparece.

O atalho impediu o sistema de descobrir que o atalho estava errado.

A correção separa duas coisas que pareciam uma: **montar a base não é a mesma
coisa que usá-la**. No uso normal, a generalização responder sem consultar o
modelo é exatamente o que se quer. Na construção, ela atrapalha — ali o
objetivo é ouvir o modelo sobre cada produto para que os conflitos tenham
chance de aparecer. O script de povoamento desliga o atalho.

### Um terceiro, de brinde

Logo depois, a base ficou com 19 produtos em vez de 34. O script parava no meio.

Causa: ele tratava **qualquer** aviso como falha fatal do modelo, e a detecção
de ambiguidade também gera aviso. Descobrir que "jogo" é ambíguo é o sistema
funcionando, não quebrando. Hoje só `modelo_falhou` interrompe o lote.

## O defeito do violão: "ter tag" não é "saber o que é"

Este apareceu demonstrando o programa, com tudo supostamente pronto.

```
[P008] Violao acustico — nylon, material
```

Nenhuma das duas tags diz que aquilo é um instrumento. E o painel mostrava
`Produtos aprendidos: 34 (0 nesta execução)`: o modelo **não tinha sido
consultado**, mesmo diante de um produto que o sistema claramente não conhecia.

A causa estava na regra que decidia quando chamar o professor. Ela dizia: só
quando o produto ficar **sem nenhuma tag**. O vocabulário reconheceu "nylon"
em "cordas de nylon", devolveu `nylon` e `material`, e isso bastou para o
sistema concluir que já sabia o suficiente. Uma palavra acessória da descrição
bloqueou a classificação do produto inteiro.

O critério confundia duas coisas diferentes. "Azul" e "material" descrevem
**como** o produto é; "calcado" e "cozinha" dizem **o que** ele é. Só o segundo
grupo responde à pergunta que importa para um catálogo.

A correção foi trocar o critério por "não tem nenhuma tag de categoria", e
fazer a resposta do modelo **somar** às tags existentes em vez de substituí-las:

```
Violao acustico  — nylon, material, audio
Cadeira de couro — couro, material, movel
Tapete azul      — azul, cor, decoracao
```

As duas fontes passam a cooperar: o vocabulário sabe de materiais e cores, o
modelo sabe de categorias, e cada um contribui com o que sabe.

### O problema era maior do que o violão

Medindo o critério antigo contra o novo em dez produtos variados:

```
Violao acustico    -> nylon, material     sem categoria
Cadeira de couro   -> couro, material     sem categoria
Cortina de algodao -> algodao, material   sem categoria
Tapete azul        -> azul, cor           sem categoria

consultas pelo criterio antigo: 0 de 10
consultas pelo criterio novo..: 4 de 10
```

**Quatro em cada dez produtos estavam no catálogo sem nada que dissesse o que
eram** — e o critério antigo não consultava o modelo em nenhum deles, porque
todos tinham *alguma* tag. Uma cadeira de couro não era móvel, um tapete não
era decoração. O defeito estava escondido atrás de uma lista de tags que
parecia preenchida.

O custo da correção ficou abaixo do previsto. Cadastrando os três produtos
problemáticos, o modelo foi consultado **uma vez só**: "cadeira" e "tapete" já
estavam entre as palavras generalizadas, vindas de outros produtos. As duas
evoluções se ajudam — a generalização paga parte do custo que o critério mais
exigente introduziu.

### Uma lista em duas linguagens

A correção precisa saber quais tags são categorias, e essa lista já existia
como enum no Swift. Duplicá-la em Python cria um risco silencioso: acrescentar
uma categoria de um lado e esquecer do outro faria o Python tratá-la como
atributo comum e consultar o modelo à toa.

Em vez de confiar na disciplina de quem edita, o teste
`test_categorias_batem_com_o_enum_do_swift` lê o arquivo Swift, extrai os casos
do enum e compara com a constante Python. Se os dois divergirem, a suíte falha.

### O que ficou de limitação

O violão foi classificado como `audio`. Não é errado, mas é o enum forçando uma
escolha: não existe categoria para instrumento musical. A lista de categorias é
fechada de propósito — é ela que garante que o modelo não invente variações —, e
o preço é que produtos fora dela caem na categoria menos ruim disponível.

Acrescentar categorias é fácil (uma linha no Swift, uma no Python, e o teste
garante que as duas acompanhem). Decidir quais acrescentar é que é trabalho de
quem conhece o catálogo.

## O estado final

```
dados/aprendido.json
  frases    34 produtos     o que foi aprendido, texto a texto
  palavras  32 generalizam  valem para qualquer produto que as use
  ambiguas  jogo            serve a mais de uma categoria; não generaliza
  revisar   4 produtos      o modelo hesitou; vale alguém olhar
```

E no catálogo, três tabelas hash em vez de duas: produtos por identificador,
tags por significado, palavras por literal.

A lição que atravessa as quatro evoluções é a mesma das anteriores, e ficou mais
forte: cada vez que medimos em vez de assumir, o resultado foi diferente do
esperado. A regra de três linhas ganhou do modelo na extração; a generalização
criou um bug que ela mesma escondia; e a medida de confiança que parecia
elegante revelou-se fraca. Nenhuma dessas coisas apareceria em um projeto que
só verificasse se o programa roda sem erro.
