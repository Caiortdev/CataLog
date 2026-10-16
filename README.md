# Catálogo de Produtos com Tags Automáticas

Projeto 4 da disciplina de Estrutura de Dados 1.

Um catálogo de e-commerce que recebe o nome e a descrição de um produto, analisa
esse texto para gerar tags sozinho, guarda tudo em tabelas de dispersão
construídas do zero e permite buscar produtos por essas tags.

## Como rodar

Precisa só do Python 3. Nenhuma biblioteca externa, nenhuma instalação, nenhuma
chave de API, nenhuma conexão com a internet.

```bash
python3 main.py
```

### Os dois modos

```bash
python3 main.py        # só o vocabulário
python3 main.py --ia   # o modelo local analisa todo produto
```

Com `--ia`, o item 2 do enunciado é cumprido ao pé da letra: um modelo de
linguagem analisa a descrição de **cada** produto cadastrado. Ele roda dentro da
própria máquina, pelo Apple Intelligence — sem internet, sem chave de API, sem
custo por chamada e sem mandar dado nenhum para fora.

O trabalho é dividido segundo o que cada lado faz melhor, e essa divisão foi
medida, não suposta:

| | vem de | porque |
|---|---|---|
| categoria (`calcado`, `cozinha`) | modelo | acerta mesmo em palavras que ninguém cadastrou |
| cor, material, uso | vocabulário | o modelo inventa atributos — atribuiu a cor azul a uma "Camisa de algodão" que não menciona cor |

O custo é pago uma vez por produto:

```
só vocabulário.........:   0,0115 ms
--ia, primeira vez.....: 178,9    ms
--ia, com cache........:   0,0185 ms
```

A resposta do modelo vai para `dados/aprendido.json`, versionado junto com o
projeto, e o que ele aprende não é um produto e sim uma **palavra**: ao
classificar uma "Frigideira antiaderente", o sistema guarda que `frigideira` é
`cozinha`, e qualquer outra frigideira já sai classificada sem consultar nada.

O modo sem `--ia` existe por portabilidade: o trabalho precisa rodar em qualquer
computador, e o Apple Intelligence exige Mac com Apple Silicon e macOS 26. Nesse
modo o conhecimento já aprendido continua valendo — ele está no arquivo, não no
modelo. Se o modelo for pedido e não estiver disponível, o programa explica o
motivo e segue com o vocabulário em vez de quebrar.

Chegar a esse desenho levou três tentativas, e as duas que falharam ensinaram
mais que a que deu certo — inclusive por que fine-tuning não resolveria o
problema. A história completa, com as medições, está em
[docs/06](docs/06-vocabulario-que-aprende.md).

## O caminho que um produto percorre

Cadastrar "Tênis azul / para corrida em asfalto" dispara esta sequência:

```
texto digitado
     |  normalizar: minúsculas, sem acento, sem pontuação
"tenis azul para corrida em asfalto"
     |  tokenizar: separa e joga fora palavras de ligação
["tenis", "azul", "corrida", "asfalto"]
     |  consultar o vocabulário (que é uma tabela hash)
["calcado", "esporte", "azul", "cor", "corrida", "asfalto", "rua"]
     |  guardar nas duas tabelas
tabela de produtos:  P001 -> o produto inteiro
índice de tags:      calcado -> [P001], azul -> [P001], corrida -> [P001] ...
```

A partir daí, buscar "corrida" é uma única consulta na segunda tabela.

## Estrutura dos arquivos

