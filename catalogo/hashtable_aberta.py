"""
Tabela de dispersão com endereçamento aberto, para comparação.

Esta classe não é usada pelo catálogo. Ela existe por um motivo específico: o
documento 1 afirma que escolhemos encadeamento separado porque o endereçamento
aberto "degrada o desempenho" quando há muitas remoções, e essa afirmação era
teoria repetida, não coisa medida. Em um projeto que mediu o modelo de
linguagem com cinco amostras, deixar a decisão estrutural mais importante
sustentada por "é o que se diz" ficou incoerente.

Então aqui está a alternativa, implementada de verdade, para o benchmark poder
comparar as duas com números.

A diferença entre as estratégias, em uma frase: no encadeamento, cada balde
guarda uma lista e as chaves que colidem convivem; no endereçamento aberto
existe uma posição por chave, e quem chega e encontra o lugar ocupado vai
procurar outro.
"""

from catalogo.hashtable import _proximo_primo, hash_djb2

# Marcador de posição que já teve algo e foi esvaziada.
#
# Este objeto é a razão de o endereçamento aberto ser mais complicado do que
# parece, e entender o porquê é entender a estratégia inteira.
#
# A busca percorre as posições a partir do índice calculado e para quando
# encontra uma vazia, porque uma posição vazia significa "a chave não está aqui,
# nem adiante". Se a remoção simplesmente esvaziasse a posição, ela criaria uma
# parada no meio do caminho: as chaves que tinham sido empurradas para depois
# dela passariam a ser inalcançáveis, embora continuassem na tabela.
#
# A lápide resolve isso dizendo "aqui teve alguém; continue procurando". O preço
# é que ela ocupa espaço e não some sozinha — o problema que o benchmark mede.
REMOVIDO = object()


