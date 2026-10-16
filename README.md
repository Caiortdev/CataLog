# Catálogo de Produtos com Tags Automáticas

Projeto 4 — Estrutura de Dados 1

Um catálogo de e-commerce que lê a descrição de um produto, descobre sozinho em
que categoria ele se encaixa, e o guarda de um jeito que torna a busca
praticamente instantânea — mesmo com dezenas de milhares de produtos.

```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```
Entrada:  "Tênis azul" + "para corrida em asfalto"
Saída:    calcado, esporte, azul, cor, corrida, asfalto, rua
          (nenhuma dessas palavras foi digitada por ninguém)
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

---

## Índice

- [O problema](#o-problema)
- [Como funciona](#como-funciona)
- [Instalação e primeiros passos](#instalação-e-primeiros-passos)
- [Como usar](#como-usar)
- [Estrutura do projeto](#estrutura-do-projeto)
- [As três tabelas hash](#as-três-tabelas-hash)
- [A inteligência artificial](#a-inteligência-artificial)
- [Testes](#testes)
- [Medições de desempenho](#medições-de-desempenho)
- [Documentação completa](#documentação-completa)
- [Onde está cada conteúdo da disciplina](#onde-está-cada-conteúdo-da-disciplina)
- [Limitações conhecidas](#limitações-conhecidas)

---

## O problema

Uma loja online com cem mil produtos. Alguém procura por "tênis azul de
corrida". Como o site encontra isso rápido?

O jeito óbvio seria abrir produto por produto e conferir se bate com o pedido.
Funciona com dez produtos; com cem mil, o cliente desiste antes de a página
carregar. Esse é o custo O(n): o tempo cresce junto com a quantidade de dados.

Este projeto resolve o problema com **tabelas de dispersão construídas do zero**
e um **índice invertido**, de forma que encontrar algo não dependa de quantas
coisas existem guardadas.

---

## Como funciona

```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```
  "Tênis azul" + "para corrida em asfalto"
            |
            v
  1. O texto é limpo      minúsculas, sem acento, sem pontuação,
                          sem palavras de ligação
            |
            v
  2. Viram tags           o vocabulário reconhece cor, material e uso;
                          a IA diz a categoria
            |
            v
  3. É guardado           três tabelas hash: produto por código,
                          tag por significado, palavra por texto literal
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

A partir daí, procurar por qualquer tag leva direto ao produto, sem olhar
nenhum outro.

---

## Instalação e primeiros passos

### Requisitos

| | |
|---|---|
| **Obrigatório** | Python 3.9 ou mais novo |
| **Opcional** | Mac com Apple Silicon, macOS 26+, Apple Intelligence ligado e Xcode — só para o modo com IA |

Não há bibliotecas para instalar. Nenhuma. Só a biblioteca padrão do Python.

### Baixar e rodar

```bash
git clone https://github.com/SEU-USUARIO/CataLog.git
cd CataLog
python3 main.py
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

Pronto. O programa abre.

### Conferir que está tudo certo

```bash
python3 -m unittest discover -s testes -t .
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

Deve aparecer `OK` no final, com 123 testes.

---

## Como usar

### Os dois modos

```bash
python3 main.py        # só o vocabulário — roda em qualquer computador
python3 main.py --ia   # o modelo local analisa todo produto
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

O modo `--ia` cumpre o item 2 do enunciado: um modelo de linguagem analisa a
descrição de **cada** produto. Ele roda dentro da própria máquina, pelo Apple
Intelligence — sem internet, sem chave de API, sem custo e sem mandar dado
nenhum para fora.

Se o modelo não estiver disponível, o programa explica o motivo e segue com o
vocabulário, em vez de quebrar.

### O menu

| tecla | o que faz |
|---|---|
| `1` | Cadastrar produto |
| `2` | Listar todos os produtos |
| `3` | Buscar por tag |
| `4` | Buscar por várias tags (exige todas) |
| `5` | Buscar escrevendo uma frase |
| `A` | Buscar palavra literal, pelo índice de texto |
| `B` | Inferir regras novas a partir do catálogo |
| `C` | Revisar classificações instáveis do modelo |
| `6` | Ver as tags existentes |
| `7` | Ver o estado interno das tabelas hash |
| `8` | Carregar produtos de exemplo |
| `9` | Remover produto |
| `0` | Sair |

### Usando como biblioteca

```python
from catalogo.catalogo import Catalogo

catalogo = Catalogo()
catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
catalogo.cadastrar("Camisa azul", "de algodão")

catalogo.buscar_por_tag("azul")                  # os dois produtos
catalogo.buscar_por_tags(["azul", "calcado"])    # só o tênis
catalogo.buscar_por_palavra("algodao")           # só a camisa
catalogo.buscar_por_texto("tenis para corrida")  # busca por frase
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

Com a IA:

```python
from catalogo.catalogo import Catalogo
from catalogo.tagger import GeradorDeTags
from catalogo.professor import Professor

gerador = GeradorDeTags(professor=Professor(), ia_primeiro=True)
catalogo = Catalogo(gerador_de_tags=gerador)
catalogo.cadastrar("Churrasqueira eletrica", "portatil com tampa de vidro")
# tags: ['cozinha']
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

### Outros comandos

```bash
python3 ferramentas/benchmark.py             # busca com índice contra varredura
python3 ferramentas/benchmark_colisoes.py    # as duas estratégias de colisão comparadas
python3 ferramentas/povoar_aprendizado.py    # reconstruir a base de conhecimento da IA
python3 ferramentas/preparar_gravacao.py     # limpar as frases da demonstração
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

---

## Estrutura do projeto

```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```
catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

testes/                      123 verificações automáticas
docs/                        documentação completa

main.py                      o programa, menu de terminal
benchmark.py                 medição de desempenho da busca
benchmark_colisoes.py        comparação das estratégias de colisão
povoar_aprendizado.py        constrói a base de conhecimento
preparar_gravacao.py         prepara para gravar a demonstração
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

---

## As três tabelas hash

Todas escritas do zero. O Python já traz uma estrutura pronta que faz isso, mas
usá-la esconderia justamente o que a disciplina avalia — função de dispersão,
colisão, fator de carga e redimensionamento.

| tabela | chave | valor | responde a |
|---|---|---|---|
| produtos | identificador | o produto | "me mostre o P007" |
| índice de tags | tag | lista de códigos | "quais produtos são calçados?" |
| índice de texto | palavra | lista de códigos | "quais produtos falam em cerâmica?" |

As duas últimas são **índices invertidos**: a chave deixou de ser o produto e
passou a ser aquilo por que se procura. É a mesma ideia do índice remissivo no
fim de um livro.

A diferença entre elas aparece bem em quatro buscas:

```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```
busca por     índice de tags   índice de texto
cozinha             1                 0        só semântico
ceramica            0                 1        só literal
calcado             1                 0        só semântico
corrida             1                 1        os dois
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

Nenhum dos dois encontra o que o outro encontra.

### Detalhes da implementação

| | |
|---|---|
| Função de dispersão | djb2, determinística |
| Colisão | encadeamento separado, com nós próprios |
| Capacidade | sempre um número primo |
| Fator de carga máximo | 0,75 — passou disso, dobra e redistribui |

---

## A inteligência artificial

O modelo roda **dentro do computador**, pelo Apple Intelligence. O trabalho é
dividido segundo o que cada lado faz melhor, e essa divisão foi medida:

| | vem de | porque |
|---|---|---|
| categoria (`calcado`, `cozinha`) | modelo | acerta mesmo em palavras que ninguém cadastrou |
| cor, material, uso | vocabulário | o modelo inventa atributos — atribuiu a cor azul a uma "Camisa de algodão" que não menciona cor |

### O que ele aprende fica em arquivo

```json
{
  "palavras": { "frigideira": "cozinha", "trena": "ferramenta" },
  "frases":   { "jogo de chaves de fenda": "ferramenta" },
  "ambiguas": ["jogo"],
  "revisar":  ["tapete de sala antiderrapante"]
}
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

E o que se aprende não é um produto, é uma **palavra**: ao classificar uma
"Frigideira antiaderente", o sistema guarda que `frigideira` é `cozinha`, e
qualquer outra frigideira já sai classificada sem consultar nada.

Medindo com quinze produtos novos que usavam palavras conhecidas: **quinze
resolvidos sem o modelo**, em 0,175 ms, contra os cerca de nove segundos que
custariam em consultas.

**Como o arquivo é versionado junto com o projeto**, uma máquina sem Apple
Intelligence não aprende nada novo, mas aproveita tudo que já foi aprendido em
outra. O conhecimento mora no arquivo, não no modelo.

### Quando ele percebe que não pode generalizar

"Jogo de chaves de fenda" é ferramenta e "jogo de facas" é cozinha. Quando a
mesma palavra aparece com duas categorias, o sistema a marca como ambígua e para
de usá-la como atalho. Um jogo de tabuleiro novo não recebe categoria nenhuma —
chutar seria pior.

---

## Testes

```bash
python3 -m unittest discover -s testes -t .
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

**123 verificações**, distribuídas assim:

| arquivo | testes | cobre |
|---|---|---|
| `test_catalogo.py` | 26 | cadastro, buscas, remoção, os dois índices |
| `test_hashtable.py` | 16 | a tabela de encadeamento |
| `test_hashtable_aberta.py` | 14 | a tabela de endereçamento aberto |
| `test_inferencia.py` | 9 | as regras inferidas do catálogo |
| `test_professor.py` | 32 | cache, generalização, ambiguidade, revisão |
| `test_tagger.py` | 26 | normalização e geração de tags |

A maior parte deles **nasceu de um defeito real** encontrado usando o programa,
não de casos imaginados: uma chuteira que saía sem cor, uma palavra de ligação
virando tag, um violão classificado só pelo material das cordas.

---

## Medições de desempenho

### Busca com índice contra percorrer tudo

```bash
python3 ferramentas/benchmark.py
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

| produtos | achados | com índice | varrendo tudo | diferença |
|---|---|---|---|---|
| 1.000 | 10 | 0,0068 ms | 0,1223 ms | 18x |
| 10.000 | 100 | 0,0517 ms | 1,3627 ms | 26x |
| 50.000 | 500 | 0,2718 ms | 12,1561 ms | **45x** |

O importante não é o número: é que a coluna da varredura cresce com o catálogo e
a do índice não — ela acompanha quantos produtos foram *encontrados*.

### As duas estratégias de colisão

```bash
python3 ferramentas/benchmark_colisoes.py
```
README.md                    você está aqui
main.py                      o programa, menu de terminal

catalogo/                    o núcleo — nada aqui depende de terminal
  hashtable.py               a tabela de dispersão (encadeamento separado)
  hashtable_aberta.py        a alternativa (endereçamento aberto), para comparar
  texto.py                   normalização e separação em palavras
  vocabulario.py             que palavra dispara que tag
  tagger.py                  o gerador de tags
  professor.py               consulta o modelo e guarda o que ele ensina
  produto.py                 os dados de um produto
  catalogo.py                junta tudo: as três tabelas e as buscas
  inferencia.py              descobre regras novas olhando o próprio catálogo

ia/
  ClassificaProduto.swift    ponte para o modelo do Apple Intelligence

dados/
  aprendido.json             o que a IA já ensinou (versionado junto)

ferramentas/                 scripts auxiliares, nenhum necessário para usar
  benchmark.py               mede busca com índice contra varredura
  benchmark_colisoes.py      compara as duas estratégias de colisão
  povoar_aprendizado.py      constrói a base de conhecimento da IA
  preparar_gravacao.py       limpa as frases da demonstração

testes/                      123 verificações automáticas

docs/                        documentação
  01-08...                   por que cada decisão foi tomada
  referencia/                como cada arquivo funciona
  apresentacao/              roteiro, tutorial de gravação e o PDF
```

Comparações por busca, conforme a tabela enche:

| ocupação | encadeamento | endereçamento aberto |
|---|---|---|
| 0,1 | 1,00 | 1,01 |
| 0,5 | 1,17 | 4,60 |
| 0,95 | **1,28** | **61,68** |

Com a tabela quase cheia, o endereçamento aberto custa 48 vezes mais. O motivo é
o agrupamento primário: uma chave desviada ocupa a posição vizinha, que desvia a
próxima, e o bloco cresce sozinho.

**Dois experimentos corrigiram afirmações** que estavam escritas na documentação
como verdade. Está contado no [documento 1](docs/01-tabela-hash.md).

---

## Documentação completa

### Por que as coisas são assim

| # | documento |
|---|---|
| 01 | [A tabela hash](docs/01-tabela-hash.md) — dispersão, colisões, fator de carga |
| 02 | [Geração de tags](docs/02-geracao-de-tags.md) — como o texto vira tag |
| 03 | [O índice invertido](docs/03-indice-invertido.md) — por que uma tabela não basta |
| 04 | [Complexidade](docs/04-complexidade.md) — a análise e os tempos medidos |
| 05 | [Decisões e alternativas](docs/05-decisoes-e-alternativas.md) — o que foi descartado |
| 06 | [O vocabulário que aprende](docs/06-vocabulario-que-aprende.md) — três tentativas com o modelo |
| 07 | [Quatro evoluções](docs/07-evolucoes.md) — e os bugs que a verificação pegou |
| 08 | [Roteiro da apresentação](docs/08-roteiro-da-apresentacao.md) |

### Como cada arquivo funciona

| # | referência |
|---|---|
| — | [Índice da referência](docs/referencia/00-indice.md) |
| 01 | [Estruturas de dados](docs/referencia/01-estruturas-de-dados.md) |
| 02 | [Texto e vocabulário](docs/referencia/02-texto-e-vocabulario.md) |
| 03 | [Geração de tags](docs/referencia/03-geracao-de-tags.md) |
| 04 | [Catálogo](docs/referencia/04-catalogo.md) |
| 05 | [Programas](docs/referencia/05-programas.md) |
| 06 | [Testes](docs/referencia/06-testes.md) |

### Material de apresentação

| arquivo | para quê |
|---|---|
| [documentacao.pdf](docs/apresentacao/documentacao.pdf) | a documentação diagramada, 14 páginas |
| [ROTEIRO.md](docs/apresentacao/ROTEIRO.md) | roteiro de apresentação, comando por comando |
| [TUTORIAL-GRAVACAO.md](docs/apresentacao/TUTORIAL-GRAVACAO.md) | tutorial para gravar um vídeo |

---

## Onde está cada conteúdo da disciplina

| conceito | arquivo | o que olhar |
|---|---|---|
| Função de dispersão | `catalogo/hashtable.py` | `hash_djb2` |
| Tratamento de colisão | `catalogo/hashtable.py` | classe `_No` e o laço em `inserir` |
| Endereçamento aberto | `catalogo/hashtable_aberta.py` | `_sondar` e o marcador `REMOVIDO` |
| Fator de carga | `catalogo/hashtable.py` | `fator_carga` e `_redimensionar` |
| Lista encadeada | `catalogo/hashtable.py` | o encadeamento dentro de cada balde |
| Índice invertido | `catalogo/catalogo.py` | `_indice_tags` e `buscar_por_tag` |
| Dois critérios de índice | `catalogo/catalogo.py` | `_indice_texto` e `buscar_por_palavra` |
| Uso estatístico dos índices | `catalogo/inferencia.py` | `inferir_regras` |
| Análise de complexidade | `docs/04-complexidade.md` | com tempos medidos |
| Comparação de estratégias | `ferramentas/benchmark_colisoes.py` | com duas afirmações corrigidas |

---

## Limitações conhecidas

Listar isto não é modéstia — é saber onde o sistema termina.

**Os dados somem ao fechar.** O catálogo vive na memória. Salvar em arquivo é
assunto de serialização ou banco de dados, e não acrescentaria nada ao que o
enunciado pede. O que a IA aprendeu, esse sim, fica gravado.

**O vocabulário é fixo.** Palavras que não estão nele não geram tags de cor ou
material. A IA cobre a categoria, mas não os atributos.

**As categorias são uma lista fechada.** Um violão é classificado como `audio`,
porque não existe categoria para instrumento musical. A lista é fechada de
propósito — é o que impede o modelo de inventar variações como `calcados` — e o
preço é que produtos fora dela caem na opção menos ruim.

**A IA precisa de um Mac recente.** Sem ela, o sistema funciona com o vocabulário
e com tudo que já foi aprendido antes.

**O plural é tratado por uma regra ingênua** que só remove o "s" final. Funciona
para "camisas", não para "papéis". O gênero não é tratado por regra: as poucas
cores que mudam no feminino estão listadas uma a uma.

**O sistema não entende frases.** Reconhece palavras. "Mochila para notebook"
recebe a marcação de informática porque a palavra "notebook" está lá, mesmo a
mochila não sendo um equipamento.

---

## Convenções do código

**Nomes em português**, porque o projeto é acadêmico e em português.

**Underscore inicial significa interno** — `_redimensionar`, `_sondar`.

**Comentários explicam o porquê**, não o quê. O código já diz o que faz; os
comentários registram a decisão, a alternativa descartada ou o defeito que
motivou aquela linha.

**Nenhuma dependência externa.** Só a biblioteca padrão do Python.
