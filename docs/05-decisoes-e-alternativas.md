# Decisões e alternativas

Documento 5 de 5. Um registro do que foi considerado e descartado em cada
encruzilhada do projeto.

Este documento existe por um motivo prático: na apresentação, a pergunta mais
provável não é "como funciona", é "por que assim e não de outro jeito". Decisão
sem alternativa registrada é decisão que ninguém tomou de verdade — simplesmente
aconteceu.

---

## 1. Linguagem: Python

**Alternativas:** C, Java.

C seria a escolha mais tradicional da disciplina: ponteiros explícitos,
`malloc`/`free`, e a estrutura literalmente visível na memória. Java daria
orientação a objetos mais formal.

Python foi escolhido porque toda a parte de manipulação de texto — normalização
Unicode, remoção de acentos, separação em palavras — fica curta e legível, o que
deixa o foco do código na estrutura de dados em vez de em gerenciamento de
strings. O risco assumido é alguém olhar e pensar "Python já tem dicionário,
então não implementou nada". Por isso o projeto inteiro é explícito sobre não
usar `dict` no núcleo, e por isso este documento existe.

---

## 2. Tabela hash escrita do zero

**Alternativa:** usar o `dict` do Python, que o enunciado permite ao dizer
"Tabela de Dispersão (Hash Table) ou Dicionários".

O `dict` do Python **é** uma tabela hash, só que escondida. Usá-lo entregaria o
uso da estrutura, não a estrutura. Função de dispersão, colisão, fator de carga
e redimensionamento — justamente o conteúdo avaliado — ficariam invisíveis.

Onde o `dict` ainda aparece no projeto: em `estatisticas()`, que devolve um
dicionário de resultados (ali ele é um formato de retorno, não uma estrutura de
busca), e em uma função auxiliar de teste, com comentário explicando a diferença.

---

## 3. Função de dispersão própria em vez de `hash()`

**Alternativa:** usar o `hash()` nativo do Python.

Além do motivo acima, existe o impedimento técnico: desde o Python 3.3 o `hash()`
de strings é aleatorizado a cada execução. A mesma chave cairia em baldes
diferentes em execuções diferentes, tornando impossível testar a distribuição ou
demonstrar o comportamento em sala. Detalhes no documento 1.

---

## 4. Analisador de tags local em vez de API de IA

**Alternativa:** chamar um serviço de inteligência artificial, como o enunciado
sugere literalmente.

Esta é a maior divergência em relação ao enunciado, e está detalhada no
documento 2. Resumo: dependência de internet na apresentação, resultado que varia
entre execuções (impossível testar), e a parte interessante do trabalho viraria
uma chamada HTTP em vez de estrutura de dados.

**Esta decisão deve ser confirmada com o professor antes da entrega.** O ponto de
troca está isolado numa classe só (`GeradorDeTags`), então adaptar é barato se
for exigido.

---

## 5. Colisão por encadeamento separado

**Alternativa:** endereçamento aberto (sondagem linear ou duplo hash).

Endereçamento aberto economiza memória e aproveita melhor o cache do
processador, porque mantém tudo em um vetor contíguo. Remover exige marcar
células como "apagadas", e no encadeamento basta religar dois ponteiros.

Esta era a justificativa até ela ser medida. A alternativa foi implementada em
`catalogo/hashtable_aberta.py` e comparada em `ferramentas/benchmark_colisoes.py`, e o
resultado corrigiu a explicação:

- a degradação por acúmulo de marcadores **não apareceu**: após 20 mil ciclos
  de remoção e inserção, o custo de busca ficou igual;
- a desvantagem real é o **agrupamento primário** da sondagem linear, que faz o
  custo explodir conforme a tabela enche — 62 comparações por busca com
  ocupação de 0,95, contra 1,28 do encadeamento;
- a economia de memória é de apenas 8%, bem menos do que se costuma supor.

A escolha continua a mesma, mas agora pelo motivo certo. Detalhes e tabelas em
[docs/01](01-tabela-hash.md).

---

## 6. Nós encadeados próprios em vez de `list` nos baldes

**Alternativa:** guardar uma lista do Python dentro de cada balde.

Daria o mesmo resultado com menos código. Mas uma lista do Python é um vetor
dinâmico, não uma lista encadeada: memória contígua, redimensionamento
automático. O encadeamento — conteúdo da disciplina — ficaria escondido atrás da
implementação da linguagem. A classe `_No`, com seu campo `proximo`, existe para
que ele fique visível.

---

## 7. Fator de carga máximo de 0.75

**Alternativas:** 0.5 (mais rápido, gasta mais memória), 1.0 (economiza memória,
correntes mais longas).

