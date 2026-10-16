"""
Tabela de dispersão (hash table) implementada do zero.

Duas decisões que valem explicação, porque são as primeiras perguntas que
aparecem ao ler este arquivo:

1) Por que não usar o dict do Python?
   Porque o dict JÁ É uma tabela hash, só que escondida. Usá-lo aqui seria
   entregar o uso da estrutura, não a estrutura. Todo o conteúdo da disciplina
   (função de dispersão, colisão, fator de carga, redimensionamento) ficaria
   invisível.

2) Por que não usar a função hash() nativa?
   Além do motivo acima, existe um detalhe prático: desde o Python 3.3 o hash
   de strings é aleatorizado a cada execução do interpretador (proteção contra
   ataques de colisão). Na prática isso significa que hash("tenis") devolve um
   número diferente cada vez que você roda o programa, e o produto cairia em
   um balde diferente a cada execução. Impossível testar, impossível demonstrar
   em sala. A nossa função é determinística.
"""


def _e_primo(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def _proximo_primo(n):
    """Menor primo maior ou igual a n."""
    if n <= 2:
        return 2
    candidato = n if n % 2 != 0 else n + 1
    while not _e_primo(candidato):
        candidato += 2
    return candidato


def hash_djb2(texto):
    """
    Função de dispersão djb2, de Daniel J. Bernstein.

    A ideia é simples: percorre a string acumulando um número, e a cada
    caractere embaralha o acumulado antes de somar o próximo. O 33 e o 5381
    não têm prova matemática elegante por trás — foram escolhidos
    empiricamente por espalharem bem strings reais. É uma das funções mais
    usadas justamente por ser curta e ter bom comportamento na prática.

    O `& 0xFFFFFFFF` limita o resultado a 32 bits. Em C isso aconteceria
    sozinho, por estouro do inteiro; em Python os inteiros crescem sem limite,
    então o número ficaria gigante e as multiplicações iriam ficando lentas.
    """
    h = 5381
    for caractere in texto:
        h = (h * 33 + ord(caractere)) & 0xFFFFFFFF
    return h


class _No:
    """
    Um elo da corrente de um balde.

    Poderíamos guardar uma lista do Python dentro de cada balde e seria menos
    código. Mas lista do Python é um vetor dinâmico, não uma lista encadeada —
    o comportamento de memória é outro. Como a disciplina é Estrutura de Dados,
    o encadeamento está escrito na mão mesmo.
    """

    def __init__(self, chave, valor, proximo=None):
        self.chave = chave
        self.valor = valor
        self.proximo = proximo


class TabelaHash:
    """
    Tabela de dispersão com tratamento de colisão por encadeamento separado.

    "Encadeamento separado" quer dizer: cada posição do vetor (cada balde)
    guarda o início de uma lista encadeada. Quando duas chaves diferentes caem
    no mesmo balde, a segunda é pendurada na corrente da primeira, em vez de
    procurar outra posição livre no vetor (que seria a estratégia de
    endereçamento aberto).

    Escolhemos encadeamento porque remover é simples (basta religar os
    ponteiros) e porque a tabela nunca "enche" de verdade. Em endereçamento
    aberto a remoção exige marcadores de célula apagada, e o desempenho
    despenca quando o fator de carga passa de ~0.7.
    """

    FATOR_CARGA_MAXIMO = 0.75

    def __init__(self, capacidade_inicial=11):
        # A capacidade é sempre um primo. Motivo em docs/03-colisoes.md:
        # resumidamente, se a capacidade tiver fatores em comum com os valores
        # de hash, as chaves se concentram em poucos baldes.
        self._capacidade = _proximo_primo(capacidade_inicial)
        self._baldes = [None] * self._capacidade
        self._tamanho = 0
        # Contador puramente didático: serve para mostrar na apresentação
        # quantas vezes duas chaves disputaram o mesmo balde.
        self.colisoes = 0

    # ------------------------------------------------------------------
    # Operações básicas
    # ------------------------------------------------------------------

    def _indice(self, chave):
        """Converte a chave em uma posição válida do vetor."""
        return hash_djb2(str(chave)) % self._capacidade

    def inserir(self, chave, valor):
        """
        Insere ou atualiza. Custo médio O(1).

        O caminho é sempre o mesmo: calcula o balde, percorre a corrente
        daquele balde procurando a chave. Se achar, atualiza. Se não achar,
        insere no início da corrente — inserir no início é O(1), inserir no
        fim exigiria percorrer tudo de novo.
        """
        indice = self._indice(chave)
        no = self._baldes[indice]

        while no is not None:
            if no.chave == chave:
                no.valor = valor
                return
            no = no.proximo

        # Chegou aqui: a chave é nova. Se o balde já tinha alguém, houve
        # colisão — duas chaves distintas disputando a mesma posição.
        if self._baldes[indice] is not None:
            self.colisoes += 1

        self._baldes[indice] = _No(chave, valor, self._baldes[indice])
        self._tamanho += 1

        if self.fator_carga() > self.FATOR_CARGA_MAXIMO:
            self._redimensionar()

    def buscar(self, chave, padrao=None):
        """Devolve o valor da chave, ou `padrao` se ela não existir."""
        no = self._baldes[self._indice(chave)]
        while no is not None:
            if no.chave == chave:
                return no.valor
            no = no.proximo
        return padrao

    def remover(self, chave):
        """
        Remove a chave e devolve o valor. Levanta KeyError se não existir.

        Aqui aparece a vantagem do encadeamento: para tirar um nó do meio da
        corrente basta fazer o anterior apontar para o seguinte.
        """
        indice = self._indice(chave)
        anterior = None
        no = self._baldes[indice]

        while no is not None:
            if no.chave == chave:
                if anterior is None:
                    self._baldes[indice] = no.proximo
                else:
                    anterior.proximo = no.proximo
                self._tamanho -= 1
                return no.valor
            anterior = no
            no = no.proximo

        raise KeyError(chave)

    # ------------------------------------------------------------------
    # Redimensionamento
    # ------------------------------------------------------------------

    def fator_carga(self):
        """Quantos elementos existem por balde, em média."""
        return self._tamanho / self._capacidade

    def _redimensionar(self):
        """
        Dobra a capacidade (arredondando para o próximo primo) e reinsere tudo.

        Por que reinserir em vez de só copiar o vetor para um maior?
        Porque a posição de cada chave é `hash % capacidade`. Mudou a
        capacidade, mudou o resto da divisão, mudou o balde. Copiar as
        correntes de lugar deixaria as chaves em posições onde a busca nunca
        iria procurá-las.

        Esta operação é O(n) — cara. Mas acontece raramente (só quando a
        tabela passa de 75% de ocupação) e, diluída entre todas as inserções,
        o custo médio por inserção continua O(1). Esse raciocínio tem nome:
        análise amortizada.
        """
        baldes_antigos = self._baldes

        self._capacidade = _proximo_primo(self._capacidade * 2)
        self._baldes = [None] * self._capacidade
        self._tamanho = 0
        self.colisoes = 0

        for no in baldes_antigos:
            while no is not None:
                self.inserir(no.chave, no.valor)
                no = no.proximo

    # ------------------------------------------------------------------
    # Leitura e inspeção
    # ------------------------------------------------------------------

    def custo_de_busca(self, chave):
        """
        Quantos nós a busca precisa examinar para responder.

        Existe para comparar esta estratégia com o endereçamento aberto, em
        `hashtable_aberta.py`. As duas percorrem coisas diferentes — aqui uma
        corrente de nós, lá uma sequência de posições do vetor —, mas estão
        fazendo o mesmo trabalho: comparar chaves até decidir. Contar as
        comparações é o que permite colocá-las lado a lado.

        É um método separado, em vez de um contador dentro de `buscar`, para
        não pôr trabalho extra no caminho que o catálogo usa o tempo todo.
        """
        visitados = 0
        no = self._baldes[self._indice(chave)]
        while no is not None:
            visitados += 1
            if no.chave == chave:
                return visitados
            no = no.proximo
        # Corrente percorrida inteira sem achar. O mínimo é 1: mesmo um balde
        # vazio custa olhar o balde.
        return max(visitados, 1)

    def chaves(self):
        for no in self._baldes:
            while no is not None:
                yield no.chave
                no = no.proximo

    def itens(self):
        for no in self._baldes:
            while no is not None:
                yield no.chave, no.valor
                no = no.proximo

    def estatisticas(self):
        """
        Fotografia do estado interno da tabela.

        Existe para a apresentação: permite mostrar que a estrutura está
        distribuindo bem as chaves em vez de acumular tudo em poucos baldes.
        `maior_corrente` é o número mais revelador — se ele cresce junto com a
        quantidade de produtos, a função de dispersão está ruim.
        """
        ocupados = 0
        maior_corrente = 0

        for no in self._baldes:
            if no is not None:
                ocupados += 1
            tamanho_corrente = 0
            while no is not None:
                tamanho_corrente += 1
                no = no.proximo
            maior_corrente = max(maior_corrente, tamanho_corrente)

        return {
            "capacidade": self._capacidade,
            "elementos": self._tamanho,
            "fator_carga": round(self.fator_carga(), 3),
            "baldes_ocupados": ocupados,
            "baldes_vazios": self._capacidade - ocupados,
            "maior_corrente": maior_corrente,
            "colisoes": self.colisoes,
        }

    def __len__(self):
        return self._tamanho

    def __contains__(self, chave):
        marcador = object()
        return self.buscar(chave, marcador) is not marcador

    def __repr__(self):
        return f"TabelaHash(elementos={self._tamanho}, capacidade={self._capacidade})"
