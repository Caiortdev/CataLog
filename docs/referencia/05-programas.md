# Referência — Programas executáveis

Arquivos cobertos: `main.py`, `ferramentas/benchmark.py`, `ferramentas/benchmark_colisoes.py`,
`ferramentas/povoar_aprendizado.py` e `ferramentas/preparar_gravacao.py`.

São os cinco programas que se executam direto. Nenhum deles contém lógica de
estrutura de dados — tudo isso está no pacote `catalogo/`.

---

## `main.py` — o programa principal

```bash
python3 main.py        # só o vocabulário, funciona em qualquer computador
python3 main.py --ia   # o modelo local analisa todo produto
```

> `--aprender` continua aceito, por ser o nome anterior do modo.

### O menu

| tecla | o que faz |
|---|---|
| `1` | Cadastrar produto |
| `2` | Listar todos |
| `3` | Buscar por tag |
| `4` | Buscar por várias tags (exige todas) |
| `5` | Buscar escrevendo uma frase |
| `A` | Buscar palavra literal (índice de texto) |
| `B` | Inferir regras novas a partir do catálogo |
| `C` | Revisar classificações instáveis do modelo |
| `6` | Ver tags existentes |
| `7` | Ver estado interno das tabelas |
| `8` | Carregar produtos de exemplo |
| `9` | Remover produto |
| `0` | Sair |

### Funções

| função | o que faz |
|---|---|
| `montar_gerador(argumentos)` | decide o modo conforme a linha de comando; devolve `(gerador, professor, descrição)` |
| `mostrar_produtos(produtos)` | imprime uma lista de produtos |
| `mostrar_estatisticas(catalogo, professor=None)` | abre o estado das três tabelas |
| `mostrar_avisos(professor, ja_vistos)` | mostra só os avisos novos; devolve o total visto |
| `mostrar_revisao(professor)` | lista as classificações instáveis |
| `mostrar_inferencias(catalogo)` | roda e exibe as regras sugeridas |
| `cadastrar(catalogo)` | pergunta nome e descrição, cadastra |
| `remover(catalogo)` | pergunta o identificador, remove |
| `carregar_exemplos(catalogo)` | cadastra os 6 produtos da constante `EXEMPLOS` |

**Importante:** o catálogo vive só na memória. Fechar o programa apaga os
produtos — mas não o que a IA aprendeu, que fica em `dados/aprendido.json`.

---

## `ferramentas/benchmark.py` — busca com índice contra varredura

```bash
python3 ferramentas/benchmark.py
```

Compara buscar pelo índice invertido com percorrer o catálogo inteiro, em
catálogos de 1.000, 10.000 e 50.000 produtos.

### Constantes ajustáveis

| nome | padrão | o que é |
|---|---|---|
| `TAMANHOS` | `[1000, 10000, 50000]` | tamanhos de catálogo testados |
| `REPETICOES` | `50` | execuções por medição |
| `TAG_PROCURADA` | `"natacao"` | a tag buscada; aparece em 1% dos produtos |

### Saída típica

```
  produtos |  achados |  indice (ms) |  varredura (ms) | quantas vezes
      1000 |       10 |       0.0068 |          0.1223 |           18x
     10000 |      100 |       0.0517 |          1.3627 |           26x
     50000 |      500 |       0.2718 |         12.1561 |           45x
```

**Como ler:** o número não é o mais importante. O importante é que a coluna da
varredura cresce junto com o catálogo e a do índice não — ela acompanha quantos
produtos foram *encontrados*.

---

## `ferramentas/benchmark_colisoes.py` — as duas estratégias de colisão

```bash
python3 ferramentas/benchmark_colisoes.py
```

Põe à prova as afirmações do [documento 1](../01-tabela-hash.md). São cinco
experimentos:

| # | o que testa | resultado |
|---|---|---|
| 1 | capacidade prima contra potência de dois | com 1024, **316 baldes nunca são usados** |
| 2 | o limite de 0,75 se justifica | 0,5 e 0,75 dão resultado **idêntico** |
| 3 | endereçamento aberto degrada com remoções | **não degrada** — a afirmação estava errada |
| 4 | quanto cada estratégia gasta de memória | encadeamento gasta 8% a mais |
| 5 | por que o endereçamento aberto perde | agrupamento: 1,28 contra 61,68 comparações |

Dois desses experimentos corrigiram afirmações que estavam escritas na
documentação como verdade.

---

## `ferramentas/povoar_aprendizado.py` — construir a base de conhecimento

```bash
python3 ferramentas/povoar_aprendizado.py
```

Preenche `dados/aprendido.json` consultando o modelo sobre uma lista de produtos
de categorias variadas. Leva cerca de 30 segundos.

### Constantes

| nome | o que é |
|---|---|
| `PRODUTOS` | a lista de produtos a classificar, agrupada por categoria |
| `CORRECOES` | correções humanas às respostas do modelo, cada uma com o motivo |

`CORRECOES` é a parte mais importante do arquivo. Rodando a lista, o modelo
errou sete vezes — classificou uma trena a laser como esporte, um colchão como
acessório, e colocou cafeteira e chaleira em "eletronico" enquanto o
micro-ondas foi para "cozinha".

**Essa possibilidade de revisar é o argumento prático contra treinar o modelo.**
O que ele ensinou são trinta linhas de JSON que uma pessoa lê em um minuto.
Dentro dos pesos de um modelo ajustado não haveria o que revisar.

### Duas particularidades

**Produtos que o vocabulário já reconhece são pulados** — perguntar sobre eles
encheria o arquivo de entradas que nunca serão lidas.

**A generalização por palavra é desligada durante a construção.** No uso normal
o atalho é desejável; aqui ele atrapalha, porque responderia antes de o modelo
ser consultado e esconderia os conflitos.

---

## `ferramentas/preparar_gravacao.py` — limpar antes de gravar

```bash
python3 ferramentas/preparar_gravacao.py
```

Apaga do aprendizado apenas as três frases usadas na demonstração, para elas
voltarem a ser novidade. O resto continua.

**Por que existe:** quando um produto é cadastrado, o sistema aprende e não
pergunta mais ao modelo. Ensaiando com as frases da demonstração, na hora de
gravar a IA não seria acionada e a parte mais interessante não aconteceria.

### Constante

| nome | o que é |
|---|---|
| `FRASES_DA_DEMONSTRACAO` | as três frases do roteiro, exatamente como serão digitadas |

Para mudar as frases da demonstração, edite esta lista.