```
catalogo/
  hashtable.py     a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py  a alternativa (endereçamento aberto), para comparar
  texto.py         normalização e separação em palavras
  vocabulario.py   que palavra dispara que tag
  tagger.py        o gerador de tags
  professor.py     consulta o modelo local sobre produtos desconhecidos
  produto.py       os dados de um produto
  catalogo.py      junta tudo: as três tabelas e as buscas
  inferencia.py    descobre regras novas olhando o próprio catálogo
ia/
  ClassificaProduto.swift   ponte para o modelo do Apple Intelligence
dados/
  aprendido.json   o que o modelo já ensinou (versionado)
testes/            os testes automatizados
docs/              por que cada decisão foi tomada
main.py            menu de terminal
benchmark.py       medição de desempenho da busca
benchmark_colisoes.py   comparação das estratégias de colisão
povoar_aprendizado.py   gera o dados/aprendido.json e registra as correções
```

O `dados/aprendido.json` já vem preenchido com 30 produtos de categorias
variadas, então a busca por `cozinha`, `ferramenta`, `pet` ou `papelaria`
funciona em qualquer máquina, sem Apple Intelligence. O
`povoar_aprendizado.py` mostra de onde vieram essas entradas e permite
reconstruí-las.

Vale abrir esse script: além da lista de produtos, ele guarda as **correções
humanas** às respostas do modelo. O modelo classificou uma trena a laser como
artigo de esporte, um colchão como acessório, e colocou cafeteira e chaleira em
"eletronico" enquanto o micro-ondas foi para "cozinha" — três eletrodomésticos
de cozinha em duas categorias. Cada correção está registrada com o motivo.

Essa possibilidade de revisar é o argumento prático contra treinar o modelo:
aqui o que ele ensinou são trinta linhas de JSON que alguém lê em um minuto e
corrige com um editor de texto. Dentro dos pesos de um modelo ajustado não
haveria nada para revisar, nem como consertar um caso específico.

## Onde está cada conteúdo da disciplina

| Conceito | Arquivo | O que olhar |
|---|---|---|
| Função de dispersão | `catalogo/hashtable.py` | `hash_djb2` |
| Tratamento de colisão | `catalogo/hashtable.py` | classe `_No` e o laço em `inserir` |
| Endereçamento aberto | `catalogo/hashtable_aberta.py` | `_sondar` e o marcador `REMOVIDO` |
| Comparação das estratégias | `benchmark_colisoes.py` | com as duas afirmações corrigidas |
| Fator de carga | `catalogo/hashtable.py` | `fator_carga` e `_redimensionar` |
| Lista encadeada | `catalogo/hashtable.py` | o encadeamento dentro de cada balde |
| Índice invertido | `catalogo/catalogo.py` | `_indice_tags` e `buscar_por_tag` |
| Dois índices, critérios diferentes | `catalogo/catalogo.py` | `_indice_texto` e `buscar_por_palavra` |
| Uso estatístico dos índices | `catalogo/inferencia.py` | `inferir_regras` |
| Análise de complexidade | `docs/04-complexidade.md` | com tempos medidos |

## Documentação

Os arquivos em `docs/` explicam o raciocínio por trás de cada parte, incluindo
as alternativas que foram consideradas e descartadas:

1. [A tabela hash](docs/01-tabela-hash.md) — função de dispersão, colisões,
   fator de carga e redimensionamento
2. [Geração de tags](docs/02-geracao-de-tags.md) — como o texto vira tag sem
   usar inteligência artificial
3. [O índice invertido](docs/03-indice-invertido.md) — por que uma tabela só
   não resolve o problema
4. [Complexidade](docs/04-complexidade.md) — a análise teórica e os tempos
   medidos de verdade
5. [Decisões e alternativas](docs/05-decisoes-e-alternativas.md) — o que foi
   descartado e por quê
6. [O vocabulário que aprende](docs/06-vocabulario-que-aprende.md) — três
   tentativas de usar o modelo de linguagem, duas que falharam, e por que
   fine-tuning não resolveria o problema
7. [Quatro evoluções](docs/07-evolucoes.md) — o terceiro índice, a inferência
   de regras a partir do próprio catálogo, a medida de confiança que se
   revelou fraca, e os dois bugs que só a verificação pegou
8. [Roteiro da apresentação](docs/08-roteiro-da-apresentacao.md) — o que
   mostrar, em que ordem, e as perguntas prováveis com as respostas

