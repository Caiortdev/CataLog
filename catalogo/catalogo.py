"""
O catálogo: onde as duas tabelas hash se encontram.

Esta é a parte do projeto que responde "por que hash table?" de verdade, e ela
merece ser lida com calma.

A PRIMEIRA TABELA é a óbvia: identificador -> Produto. Serve para "me mostre o
produto P007". Custo O(1).

A SEGUNDA TABELA é a que o enunciado está pedindo sem dizer o nome. O item 4
manda buscar produtos PELAS TAGS. Se tivéssemos só a primeira tabela, a busca
por "corrida" teria que abrir cada produto e olhar a lista de tags dele: O(n),
exatamente o custo que a tabela hash existe para evitar. A estrutura certa
estaria respondendo à pergunta errada.

Então criamos uma segunda tabela, invertida:

    tabela de produtos          tabela de tags (índice invertido)
    P001 -> Tênis azul          calcado -> [P001]
    P002 -> Camisa azul         azul    -> [P001, P002]
                                corrida -> [P001]

A chave deixou de ser o produto e passou a ser a tag. Agora buscar "azul" é
uma consulta O(1) que já devolve a resposta pronta. Essa inversão é a mesma
ideia que o índice remissivo de um livro usa: em vez de ler o livro inteiro
procurando a palavra, você olha a palavra no final e ela te dá as páginas.

O preço disso é duplicação: a mesma informação (produto P001 tem a tag azul)
fica guardada nos dois lugares. Em troca de memória extra, ganhamos velocidade
de busca. É uma das trocas mais comuns em computação, e aqui ela é consciente.
"""

from catalogo.hashtable import TabelaHash
from catalogo.produto import Produto
from catalogo.tagger import GeradorDeTags
from catalogo.texto import normalizar, tokenizar


