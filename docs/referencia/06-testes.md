# Referência — Testes

Arquivos cobertos: tudo em `testes/`.

São 123 verificações automáticas. A maior parte delas não veio de casos
imaginados: veio de defeitos reais encontrados usando o programa.

---

## Como rodar

```bash
python3 -m unittest discover -s testes -t .
```

Com os nomes de cada teste:

```bash
python3 -m unittest discover -s testes -t . -v
```

Um arquivo só:

```bash
python3 -m unittest testes.test_hashtable -v
```

Uma classe ou um teste específico:

```bash
python3 -m unittest testes.test_hashtable.TestColisoes
python3 -m unittest testes.test_hashtable.TestColisoes.test_chaves_colidindo_convivem_no_mesmo_balde
```

### Sobre os 4 testes que às vezes aparecem como "skipped"

São os que conversam com o Apple Intelligence. Eles se desativam sozinhos
quando o modelo não está disponível, para a suíte passar em qualquer máquina.

```
Ran 123 tests in 0.04s
OK (skipped=4)     <- normal numa máquina sem o modelo
OK                 <- numa máquina com o modelo ligado
```

---

## Os arquivos

| arquivo | testes | o que cobre |
|---|---|---|
| `test_catalogo.py` | 26 | cadastro, buscas, remoção, os dois índices |
| `test_hashtable.py` | 16 | a tabela de encadeamento |
| `test_hashtable_aberta.py` | 14 | a tabela de endereçamento aberto |
| `test_inferencia.py` | 9 | as regras inferidas do catálogo |
| `test_professor.py` | 32 | cache, generalização, ambiguidade, fila de revisão |
| `test_tagger.py` | 26 | normalização de texto e geração de tags |

---

## Os testes que pegam os erros clássicos

Vale conhecer estes, porque cada um existe por um motivo específico.

### `test_nenhum_elemento_se_perde_no_redimensionamento`
*(test_hashtable.py)*

Pega o erro de copiar os baldes para um vetor maior sem recalcular os índices.
Os dados continuam na memória, mas a busca procura no lugar errado. É traiçoeiro
porque a inserção parece ter funcionado — só a busca falha.

### `test_remover_do_meio_da_corrente_nao_quebra_o_resto`
*(test_hashtable.py)*

Verifica o religamento de ponteiros. Se estiver errado, uma chave sobrescreve a
outra — e o bug passa despercebido em testes comuns, porque colisão com poucos
dados é rara.

### `test_remover_do_meio_nao_esconde_o_que_vem_depois`
*(test_hashtable_aberta.py)*

O motivo de a lápide existir. Se a remoção esvaziasse a posição de verdade,
cortaria o caminho de sondagem e as chaves que vieram depois ficariam
inalcançáveis, embora continuassem guardadas. Só aparece com colisão **e**
remoção juntas.

### `test_produto_removido_some_do_indice_de_tags`
*(test_catalogo.py)*

Pega o erro de remover só da tabela de produtos. A listagem fica certa e parece
que funcionou, mas o identificador continua pendurado no índice — e a busca
devolve um produto fantasma.

### `test_categorias_batem_com_o_enum_do_swift`
*(test_professor.py)*

Lê o arquivo Swift, extrai os casos do enum e compara com a constante Python. A
mesma lista existe em dois lugares, em duas linguagens, e a divergência seria
silenciosa.

---

## Os testes que nasceram de defeitos reais

| teste | o defeito que ele impede |
|---|---|
| `test_cor_no_feminino_e_reconhecida` | "Chuteira preta" saía sem nenhuma tag de cor |
| `test_palavra_de_ligacao_dentro_de_tag_composta` | a tag `de` apareceu no catálogo, vinda de "de homem" |
| `test_produto_sem_categoria_consulta_o_professor` | um violão classificado só pelo material das cordas |
| `test_palavra_ambigua_para_de_generalizar` | "jogo" virando cozinha para jogos de tabuleiro |
| `test_hifen_entre_numeros_nao_junta` | "aro 15 - novo" virando "15novo" |

---

## Como os testes evitam depender do ambiente

**Vocabulário controlado.** Vários testes passam uma lista pequena no construtor
em vez de usar o `vocabulario.py` real, para verificar o algoritmo e não o
conteúdo do arquivo.

**Cache temporário.** Os testes do `Professor` usam `tempfile.TemporaryDirectory`
e nunca tocam o `dados/aprendido.json` do projeto.

**Professor falso.** `test_tagger.py` define uma classe que conta quantas vezes
foi consultada, para verificar *quando* o modelo é chamado sem precisar dele.

**Desativação automática.** Os testes de integração verificam a disponibilidade
do modelo antes de rodar e se pulam sozinhos.

---

## Escrevendo um teste novo

Siga o padrão dos existentes: classe por assunto, nome de método descrevendo o
comportamento, e docstring explicando **por que** o teste existe quando o motivo
não for óbvio.

```python
class TestMinhaFuncionalidade(unittest.TestCase):

    def setUp(self):
        self.catalogo = Catalogo()

    def test_descreve_o_comportamento_esperado(self):
        """
        Quando o motivo não for óbvio, explique aqui.
        Os testes deste projeto são lidos como documentação.
        """
        self.assertEqual(resultado, esperado)
```