0.75 é o valor usado pelo `HashMap` do Java e é um meio-termo consolidado. Com
ele, a maior parte dos baldes tem zero ou um elemento, e redimensionamentos
acontecem com pouca frequência. Está exposto como constante de classe
(`FATOR_CARGA_MAXIMO`) justamente para poder ser alterado e observado.

---

## 8. Capacidade sempre em número primo

**Alternativa:** potências de dois, que permitiriam trocar o custoso `%` por uma
operação de bits (`& (capacidade - 1)`), bem mais rápida.

A otimização por bits é real e muito usada — o Java faz isso. Mas ela exige uma
função de dispersão de qualidade alta, porque com potência de dois o `&` só olha
os bits menos significativos do hash; se eles forem pouco variados, as chaves se
concentram. O número primo é mais tolerante a uma função de dispersão mediana, e
o ganho de velocidade não faria diferença perceptível na escala deste trabalho.

---

## 9. Tags guardadas sem acento

**Alternativa:** guardar "calçado" com cedilha e normalizar só na hora da busca.

Tag é chave de hash, e hash exige igualdade exata. Guardar na forma canônica
elimina na origem uma categoria inteira de bug — aquele em que o produto está
cadastrado, a busca parece certa, e mesmo assim nada é encontrado.

O custo é estético: a interface mostra "calcado" em vez de "calçado". Daria para
resolver guardando um rótulo bonito junto de cada tag, mas isso é polimento
visual que não acrescenta nada à estrutura de dados.

---

## 10. Duas tabelas em vez de uma

**Alternativa:** só a tabela de produtos, varrendo tudo para buscar por tag.

Esta é a decisão mais importante do projeto e tem um documento inteiro (o 3) e
um benchmark (o 4) dedicados a ela. A alternativa é O(n) por busca; a escolhida é
O(1) para localizar mais O(k) para montar o resultado. Custa memória duplicada e
a obrigação de manter as duas tabelas coerentes na remoção.

---

## 11. Onde deliberadamente NÃO otimizamos

Vale registrar, porque mostra que a escolha de estrutura foi pensada caso a caso
em vez de aplicada por reflexo.

**Eliminar tags repetidas usa `if tag not in tags`**, que é busca linear. Um
produto tem menos de dez tags; montar uma estrutura de hash para dez itens
custaria mais tempo do que economizaria. Otimizar aqui seria otimizar o lugar
errado.

**`tags_conhecidas()` ordena a lista a cada chamada.** É usada só para exibir o
menu, uma vez, com interação humana no meio. Guardar uma versão ordenada em cache
adicionaria um estado a manter sincronizado em troca de microssegundos que
ninguém perceberia.

**`buscar_por_tags` monta tabelas hash temporárias** — e aqui a decisão foi a
oposta. A diferença também é pequena com listas curtas, mas a alternativa seria
um laço linear dentro de outro laço, ou seja, custo quadrático. Trocar O(k·m) por
algo que multiplica pelo tamanho das listas é o tipo de coisa que funciona nos
testes e derruba o sistema em produção.

A regra que guiou os três casos: aceitar busca linear quando o conjunto é
comprovadamente pequeno e não cresce; recusar quando ela estiver dentro de um
laço que depende do tamanho dos dados.

---

## 12. Sem persistência em arquivo

**Alternativa:** salvar o catálogo em JSON ou SQLite.

O catálogo só existe na memória e some ao fechar o programa. Salvar em arquivo é
assunto de serialização ou banco de dados, e não acrescentaria nada ao que o
enunciado pede. Também traria uma decisão nova e não trivial: reconstruir o
índice invertido ao carregar, ou salvá-lo também e arriscar que ele fique
dessincronizado dos produtos.

---

## 13. Formas femininas listadas em vez de regra de gênero

**Alternativa:** uma regra trocando "a" final por "o".

A regra quebraria palavras legítimas: "rosa" viraria "roso", "marca" viraria
"marco", "camisa" viraria "camiso". Uma regra que erra em silêncio é pior que
nenhuma regra, porque o erro só aparece como tags faltando em produtos
aleatórios.

Listar as cinco cores que mudam de gênero é menos elegante, mais previsível, e
cada caso é verificável. Esta decisão veio depois de um defeito real encontrado
rodando o programa, não de planejamento — está contada no documento 2.

---

## 14. `unittest` em vez de `pytest`

`unittest` vem junto com o Python. `pytest` tem sintaxe mais enxuta, mas exigiria
`pip install` para qualquer pessoa que fosse rodar o trabalho — incluindo o
professor, na máquina dele, possivelmente sem internet. Zero dependências
externas era um requisito autoimposto do projeto, e ele vale para os testes
também.