## Limitações conhecidas

Listar isto não é modéstia. É o que separa um trabalho que entende o próprio
código de um que só fez funcionar.

**O catálogo só existe na memória.** Fechar o programa apaga tudo. Salvar em
arquivo é assunto de serialização ou banco de dados, e não acrescentaria nada
ao que o enunciado pede sobre estruturas de dados.

**O vocabulário é fixo.** Um produto cujas palavras não estejam em
`vocabulario.py` é cadastrado normalmente, mas fica sem tags e não aparece em
buscas. É o problema que a flag `--aprender` resolve: nesses casos — e só
nesses — o modelo local é consultado e a resposta fica gravada.

**O modelo não sabe dizer "não sei".** Quando perguntado sobre atributos que o
texto não menciona, ele inventa: atribuiu a cor azul a uma "Camisa de algodão",
que não tem cor escrita em lugar nenhum. É por isso que ele é consultado apenas
sobre a categoria do produto, nunca para completar cor, material ou uso — essas
tags só vêm do vocabulário, que não inventa.

**A palavra principal é escolhida por uma regra simples**, que erra em nomes
compostos: "Guarda-chuva" vira `guarda` e "Micro-ondas" vira `micro`. Como chave
de busca isso ainda funciona — qualquer guarda-chuva cai na mesma entrada —, e
quando o truncamento junta coisas diferentes, a detecção de ambiguidade impede
o erro. Mas é uma limitação real, e tratar nomes compostos de verdade exigiria
análise morfológica do português.

**As categorias são uma lista fechada.** Um violão acústico é classificado
como `audio`, porque não existe categoria para instrumento musical. A lista é
fechada de propósito — é o que impede o modelo de inventar variações como
`calcados` — e o preço é que produtos fora dela caem na opção menos ruim.
Acrescentar categorias exige uma linha no Swift e outra em `professor.py`; o
teste `test_categorias_batem_com_o_enum_do_swift` garante que as duas não se
separem.

**O modelo é consultado apenas sobre a categoria.** Chegamos a testar deixá-lo
classificar palavras isoladas, para o vocabulário crescer sozinho. Foi
descartado com dados: ele classificou "dobravel" como calçado, "couro" como
calçado e até "xyzabc" — que não é palavra de idioma nenhum — como calçado. Isso
envenenaria o vocabulário de forma permanente.

**O plural é tratado por uma regra ingênua** que só remove o "s" final.
Funciona para "camisas", não funciona para "papéis". O gênero não é tratado por
regra nenhuma: as poucas cores que mudam no feminino estão listadas uma a uma no
vocabulário. Essa limitação só apareceu rodando o programa — "Chuteira preta"
saía sem tag de cor.

**Palavras-chave não entendem contexto.** "Mochila para notebook" recebe a tag
`informatica`, porque a palavra "notebook" está no texto, mesmo a mochila não
sendo um equipamento de informática. É o comportamento esperado de um sistema
baseado em palavras, e é defensável: quem procura acessório de informática
provavelmente quer ver essa mochila. Mas é importante saber que o sistema não
compreende a frase, só reconhece palavras.

## Roteiro sugerido para a apresentação

O roteiro detalhado, com tempos, comandos e as perguntas prováveis, está em
[docs/08](docs/08-roteiro-da-apresentacao.md). Em resumo:

1. O problema e por que uma lista não serve (1 min).
2. `python3 main.py --ia` — tags geradas sozinhas, busca por característica,
   os dois índices (3 min).
3. `python3 benchmark.py` — por que índice invertido: 45x mais rápido (2 min).
4. `python3 benchmark_colisoes.py` — por que encadeamento, e a afirmação que
   eu tinha escrito errada no documento 1 (3 min).
5. O `dados/aprendido.json` e a detecção de ambiguidade (2 min).
6. Fechamento: 123 testes, a maioria nascida de defeito real (1 min).