class TabelaHashAberta:
    """
    Endereçamento aberto com sondagem linear.

    Sondagem linear quer dizer que, achando a posição ocupada, tentamos a
    seguinte, depois a seguinte, e assim por diante. É a forma mais simples de
    endereçamento aberto e a mais fácil de explicar; existem outras (sondagem
    quadrática, duplo hash) que espalham melhor, ao custo de perder localidade
    de memória.

    A interface é igual à da TabelaHash de propósito. As duas podem ser trocadas
    uma pela outra no benchmark sem mudar mais nada, que é o que torna a
    comparação honesta.
    """

    FATOR_CARGA_MAXIMO = 0.75

    def __init__(self, capacidade_inicial=11):
        self._capacidade = _proximo_primo(capacidade_inicial)
        self._chaves = [None] * self._capacidade
        self._valores = [None] * self._capacidade
        self._tamanho = 0
        # Lápides contam para a ocupação da tabela, mesmo não sendo dados.
        self._lapides = 0
        self.colisoes = 0

    # ------------------------------------------------------------------
    # Sondagem
    # ------------------------------------------------------------------

    def _posicao_inicial(self, chave):
        return hash_djb2(str(chave)) % self._capacidade

    def _sondar(self, chave):
        """
        Procura a chave e devolve (indice, encontrou, sondagens).

        Quando não encontra, o índice devolvido é o primeiro lugar utilizável
        para inserir — que pode ser uma lápide reaproveitada ou uma posição
        nunca usada.

        O laço precisa continuar passando pelas lápides mesmo quando já achou
        uma para reaproveitar, porque a chave procurada pode estar depois dela.
        Parar na primeira lápide inseriria uma cópia duplicada de uma chave que
        já existe mais adiante.
        """
        indice = self._posicao_inicial(chave)
        primeiro_livre = None
        sondagens = 0

        for _ in range(self._capacidade):
            sondagens += 1
            atual = self._chaves[indice]

            if atual is None:
                # Posição nunca usada: a chave não está na tabela.
                return (primeiro_livre if primeiro_livre is not None else indice,
                        False, sondagens)

            if atual is REMOVIDO:
                if primeiro_livre is None:
                    primeiro_livre = indice
            elif atual == chave:
                return indice, True, sondagens

            indice = (indice + 1) % self._capacidade

        # Deu a volta inteira sem achar posição livre. Só acontece se a tabela
        # estiver completamente cheia de dados e lápides, o que o controle de
        # fator de carga deveria impedir.
        return (primeiro_livre if primeiro_livre is not None else indice,
                False, sondagens)

    # ------------------------------------------------------------------
    # Operações
    # ------------------------------------------------------------------

    def inserir(self, chave, valor):
        indice, encontrou, sondagens = self._sondar(chave)

        if encontrou:
            self._valores[indice] = valor
            return

        # Mais de uma sondagem significa que a posição calculada estava ocupada
        # por outra chave — exatamente a definição de colisão.
        if sondagens > 1:
            self.colisoes += 1

        if self._chaves[indice] is REMOVIDO:
            self._lapides -= 1

        self._chaves[indice] = chave
        self._valores[indice] = valor
        self._tamanho += 1

        if self.fator_carga() > self.FATOR_CARGA_MAXIMO:
            self._redimensionar()

    def buscar(self, chave, padrao=None):
        indice, encontrou, _ = self._sondar(chave)
        return self._valores[indice] if encontrou else padrao

    def remover(self, chave):
        """
        Remove a chave, deixando uma lápide no lugar.

        É aqui que a estratégia cobra seu preço. No encadeamento, remover
        religa dois ponteiros e a memória volta a ficar limpa. Aqui, a posição
        não pode ser esvaziada de verdade sem quebrar as buscas que passam por
        ela, então fica um marcador que continua custando uma sondagem a cada
        consulta futura.
        """
        indice, encontrou, _ = self._sondar(chave)
        if not encontrou:
            raise KeyError(chave)

        valor = self._valores[indice]
        self._chaves[indice] = REMOVIDO
        self._valores[indice] = None
        self._tamanho -= 1
        self._lapides += 1
        return valor

    # ------------------------------------------------------------------
    # Carga e redimensionamento
    # ------------------------------------------------------------------

    def fator_carga(self):
        """
        Ocupação da tabela, contando as lápides.

        Esta é a diferença crucial em relação ao encadeamento. Lá, o fator de
        carga é só a razão entre elementos e baldes. Aqui, as lápides ocupam
        posição e atrapalham a sondagem, então precisam entrar na conta — caso
        contrário uma tabela cheia de marcadores de remoção pareceria vazia e
        nunca seria reorganizada.
        """
        return (self._tamanho + self._lapides) / self._capacidade

    def _redimensionar(self):
        """
        Reconstrói a tabela, descartando as lápides.

        A limpeza das lápides é um efeito colateral importante: elas só somem
        aqui. Um uso com muitas remoções e poucas inserções pode ficar bastante
        tempo com a tabela suja, porque nada dispara a reconstrução.
        """
        chaves_antigas = self._chaves
        valores_antigos = self._valores

        # Se quase tudo era lápide, a tabela não precisa crescer — basta
        # limpar. Dobrar o tamanho nesse caso desperdiçaria memória.
        if self._tamanho > self._capacidade * self.FATOR_CARGA_MAXIMO / 2:
            self._capacidade = _proximo_primo(self._capacidade * 2)

        self._chaves = [None] * self._capacidade
        self._valores = [None] * self._capacidade
        self._tamanho = 0
        self._lapides = 0
        self.colisoes = 0

        for chave, valor in zip(chaves_antigas, valores_antigos):
            if chave is not None and chave is not REMOVIDO:
                self.inserir(chave, valor)

    # ------------------------------------------------------------------
    # Leitura e inspeção
    # ------------------------------------------------------------------

    def custo_de_busca(self, chave):
        """
        Quantas posições a busca precisa examinar para responder.

        É a métrica que torna as duas estratégias comparáveis. No encadeamento
        o custo é o número de nós percorridos na corrente; aqui é o número de
        sondagens. Nos dois casos, é quantas comparações a estrutura fez para
        dar a resposta — e é isso que o O(1) promete manter pequeno.
        """
        _, _, sondagens = self._sondar(chave)
        return sondagens

    def chaves(self):
        for chave in self._chaves:
            if chave is not None and chave is not REMOVIDO:
                yield chave

    def itens(self):
        for chave, valor in zip(self._chaves, self._valores):
            if chave is not None and chave is not REMOVIDO:
                yield chave, valor

    def estatisticas(self):
        maior_sondagem = 0
        for chave in self._chaves:
            if chave is not None and chave is not REMOVIDO:
                maior_sondagem = max(maior_sondagem, self.custo_de_busca(chave))

        return {
            "capacidade": self._capacidade,
            "elementos": self._tamanho,
            "fator_carga": round(self.fator_carga(), 3),
            "lapides": self._lapides,
            "maior_sondagem": maior_sondagem,
            "colisoes": self.colisoes,
        }

    def __len__(self):
        return self._tamanho

    def __contains__(self, chave):
        _, encontrou, _ = self._sondar(chave)
        return encontrou

    def __repr__(self):
        return (f"TabelaHashAberta(elementos={self._tamanho}, "
                f"lapides={self._lapides}, capacidade={self._capacidade})")
