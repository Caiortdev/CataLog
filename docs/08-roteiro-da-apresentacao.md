# Roteiro da apresentação

Documento 8 de 8. Um plano para apresentar o trabalho em cerca de 12 minutos,
com o que mostrar na tela, os números a citar e as perguntas prováveis.

Não é um texto para decorar. São os pontos de apoio; a fala sai melhor com as
suas palavras.

---

## Antes de entrar na sala

**Teste tudo uma vez, na máquina que você vai usar.**

```bash
python3 -m unittest discover -s testes -t .
python3 ferramentas/benchmark.py
python3 ferramentas/benchmark_colisoes.py
python3 main.py --ia
```

**Abra três abas de terminal** já na pasta do projeto, uma para cada coisa que
você vai rodar. Trocar de aba é mais rápido e menos arriscado que digitar
comando na frente de todo mundo.

**Aumente a fonte do terminal.** As tabelas dos benchmarks têm colunas; se não
couberem na largura da tela, quebram e ficam ilegíveis.

**Deixe o `dados/aprendido.json` aberto em um editor**, em outra janela. Você vai
querer mostrá-lo.

**Se o Apple Intelligence não estiver disponível** na máquina da apresentação,
não é problema: rode sem `--ia`. Tudo funciona, inclusive as categorias já
aprendidas, porque elas estão no arquivo. Só diga isso em uma frase, para
ninguém achar que quebrou.

---

## A ideia que amarra a apresentação

Se der para levar uma frase só, é esta:

> Toda vez que medimos em vez de assumir, o resultado foi diferente do que a
> gente esperava — e duas decisões do trabalho mudaram por causa disso.

Ela funciona porque é verdade e porque é difícil de forjar. Qualquer grupo
mostra um programa rodando; mostrar onde você errou, como descobriu e o que
corrigiu é outra conversa.

---

## 1. O problema e a escolha da estrutura (1 min)

Diga o problema do enunciado em uma frase: um e-commerce precisa achar produtos
por característica, não por nome.

Depois mostre por que isso é um problema de estrutura de dados:

> Com os produtos em uma lista, achar todos os "azuis" custa percorrer o
> catálogo inteiro. Com 100 mil produtos, 100 mil comparações para achar talvez
> três. É O(n), e é o que a tabela hash existe para evitar.

Explique a ideia em uma frase: em vez de procurar onde o produto está, a tabela
**calcula** onde ele deveria estar.

**Não gaste mais que um minuto aqui.** Essa parte todos os grupos vão falar.

---

## 2. Demonstração (3 min)

```bash
python3 main.py --ia
```

**Opção 8** — carrega os produtos de exemplo. Mostre que as tags apareceram
sozinhas, ninguém digitou nenhuma.

Aponte o exemplo do enunciado:

```
[P001] Tênis azul — esporte, calcado, azul, cor, corrida, asfalto, rua
```

> As quatro tags que o enunciado pede estão aqui: calçado, esporte, corrida e
> azul. A primeira veio do modelo de linguagem, as outras do vocabulário.

**Opção 1** — cadastre algo que o sistema nunca viu. Sugestão: "Aspirador robô"
com descrição "com sensor de obstáculo". Nenhuma dessas palavras está no
vocabulário, e mesmo assim ele sai classificado como eletrônico.

**Opção 3** — busque `eletronico`. Vão aparecer produtos de tipos bem
diferentes: fone, mochila e o aspirador.

> Repare que estou buscando por característica, não por nome. É o item 4 do
> enunciado.

**Opção A** — busque uma palavra que está escrita no produto mas não é tag de
nada, como `aluminio` ou `sensor`.

> São dois índices diferentes. Um busca por significado, o outro por palavra
> escrita. Nenhum dos dois acha o que o outro acha.

**Opção 7** — abra as estatísticas e deixe na tela enquanto fala da próxima
parte.

---

## 3. Por que três tabelas, e não uma (2 min)

Com as estatísticas na tela, explique o índice invertido:

> A primeira tabela guarda produto por identificador. Mas o enunciado pede
> busca **por tag**, e a tag não é a chave — então o hash não ajudaria em nada.
> A estrutura estaria certa respondendo a pergunta errada.

