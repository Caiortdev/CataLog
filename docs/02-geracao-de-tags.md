# Geração de tags

Documento 2 de 5. Como o texto "Tênis azul para corrida em asfalto" vira a lista
`["calcado", "esporte", "azul", "cor", "corrida", "asfalto", "rua"]`.

Código correspondente: `catalogo/texto.py`, `catalogo/vocabulario.py` e
`catalogo/tagger.py`.

## Primeiro, uma questão a resolver com o professor

O enunciado diz, no item 2: "Pedir à IA que analise a descrição e gere tags
relevantes". Este projeto **não** chama nenhum serviço de inteligência
artificial. A análise é feita por regras escritas por nós.

Essa escolha foi deliberada, e vale confirmar com quem avalia antes da entrega.
Os motivos:

**Dependência externa na hora da apresentação.** Chamar uma API exige chave de
acesso, internet funcionando e o serviço estar no ar. Qualquer um dos três
falhando trava a demonstração.

**Resultado que muda sozinho.** Um modelo de linguagem pode devolver tags
diferentes para a mesma entrada em execuções diferentes. Isso inviabiliza testes
automatizados: não dá para escrever `assertEqual` em cima de algo que varia.

**A disciplina é Estrutura de Dados.** Chamando uma API, a parte interessante do
trabalho vira "fiz um POST e li um JSON". Fazendo a análise aqui, ela vira
manipulação de strings, normalização e consulta em tabela hash — que é o
conteúdo da matéria.

**Dá para explicar cada tag gerada.** Se o professor perguntar por que apareceu a
tag `rua`, a resposta está em uma linha do `vocabulario.py`. Com um modelo de
linguagem, a resposta honesta seria "não sei".

Se a exigência da API for inegociável, o ponto de troca é pequeno e está isolado:
basta trocar a classe `GeradorDeTags` por outra que faça a chamada HTTP. Todo o
resto do projeto — as duas tabelas hash, o índice, as buscas — continua igual,
porque nada mais depende de como as tags foram produzidas. Essa separação foi
pensada desde o começo.

## O algoritmo, em quatro linhas

```
para cada palavra útil do texto:
    está no vocabulário?       -> pega as tags dela
    não está? e no singular?   -> tenta de novo
    continua não achando?      -> ignora a palavra
```

O resto deste documento explica por que cada etapa é necessária.

## Normalização: o passo que torna o hash possível

Esta é a parte que conecta a análise de texto com a estrutura de dados, e é a
mais importante de entender.

Tabela hash funciona por **igualdade exata**. `hash("Tênis")` e `hash("tenis")`
são números completamente diferentes, porque o código do caractere "T" não tem
nada a ver com o do "t", nem o do "ê" com o do "e". Um caractere de diferença e
a chave vai parar em outro balde.

Agora pense no uso real. A pessoa cadastra "Tênis Azul". Outra busca por "tenis
azul". Uma terceira digita "TÊNIS, AZUL!". São a mesma coisa para um humano e
três chaves distintas para a tabela.

A solução é reduzir todas as variações a uma forma única antes de qualquer
coisa tocar o hash:

```python
def normalizar(texto):
    texto = remover_acentos(texto.lower())
    return "".join(c if c.isalnum() else " " for c in texto)
```

Três operações, nessa ordem:

**Minúsculas.** Resolve "TÊNIS" contra "tênis".

**Remover acentos.** Resolve "tênis" contra "tenis". O truque está em
`unicodedata.normalize("NFD", texto)`: a forma NFD do Unicode separa a letra do
acento em dois caracteres distintos — "ê" vira "e" seguido de um acento solto.
Depois disso basta descartar os caracteres da categoria `Mn` (*Mark,
nonspacing*), que é onde os acentos moram. A letra base sobrevive.

**Pontuação vira espaço.** Repare que a pontuação não é apagada, é substituída
por espaço. Se fosse apagada, "azul,corrida" viraria a palavra inexistente
"azulcorrida". Existe um teste só para isso:
`test_pontuacao_vira_espaco_e_nao_some`.

A mesma normalização é aplicada nos dois lados — no cadastro e na busca. É isso
que faz procurar "CALÇADO" encontrar um produto cuja tag foi guardada como
"calcado". Sem isso, a busca falharia de um jeito difícil de depurar, porque o
produto está lá e tudo parece certo.

## Stopwords: jogar fora o que não ajuda

