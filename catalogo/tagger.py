"""
Geração automática de tags a partir do texto do produto.

Este é o módulo que cumpre o item 2 do enunciado: "analisar a descrição e
gerar tags relevantes". Em vez de chamar um serviço externo, a análise é feita
aqui, por regras que a gente escreveu e consegue explicar linha a linha.

O algoritmo é curto de propósito:

    para cada palavra útil do texto:
        existe no vocabulário?        -> pega as tags dela
        não existe? e no singular?    -> tenta de novo
        continua sem achar?           -> ignora a palavra

A parte interessante para a disciplina é ONDE o vocabulário fica guardado:
dentro de uma TabelaHash nossa. O vocabulário tem dezenas de termos e é
consultado uma vez por palavra de cada produto cadastrado. Se fosse uma lista
e a gente percorresse ela inteira a cada palavra, o custo seria O(V) por
palavra, com V = tamanho do vocabulário. Com a tabela hash, é O(1). É a mesma
estrutura do catálogo sendo reaproveitada para um problema diferente, o que
mostra que a escolha não foi só para cumprir enunciado.
"""

from catalogo.hashtable import TabelaHash
from catalogo.professor import CATEGORIAS
from catalogo.texto import singularizar, tokenizar
from catalogo.vocabulario import VOCABULARIO


class GeradorDeTags:
    """
    Converte nome + descrição em uma lista de tags.

    É uma classe, e não uma função solta, por um motivo prático: o vocabulário
    precisa ser carregado na tabela hash uma única vez e reaproveitado em todos
    os produtos. Se fosse função, ou a gente recarregaria o vocabulário a cada
    chamada (desperdício), ou usaria uma variável global (pior de testar).
    Recebendo o vocabulário no construtor, o teste consegue passar um
    vocabulário pequeno e controlado.
    """

    def __init__(self, entradas=VOCABULARIO, professor=None, ia_primeiro=False):
        self._vocabulario = TabelaHash(capacidade_inicial=len(entradas) * 2)
        for termo, tags in entradas:
            self._vocabulario.inserir(termo, tags)
        # O professor é opcional. Sem ele, este gerador funciona só com o
        # vocabulário, sem depender de nada externo.
        self._professor = professor
        # Com ia_primeiro, o modelo é consultado para TODO produto e a
        # categoria dele encabeça as tags. É o modo que segue o enunciado
        # ao pé da letra; o custo está documentado no método gerar().
        self._ia_primeiro = ia_primeiro

    def gerar(self, nome, descricao=""):
        """
        Devolve as tags do produto, sem repetição, na ordem em que foram
        descobertas no texto.

        Sobre a eliminação de duplicatas: usamos uma lista com verificação
        `not in`, que é uma busca linear. Isso parece contradizer todo o
        discurso de O(1) do projeto, mas não contradiz: um produto tem umas
        poucas tags (menos de dez), então a lista percorrida é minúscula e a
        diferença é irrelevante. Montar uma estrutura de hash para dez itens
        custaria mais do que economizaria. Otimizar aqui seria otimizar o lugar
        errado.

        A ordem de descoberta é preservada em vez de alfabética porque ela
        carrega informação: as tags que vêm do nome do produto aparecem antes
        das que vêm da descrição, e o nome costuma ser mais importante.
        """
        texto = f"{nome} {descricao}"
        tags = []

        for palavra in tokenizar(texto):
            encontradas = self._buscar_no_vocabulario(palavra)
            if encontradas is None:
                continue
            for tag in encontradas:
                if tag not in tags:
                    tags.append(tag)

        if self._professor is None:
            return tags

        if self._ia_primeiro:
            return self._com_a_ia_na_frente(texto, tags)

        # Modo complementar: o modelo só entra quando o vocabulário não soube
        # dizer que coisa o produto é.
        if not self._sabe_o_que_e(tags):
            categoria = self._professor.categoria_de(texto)
            if categoria and categoria not in tags:
                tags.append(categoria)

        return tags

    def _com_a_ia_na_frente(self, texto, do_vocabulario):
        """
        O modo em que o modelo analisa todo produto, como o enunciado descreve.

        A categoria vem do modelo e encabeça a lista; o vocabulário entra em
        seguida, com o que ele sabe melhor. A divisão não é arbitrária, é o que
        as medições mostraram sobre cada um:

        O modelo é bom em dizer a que categoria um produto pertence, inclusive
        de palavras que ninguém cadastrou — ele classificou "guarda-chuva" como
        acessório sem nunca ter visto a palavra.

        O modelo é ruim em atributos. Perguntado sobre a cor de uma "Camisa de
        algodão", que não menciona cor nenhuma, ele respondeu "azul". Inventou.
        Por isso cor, material e uso continuam vindo do vocabulário, que só
        reporta o que está escrito.

        Sobre o custo: cada produto novo passa a levar cerca de meio segundo, em
        vez de microssegundos. Isso é pago uma vez por produto — a resposta vai
        para o cache, e produtos parecidos são resolvidos pela generalização de
        palavra sem tocar no modelo. Quando o modelo não está disponível, o
        vocabulário assume sozinho e o programa continua funcionando.
        """
        categoria = self._professor.categoria_de(texto)

        tags = [categoria] if categoria else []
        for tag in do_vocabulario:
            if tag not in tags:
                tags.append(tag)
        return tags

    @staticmethod
    def _sabe_o_que_e(tags):
        """
        Se as tags já dizem QUE COISA o produto é, e não apenas como ele é.

        A distinção veio de um defeito encontrado rodando o programa. Um
        "Violão acústico com cordas de nylon" saía com as tags "nylon" e
        "material", e só. O vocabulário reconhecia "nylon" na descrição, isso
        contava como "já temos tags", e o modelo nunca chegava a ser
        consultado — o produto ficava no catálogo sem nada que dissesse que era
        um instrumento musical.

        O critério antigo era "tem alguma tag". Ele confundia duas coisas
        diferentes: "azul" e "material" descrevem o produto, enquanto "calcado"
        e "cozinha" dizem o que ele é. Uma palavra acessória na descrição
        bloqueava a classificação do produto inteiro.
        """
        return any(tag in CATEGORIAS for tag in tags)

    def _perguntar_ao_professor(self, texto):
        """
        Consulta o modelo sobre a categoria do produto.

        A resposta é acrescentada às tags existentes, nunca as substitui. O
        violão fica com "nylon" e "material", vindos do vocabulário, mais a
        categoria vinda do modelo: as duas fontes somam, cada uma no que sabe.

        O modelo continua restrito à categoria, e não é usado para completar
        cor, material ou uso. O motivo está medido no documento 6: perguntado
        sobre atributos que o texto não menciona, ele inventa — chegou a
        atribuir a cor azul a uma "Camisa de algodão", que não tem cor escrita
        em lugar nenhum. Categoria ele acerta; o resto fica com o vocabulário,
        que não inventa.
        """
        categoria = self._professor.categoria_de(texto)
        return [categoria] if categoria else []

    def _buscar_no_vocabulario(self, palavra):
        """
        Procura a palavra, e só se não achar tenta a forma singular.

        A ordem importa e evita um bug: "tenis" está no vocabulário e é achado
        de primeira, então nunca chega a ser singularizado para "teni". Se a
        gente singularizasse antes de buscar, o produto do enunciado perderia
        as tags principais.
        """
        encontradas = self._vocabulario.buscar(palavra)
        if encontradas is not None:
            return encontradas
        return self._vocabulario.buscar(singularizar(palavra))

    def termos_conhecidos(self):
        """Quantos termos o vocabulário tem. Usado na tela de estatísticas."""
        return len(self._vocabulario)