Mostre a inversão:

```
tabela de produtos          índice de tags
P001 -> Tênis azul          calcado -> [P001, P003]
P002 -> Camisa azul         azul    -> [P001, P002]
```

> Virando a chave do avesso, buscar vira uma consulta direta. É a mesma ideia
> do índice remissivo no fim de um livro.

Agora o benchmark:

```bash
python3 ferramentas/benchmark.py
```

> Com 50 mil produtos, a busca com índice é 45 vezes mais rápida que varrer o
> catálogo. E o que importa não é o número: é que a coluna da varredura cresce
> junto com o catálogo e a do índice não.

**Se perguntarem por que o tempo do índice também subiu**, a resposta é boa:
ele cresce com o número de produtos **encontrados**, não com o tamanho do
catálogo. Dividindo pelo número de achados, dá constante.

---

## 4. Por que encadeamento, e onde eu errei (3 min)

Esta é a parte mais forte. Não corra.

```bash
python3 ferramentas/benchmark_colisoes.py
```

Comece pelo **experimento 1**:

> Com capacidade 1024, 316 baldes nunca recebem chave nenhuma — 31% da tabela
> é desperdício. Com 1031, que é primo, nenhum fica vazio.

Depois pule direto para o **experimento 5**, que é o mais visual:

```
ocupação   encadeamento   endereçamento aberto
   0.1          1.00              1.01
   0.5          1.17              4.60
   0.95         1.28             61.68
```

> Com a tabela vazia, as duas estratégias empatam. Conforme enche, o
> encadeamento quase não se mexe e o endereçamento aberto vai para 62
> comparações por busca. Quarenta e oito vezes pior.

Explique o agrupamento em uma frase: chave desviada ocupa a posição vizinha,
que desvia a próxima, e o bloco cresce sozinho.

**Agora o experimento 3, e a parte que vale a nota:**

> Eu tinha escrito na documentação que o endereçamento aberto perde porque
> degrada com remoções. Implementei a alternativa, rodei 20 mil ciclos de
> remoção e inserção, e o custo não subiu: 3,33 antes e 3,33 depois. A
> afirmação estava errada — eu tinha repetido teoria de livro sem verificar.

Abra `docs/01-tabela-hash.md` e mostre a correção, com a versão antiga
registrada ao lado do que os números disseram.

> O motivo real era o agrupamento, não as remoções. Corrigi o documento.

---

## 5. A inteligência artificial: o que resolve e o que não (2 min)

> O enunciado pede para a IA analisar a descrição. Usei o modelo que roda
> dentro do próprio Mac, sem internet e sem chave de API.

Mostre o `dados/aprendido.json`:

```json
{
  "palavras": { "frigideira": "cozinha", "trena": "ferramenta" },
  "frases":   { "jogo de chaves de fenda": "ferramenta" },
  "ambiguas": ["jogo"],
  "revisar":  [...]
}
```

> O que o modelo ensina fica neste arquivo, não dentro dele. Por isso o
> trabalho roda em qualquer computador: o conhecimento viaja junto.

**O ponto que mais rende** — a seção `ambiguas`:

> "Jogo de chaves de fenda" é ferramenta e "jogo de facas" é cozinha. O sistema
> percebe sozinho que a palavra "jogo" serve às duas e para de usá-la para
> generalizar. Um jogo de tabuleiro novo não recebe categoria nenhuma, porque
> chutar seria pior.

**Se sobrar tempo, conte o que não deu certo:**

> Tentei deixar o modelo gerar as tags livremente. Ele dizia "calcado" para um
> produto e "calcados" para outro. Para a tabela hash são duas chaves
> diferentes, e metade dos calçados sumia da busca: seis de seis viravam quatro
> de seis. Resolvi restringindo a resposta a um conjunto fechado de categorias.

---

## 6. Fechamento (1 min)

> São 123 testes automatizados, e a maior parte deles nasceu de defeito real,
> não de caso imaginado. Uma chuteira que saía sem cor, uma palavra de ligação
> virando tag, um violão classificado só pelo material das cordas. Cada um
> desses é hoje um teste que impede o problema de voltar.

