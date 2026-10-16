# Referência técnica

Documentação de cada arquivo e cada módulo do projeto: o que faz, como usar,
e o que cada função recebe e devolve.

> Para entender **por que** as coisas foram feitas assim, veja os
> [documentos narrativos](../) numerados de 01 a 08. Esta pasta responde *o quê*
> e *como*; aqueles respondem *por quê*.

---

## Os documentos

| # | documento | arquivos cobertos |
|---|---|---|
| 01 | [Estruturas de dados](01-estruturas-de-dados.md) | `hashtable.py`, `hashtable_aberta.py` |
| 02 | [Texto e vocabulário](02-texto-e-vocabulario.md) | `texto.py`, `vocabulario.py` |
| 03 | [Geração de tags](03-geracao-de-tags.md) | `tagger.py`, `professor.py`, `ClassificaProduto.swift` |
| 04 | [Catálogo](04-catalogo.md) | `produto.py`, `catalogo.py`, `inferencia.py` |
| 05 | [Programas](05-programas.md) | `main.py`, os benchmarks e os scripts |
| 06 | [Testes](06-testes.md) | tudo em `testes/` |

---

## Mapa rápido: onde está cada coisa

| procurando por | vá para |
|---|---|
| a função de hash | [01](01-estruturas-de-dados.md) → `hash_djb2` |
| como funciona a colisão | [01](01-estruturas-de-dados.md) → `TabelaHash` |
| por que a capacidade é prima | [01](01-estruturas-de-dados.md) → redimensionamento |
| como o texto é limpo | [02](02-texto-e-vocabulario.md) → `normalizar` |
| como acrescentar palavras | [02](02-texto-e-vocabulario.md) → `VOCABULARIO` |
| como a IA é consultada | [03](03-geracao-de-tags.md) → `Professor.categoria_de` |
| o formato do arquivo de aprendizado | [03](03-geracao-de-tags.md) → `aprendido.json` |
| como buscar produtos | [04](04-catalogo.md) → os cinco jeitos de buscar |
| o que cada tabela guarda | [04](04-catalogo.md) → as três tabelas |
| as opções do menu | [05](05-programas.md) → `main.py` |
| como rodar os testes | [06](06-testes.md) → como rodar |

---

## Dependências entre os módulos

```
        texto.py          vocabulario.py
           |                    |
           +---------+----------+
                     |
                  tagger.py  <----  professor.py  <---- ClassificaProduto.swift
                     |                    |
                     |              aprendido.json
                     |
   hashtable.py --> catalogo.py <-- produto.py
                     |
                inferencia.py
```

**Lendo de baixo para cima:** `hashtable.py` não depende de nada e é usada por
quase todos. `texto.py` também não depende de nada. `catalogo.py` é o ponto onde
tudo se encontra. `professor.py` é o único que fala com o mundo externo.

**`hashtable_aberta.py` não aparece** porque nada no sistema depende dela — ela
existe só para a comparação do benchmark.

---

## Convenções do código

**Nomes em português.** Classes, métodos e variáveis. O projeto é um trabalho
acadêmico em português, e misturar os dois idiomas atrapalharia a leitura.

**Underscore inicial significa interno.** `_redimensionar`, `_sondar`,
`_indexar` não fazem parte da interface pública e podem mudar.

**Comentários explicam o porquê, não o quê.** O código já diz o que faz; os
comentários registram a decisão, a alternativa descartada ou o defeito que
motivou aquela linha.

**Nenhuma dependência externa.** Só a biblioteca padrão do Python. O modo com
IA usa Swift, que já vem no macOS com o Xcode.
