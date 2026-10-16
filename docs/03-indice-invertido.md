# O índice invertido

Documento 3 de 5. Por que uma tabela hash só não resolve o problema do
enunciado, e o que a segunda tabela muda.

Código correspondente: `catalogo/catalogo.py`.

## A armadilha

O enunciado, no item 3, manda "armazenar o produto em uma Tabela de Dispersão".
A leitura imediata é essa:

```
tabela de produtos
P001 -> Produto("Tênis azul", tags=[calcado, esporte, azul, corrida])
P002 -> Produto("Camisa azul", tags=[vestuario, azul, algodao])
P003 -> Produto("Chuteira preta", tags=[calcado, futebol, preto])
```

Está correto, e resolve bem a pergunta "me mostre o produto P002": uma conta de
hash e acesso direto, O(1).

Mas o item 4 pede outra coisa: "implementar uma função de busca que use essas
tags para encontrar os produtos". E com essa estrutura, buscar por `azul` ficaria
assim:

```python
def buscar(self, tag):
    encontrados = []
    for produto in todos_os_produtos:      # <- aqui mora o problema
        if tag in produto.tags:
            encontrados.append(produto)
    return encontrados
```

Esse laço percorre o catálogo inteiro. Com 100 mil produtos, são 100 mil
iterações para achar talvez três. O custo é O(n) — exatamente o custo que a
tabela hash existe para evitar.

Vale parar neste ponto, porque é a lição principal do projeto: **a estrutura
estava certa, mas respondendo à pergunta errada.** A tabela foi construída para
achar coisas pela chave "identificador do produto", e a busca precisa achar
coisas pela chave "tag". Como a tag não é a chave, o hash não ajuda em nada.

## A inversão

Se o problema é que a tag não é a chave, a solução é fazer dela uma chave. Isso
significa uma segunda tabela, construída ao contrário:

```
tabela de produtos              índice de tags
P001 -> Produto(Tênis azul)     calcado   -> [P001, P003]
P002 -> Produto(Camisa azul)    azul      -> [P001, P002]
P003 -> Produto(Chuteira preta) corrida   -> [P001]
                                vestuario -> [P002]
                                futebol   -> [P003]
```

Na primeira tabela a chave é o produto e o valor são seus dados. Na segunda, a
chave é a tag e o valor é a lista de quem a possui. Por isso o nome: o
relacionamento foi invertido.

Agora buscar `azul` é:

```python
identificadores = self._indice_tags.buscar("azul")   # O(1)
return [self._produtos.buscar(i) for i in identificadores]
```

Não há laço sobre o catálogo. O tamanho do catálogo sumiu da conta.

A ideia não é nova nem deste projeto: é exatamente o índice remissivo no fim de
um livro técnico. Em vez de ler o livro inteiro procurando "recursão", você olha
a palavra no índice e ela te entrega as páginas. Motores de busca funcionam com
a mesma estrutura, em escala maior.

## O preço

Nada disso é de graça. A informação "o produto P001 tem a tag azul" agora está
guardada em dois lugares: na lista de tags do produto e na lista de produtos da
tag. É duplicação deliberada.

O que ganhamos com isso é velocidade de busca; o que pagamos é memória e o dever
de manter as duas cópias coerentes. Essa troca entre espaço e tempo é uma das
decisões mais comuns em computação, e aqui ela foi feita com consciência: num
e-commerce, busca acontece milhares de vezes para cada cadastro, então faz todo
sentido gastar na escrita para economizar na leitura.

## Onde a duplicação cobra o preço: remover

Manter duas cópias significa que toda remoção precisa acontecer nos dois lugares.
Este é o bug clássico da estrutura:

```python
# ERRADO
def remover(self, identificador):
    return self._produtos.remover(identificador)
```

Parece certo. A listagem fica correta, o produto some, `len()` diminui. Mas o
identificador continua pendurado nas listas de tags do índice. Então:

```python
catalogo.remover("P001")
catalogo.buscar_por_tag("azul")   # devolve [None, <Camisa azul>]
```

A busca encontra "P001" no índice, vai procurar esse produto na primeira tabela,
não acha, e devolve `None` no meio dos resultados. O programa quebra na hora de
exibir, e o erro aparece **longe** de onde foi causado — numa função de busca que
está correta. É o tipo de bug que consome uma tarde inteira.

A versão certa limpa os dois lados, e ainda faz uma faxina:

```python
for tag in produto.tags:
    identificadores = self._indice_tags.buscar(tag)
    identificadores.remove(identificador)
    if not identificadores:
        self._indice_tags.remover(tag)
```

A última condição remove a tag do índice quando ela fica sem nenhum produto. Sem
isso, o índice só cresceria: tags órfãs acumulariam para sempre, ocupando baldes
e aparecendo na listagem de tags do catálogo como se existissem produtos com
elas.

Três testes guardam esse comportamento, em `testes/test_catalogo.py`:
`test_produto_removido_some_do_indice_de_tags`,
`test_tag_que_ficou_sem_ninguem_sai_do_indice` e
`test_produto_removido_some_da_busca_por_identificador`.

## Buscar por várias tags ao mesmo tempo

Filtrar por `azul` **e** `calcado` significa achar os produtos presentes nas duas
listas — uma interseção. Duas decisões aqui, as duas copiadas de motores de busca
de verdade.

**Desistir cedo.** Se qualquer uma das tags não existe no índice, o resultado é
necessariamente vazio. Devolvemos na hora, sem fazer trabalho nenhum.

**Começar pela tag mais rara.** As listas são ordenadas por tamanho e a menor
vira a lista de candidatos. Procurar os poucos produtos de `natacao` dentro do
conjunto `azul` é muito mais barato que o contrário, porque o número de
candidatos a verificar já começa pequeno. O resultado é o mesmo; o trabalho para
chegar nele, não.

Para testar se um candidato está nas outras listas, montamos uma `TabelaHash` na
hora e usamos ela como conjunto. Com listas pequenas isso é indiferente, mas a
alternativa (`if identificador in lista`, dentro de um laço) seria busca linear
dentro de busca linear, ou seja, custo quadrático. Seria estranho o projeto
inteiro defender O(1) e cair num laço aninhado justamente na função de busca mais
sofisticada.

## Um terceiro índice, acrescentado depois

O catálogo ganhou mais tarde um segundo índice invertido, com um critério
diferente: em vez das tags (que são significado), ele guarda as palavras
literalmente escritas no produto.

O motivo foi uma lacuna medida. Produtos classificados pelo modelo de
linguagem recebem uma única tag, enquanto os reconhecidos pelo vocabulário
recebem cinco ou sete. Uma "Frigideira antiaderente de cerâmica" ficava só com
a tag "cozinha", e quem procurasse "ceramica" não a achava — apesar de a
palavra estar escrita ali.

Os dois índices respondem a perguntas diferentes e nenhum substitui o outro:

```
cozinha    tags: 1   texto: 0    só semântico, a palavra não está no texto
ceramica   tags: 0   texto: 1    só literal, não é tag de nada
calcado    tags: 1   texto: 0    só semântico
corrida    tags: 1   texto: 1    os dois
```

O custo é o mesmo de antes, agora em dobro: mais memória e mais um lugar para
limpar na remoção. O teste `test_remocao_limpa_o_indice_literal` existe
justamente porque esquecer o segundo índice reproduziria o bug dos
identificadores órfãos descrito acima.

Detalhes e o que motivou cada escolha estão em
[docs/07](07-evolucoes.md).