Na frase "Tênis azul para corrida em asfalto", as palavras "para" e "em" não
distinguem nada. Praticamente toda descrição de produto tem alguma delas.

Se virassem tags, a tag `para` apontaria para metade do catálogo. Ela não
filtraria nada, mas ocuparia espaço no índice e apareceria na listagem de tags
poluindo tudo. Por isso existe a lista `STOPWORDS`.

O conceito vem de recuperação de informação, e a lógica é simples: um termo que
aparece em quase todos os documentos não serve para separá-los.

## O vocabulário mora dentro de uma tabela hash

Aqui está a parte do módulo que mais interessa à disciplina.

O vocabulário tem dezenas de termos, e é consultado **uma vez para cada palavra
de cada produto cadastrado**. Guardá-lo em uma lista e percorrer essa lista a
cada palavra custaria O(V), com V = tamanho do vocabulário. Para um produto com
8 palavras e um vocabulário de 70 termos, seriam até 560 comparações por
cadastro.

Carregando o vocabulário em uma `TabelaHash`, cada consulta é O(1). Um produto
com 8 palavras faz 8 consultas diretas, independentemente de o vocabulário ter
70 ou 70 mil termos.

É a mesma estrutura do catálogo resolvendo um problema completamente diferente.
Isso é um argumento forte na apresentação: mostra que a tabela hash não foi usada
porque o enunciado mandou, mas porque ela era a ferramenta certa — duas vezes,
em dois lugares distintos, pelo mesmo motivo.

O arquivo `vocabulario.py` guarda os dados como uma lista de tuplas, não como um
dicionário do Python. Não é capricho: quem faz o papel de dicionário neste
projeto é a nossa tabela. Ali é só o dado bruto, que o `GeradorDeTags` carrega
na estrutura ao iniciar.

## Plural, gênero, e o defeito que só apareceu rodando

A função `singularizar` é uma heurística ingênua: se a palavra termina em "s" e
tem mais de três letras, remove o "s".

Funciona para "camisas" para "camisa". Não funciona para "papéis" para "papel".
E tem um caso perigoso: "tenis" viraria "teni", que não existe.

A proteção contra isso não está na função, e sim na **ordem** em que ela é
chamada:

```python
encontradas = self._vocabulario.buscar(palavra)
if encontradas is not None:
    return encontradas
return self._vocabulario.buscar(singularizar(palavra))
```

Busca a palavra original primeiro. Como "tenis" está no vocabulário, ele é
encontrado de primeira e nunca chega a ser singularizado. Se a ordem fosse
invertida, o produto principal do enunciado perderia justamente as tags mais
importantes. Inverter essas duas linhas é o tipo de mudança que parece inofensiva
e quebra o sistema inteiro.

### O defeito do gênero

Este não apareceu escrevendo testes. Apareceu rodando o programa com os produtos
de exemplo e olhando a saída: **"Chuteira preta" saiu sem nenhuma tag.**

Duas causas somadas. "chuteira" não estava no vocabulário, e "preta" também não
— a regra de singular não sabe nada sobre gênero, então "preta" nunca viraria
"preto".

A correção óbvia seria escrever uma regra trocando "a" final por "o". Mas ela
estragaria palavras legítimas: "rosa" viraria "roso", "marca" viraria "marco",
"camisa" viraria "camiso". Uma regra que erra em silêncio é pior que nenhuma
regra.

A correção adotada foi listar as poucas cores que mudam de gênero
(`preta`, `branca`, `vermelha`, `amarela`, `roxa`) uma a uma no vocabulário.
Menos elegante, mais previsível, e cada caso é verificável.

Em seguida foi escrito o teste `test_cor_no_feminino_e_reconhecida` para que o
problema não volte sem ninguém perceber. Essa é a parte que vale registrar: o
teste nasceu de um defeito real encontrado em uso, não de uma lista de casos
imaginados antes.

## Buscar por frase usa o mesmo caminho

A função `buscar_por_texto` do catálogo passa a frase digitada pelo **mesmo
gerador de tags** usado no cadastro.

Esse detalhe é o que faz a busca funcionar. Se "Tênis azul" virou as tags X, Y e
Z na hora de cadastrar, a mesma frase digitada na busca vira X, Y e Z de novo.
Os dois lados falam a mesma língua porque passam pelo mesmo tradutor. Se a busca
tivesse a própria lógica de interpretar texto, qualquer diferença entre as duas
viraria um produto que existe mas não é encontrado.