E feche com a ideia central:

> A conclusão que eu levo é que medir mudou decisões. Duas afirmações que eu
> tinha escrito como verdade estavam erradas, e só apareceram porque implementei
> a alternativa e comparei.

---

## Perguntas prováveis

**"Por que não usou o dicionário do Python, se o enunciado permite?"**
O dicionário já é uma tabela hash, só que escondida. Usá-lo entregaria o uso da
estrutura, não a estrutura — função de dispersão, colisão e redimensionamento
ficariam invisíveis. Fiz o caminho mais difícil de propósito.

**"Por que a tag é 'calcado' e não 'calçado'?"**
Porque a tag é chave de hash, e hash exige igualdade exata. Se guardasse com
cedilha e o cliente digitasse sem, os dois textos teriam números diferentes e
cairiam em baldes diferentes. Guardo na forma canônica e normalizo a busca —
procurar "CALÇADO", "calçado" ou "calcado" acha o mesmo produto. Posso
demonstrar.

**"Por que a capacidade é um número primo?"**
Porque a posição é hash módulo capacidade. Se a capacidade tiver fatores em
comum com os valores de hash, as chaves se concentram. Medi: com 1024, 31% dos
baldes nunca são usados; com 1031, nenhum fica vazio.

**"Qual a complexidade das operações?"**
Busca e inserção são O(1) no caso médio e O(n) no pior, quando todas as chaves
caem no mesmo balde. A busca por tag é O(1) para achar a lista mais O(k) para
montar o resultado, com k = produtos encontrados. Está tudo em `docs/04`.

**"E se duas chaves colidirem?"**
Elas convivem. Cada balde guarda uma lista encadeada, e a busca percorre a
corrente comparando as chaves. Dá para ver acontecendo: cadastre um produto de
cozinha e um de esporte e abra a opção 7 — as duas tags caem no mesmo balde.

**"Isso roda na minha máquina?"**
Sem `--ia`, roda em qualquer lugar com Python 3, sem instalar nada. O modo com
IA precisa de Mac com Apple Silicon e macOS 26. Mas o que o modelo já aprendeu
está no `dados/aprendido.json`, que vai junto — então a busca por essas
categorias funciona mesmo sem ele.

**"A IA é mesmo necessária? O vocabulário não bastaria?"**
O vocabulário é mais rápido e nunca inventa, mas só conhece o que foi
cadastrado. Um "guarda-chuva" ficaria sem tag nenhuma e invisível na busca. O
modelo resolve isso sem cadastro prévio. Por outro lado, ele inventa atributos
— atribuiu a cor azul a uma camisa de algodão que não menciona cor. Por isso
cada um cuida do que faz bem: o modelo diz a categoria, o vocabulário diz cor e
material.

**"Por que não treinou o modelo (fine-tuning)?"**
Porque o que eu precisava era um mapeamento fixo: "tenis" sempre vira "calcado".
Isso é uma tabela de lookup, que é justamente o `vocabulario.py`. Treinar uma
rede de bilhões de parâmetros para memorizar um mapeamento determinístico é a
ferramenta errada, e ela ainda erraria às vezes. Além disso, o adaptador
precisaria ser retreinado a cada atualização do modelo pela Apple.

**"Quantos produtos você testou?"**
Os testes chegam a 300 produtos, os benchmarks a 50 mil. A tabela redimensiona
sozinha várias vezes nesse caminho, e há um teste só para garantir que nada se
perde no redimensionamento.

---

## O que não fazer

**Não comece pela IA.** A disciplina é Estrutura de Dados. A IA é o acessório;
as tabelas hash são o trabalho.

**Não leia a tela em voz alta.** Mostre o resultado e diga o que ele significa.

**Não esconda as limitações.** Se perguntarem algo que não funciona bem, diga —
o violão virou "audio" porque não existe categoria para instrumento musical, e
isso está documentado. Admitir um limite conhecido passa mais confiança que
improvisar uma justificativa.

**Não prometa o que não mediu.** Todo número que você citar está em algum
benchmark que dá para rodar na hora. Se alguém pedir para provar, rode.