class Catalogo:

    def __init__(self, gerador_de_tags=None):
        # Tabela 1: acesso direto ao produto pelo identificador.
        self._produtos = TabelaHash()
        # Tabela 2: índice invertido semântico, tag -> identificadores.
        self._indice_tags = TabelaHash()
        # Tabela 3: índice invertido literal, palavra do texto -> identificadores.
        #
        # As duas últimas são índices invertidos, mas respondem a perguntas
        # diferentes, e a diferença justifica terem sido separadas.
        #
        # O índice de tags é SEMÂNTICO: "tenis" vira "calcado" e "esporte",
        # palavras que não estão escritas em lugar nenhum do produto. Ele acha
        # por significado, mas só conhece o que o vocabulário ensinou.
        #
        # O índice de texto é LITERAL: guarda exatamente as palavras digitadas.
        # Ele não entende nada, mas também não depende de vocabulário — e é por
        # isso que existe. Uma "Frigideira antiaderente de cerâmica" aprendida
        # pelo modelo recebe uma única tag, "cozinha", e quem procurasse por
        # "ceramica" não acharia. Com o índice literal, acha.
        self._indice_texto = TabelaHash()
        self._gerador = gerador_de_tags or GeradorDeTags()
        self._proximo_numero = 1

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def cadastrar(self, nome, descricao=""):
        """
        Cadastra um produto e já o deixa pesquisável. Custo O(t), com t = número
        de tags do produto (um punhado), ou seja, praticamente constante.

        A ordem das três etapas importa: as tags precisam existir antes de
        podermos indexá-las.
        """
        if not nome.strip():
            raise ValueError("produto precisa de um nome")

        identificador = self._gerar_identificador()
        tags = self._gerador.gerar(nome, descricao)
        produto = Produto(identificador, nome, descricao, tags)

        self._produtos.inserir(identificador, produto)
        for tag in tags:
            self._indexar(self._indice_tags, tag, identificador)
        for palavra in tokenizar(f"{nome} {descricao}"):
            self._indexar(self._indice_texto, palavra, identificador)

        return produto

    def remover(self, identificador):
        """
        Tira o produto do catálogo e também do índice.

        O detalhe que costuma virar bug: remover só da primeira tabela. O
        produto some da listagem, mas o identificador dele continua pendurado
        nas listas de tags. A busca por "corrida" devolveria um identificador
        que não existe mais, e o programa quebraria ao tentar abrir o produto.
        Por isso a limpeza do índice acontece aqui, junto.
        """
        produto = self._produtos.remover(identificador)

        # Os dois índices precisam ser limpos, não só o de tags. Esquecer o de
        # texto deixaria o mesmo rastro de identificadores apontando para um
        # produto que não existe mais.
        self._desindexar(self._indice_tags, produto.tags, identificador)
        self._desindexar(
            self._indice_texto,
            tokenizar(f"{produto.nome} {produto.descricao}"),
            identificador,
        )

        return produto

    @staticmethod
    def _indexar(indice, chave, identificador):
        identificadores = indice.buscar(chave)
        if identificadores is None:
            indice.inserir(chave, [identificador])
        elif identificador not in identificadores:
            identificadores.append(identificador)

    @staticmethod
    def _desindexar(indice, chaves, identificador):
        for chave in chaves:
            identificadores = indice.buscar(chave)
            if identificadores is None or identificador not in identificadores:
                continue
            identificadores.remove(identificador)
            # Chave que ficou sem nenhum produto sai do índice. Deixá-la ali
            # faria a tabela crescer para sempre e sujaria as listagens.
            if not identificadores:
                indice.remover(chave)

    def _gerar_identificador(self):
        identificador = f"P{self._proximo_numero:03d}"
        self._proximo_numero += 1
        return identificador

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def obter(self, identificador):
        """Busca pelo identificador. O(1)."""
        return self._produtos.buscar(identificador)

    def buscar_por_tag(self, tag):
        """
        Todos os produtos que têm a tag. O(1) para achar a lista, mais O(k)
        para montar o resultado, com k = quantidade de produtos com a tag.

        Note que não existe nenhum laço sobre o catálogo aqui. O tamanho do
        catálogo não aparece na conta: ter 10 ou 10 milhões de produtos não
        muda o tempo de localizar a lista.
        """
        termo = self._normalizar_termo(tag)
        identificadores = self._indice_tags.buscar(termo)
        if identificadores is None:
            return []
        return [self._produtos.buscar(i) for i in identificadores]

    def buscar_por_tags(self, tags):
        """
        Produtos que têm TODAS as tags informadas (filtro, não soma).

        Duas decisões de desempenho aqui, as duas emprestadas de motores de
        busca de verdade:

        1. Se qualquer uma das tags não existe no índice, o resultado é vazio
           e a gente devolve na hora, sem fazer trabalho nenhum.

        2. Começamos pela tag mais rara (a lista mais curta). Procurar "azul"
           dentro dos resultados de "natacao" é muito mais barato que o
           contrário, porque o candidato inicial já é pequeno.

        A verificação de pertinência usa uma TabelaHash montada na hora. Com
        listas pequenas isso é indiferente, mas escrever com `in lista` seria
        busca linear dentro de um laço, ou seja, custo quadrático — justamente
        o padrão que o resto do projeto evita.
        """
        termos = [self._normalizar_termo(t) for t in tags if t.strip()]
        if not termos:
            return []

        listas = []
        for termo in termos:
            identificadores = self._indice_tags.buscar(termo)
            if identificadores is None:
                return []
            listas.append(identificadores)

        listas.sort(key=len)
        candidatos, demais = listas[0], listas[1:]

        conjuntos = []
        for lista in demais:
            tabela = TabelaHash(capacidade_inicial=len(lista) * 2 + 1)
            for identificador in lista:
                tabela.inserir(identificador, True)
            conjuntos.append(tabela)

        resultado = []
        for identificador in candidatos:
            if all(identificador in tabela for tabela in conjuntos):
                resultado.append(self._produtos.buscar(identificador))
        return resultado

    def buscar_por_palavra(self, palavra):
        """
        Produtos cujo texto contém literalmente esta palavra. O(k).

        Complementa `buscar_por_tag`, que busca por significado. A diferença
        aparece bem em dois exemplos do catálogo:

        Procurar "calcado" acha o tênis, mesmo a palavra não estando escrita
        nele — isso só o índice de tags faz, porque envolve saber que tênis é
        um calçado.

        Procurar "ceramica" acha a frigideira, mesmo "ceramica" não sendo tag
        de nada — isso só o índice de texto faz, porque a palavra está escrita
        lá e nenhum vocabulário precisou conhecê-la.

        Nenhum dos dois substitui o outro.
        """
        termo = self._normalizar_termo(palavra)
        identificadores = self._indice_texto.buscar(termo)
        if identificadores is None:
            return []
        return [self._produtos.buscar(i) for i in identificadores]

    def buscar_por_texto(self, texto):
        """
        Busca escrevendo uma frase em vez de tags exatas.

        A frase passa pelo mesmo gerador de tags usado no cadastro. É o truque
        que faz a busca funcionar: se "Tênis azul" virou as tags X, Y e Z na
        hora de cadastrar, a mesma frase digitada na busca vira X, Y e Z de
        novo. Os dois lados falam a mesma língua porque passam pelo mesmo
        tradutor.
        """
        tags = self._gerador.gerar(texto, "")
        if not tags:
            return []
        return self.buscar_por_tags(tags)

    def todos(self):
        """Percorre o catálogo inteiro. O(n) — e aqui é inevitável mesmo."""
        return [produto for _, produto in self._produtos.itens()]

    def tags_conhecidas(self):
        return sorted(self._indice_tags.chaves())

    def palavras_indexadas(self):
        """
        Todas as palavras que aparecem no texto de algum produto.

        Existe para o módulo de inferência poder percorrer o índice literal
        sem mexer nas tabelas por dentro.
        """
        return sorted(self._indice_texto.chaves())

    @staticmethod
    def _normalizar_termo(tag):
        """
        Põe o termo buscado na mesma forma usada no cadastro.

        Sem isto, buscar "Calçado" não acharia nada: a tag foi guardada como
        "calcado" e hash não perdoa diferença de um caractere.
        """
        return normalizar(tag).strip()

    # ------------------------------------------------------------------
    # Diagnóstico
    # ------------------------------------------------------------------

    def estatisticas(self):
        return {
            "produtos": self._produtos.estatisticas(),
            "indice_de_tags": self._indice_tags.estatisticas(),
            "indice_de_texto": self._indice_texto.estatisticas(),
            "termos_no_vocabulario": self._gerador.termos_conhecidos(),
        }

    def __len__(self):
        return len(self._produtos)
