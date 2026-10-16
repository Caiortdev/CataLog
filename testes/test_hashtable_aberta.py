"""
Testes da tabela com endereçamento aberto.

A classe existe para comparação, não para uso no catálogo, mas isso não a
dispensa de estar correta: uma comparação feita contra uma implementação com
bug não mede nada. Os testes aqui se concentram no que a estratégia tem de
diferente — a sondagem e as lápides —, já que o resto do comportamento é o
mesmo verificado em `test_hashtable.py`.
"""

import unittest

from catalogo.hashtable import TabelaHash, hash_djb2
from catalogo.hashtable_aberta import REMOVIDO, TabelaHashAberta


def chaves_que_colidem(capacidade, quantidade=2, limite=20000):
    """Chaves diferentes cujo hash cai na mesma posição inicial."""
    grupos = {}
    for i in range(limite):
        chave = f"chave-{i}"
        indice = hash_djb2(chave) % capacidade
        grupos.setdefault(indice, []).append(chave)
        if len(grupos[indice]) == quantidade:
            return grupos[indice]
    raise RuntimeError("não encontrou colisão dentro do limite de busca")


class TestOperacoesBasicas(unittest.TestCase):

    def setUp(self):
        self.tabela = TabelaHashAberta(capacidade_inicial=11)

    def test_inserir_e_buscar(self):
        self.tabela.inserir("tenis", "Tênis de corrida")
        self.assertEqual(self.tabela.buscar("tenis"), "Tênis de corrida")

    def test_chave_inexistente(self):
        self.assertIsNone(self.tabela.buscar("nao-existe"))
        self.assertNotIn("nao-existe", self.tabela)

    def test_atualizar_nao_duplica(self):
        self.tabela.inserir("tenis", "antigo")
        self.tabela.inserir("tenis", "novo")
        self.assertEqual(self.tabela.buscar("tenis"), "novo")
        self.assertEqual(len(self.tabela), 1)

    def test_remover_chave_inexistente(self):
        with self.assertRaises(KeyError):
            self.tabela.remover("nao-existe")


class TestSondagem(unittest.TestCase):
    """
    O comportamento que distingue esta estratégia.

    Quando duas chaves querem a mesma posição, a segunda não fica pendurada na
    primeira: ela vai ocupar outro lugar do vetor. A busca precisa percorrer o
    mesmo caminho para encontrá-la.
    """

    def test_chaves_colidindo_ocupam_posicoes_diferentes(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        primeira, segunda = chaves_que_colidem(11, 2)

        tabela.inserir(primeira, "A")
        tabela.inserir(segunda, "B")

        self.assertEqual(tabela.buscar(primeira), "A")
        self.assertEqual(tabela.buscar(segunda), "B")
        self.assertEqual(len(tabela), 2)
        self.assertEqual(tabela.colisoes, 1)
        # A segunda custou mais de uma sondagem, justamente por ter sido
        # desviada da posição que queria.
        self.assertEqual(tabela.custo_de_busca(primeira), 1)
        self.assertGreater(tabela.custo_de_busca(segunda), 1)


class TestLapides(unittest.TestCase):
    """
    O teste mais importante do arquivo, e a razão de a lápide existir.

    Se a remoção esvaziasse a posição de verdade, ela cortaria o caminho de
    sondagem: as chaves que tinham sido empurradas para depois dela ficariam
    inalcançáveis, embora continuassem guardadas. O bug é traiçoeiro porque só
    aparece quando há colisão E remoção, combinação rara em testes simples.
    """

    def test_remover_do_meio_nao_esconde_o_que_vem_depois(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        a, b, c = chaves_que_colidem(11, 3)

        tabela.inserir(a, 1)
        tabela.inserir(b, 2)
        tabela.inserir(c, 3)

        tabela.remover(b)

        self.assertEqual(tabela.buscar(a), 1)
        self.assertIsNone(tabela.buscar(b))
        # Esta é a asserção que pega o bug: "c" está depois da posição que foi
        # esvaziada, e precisa continuar sendo encontrado.
        self.assertEqual(tabela.buscar(c), 3)

    def test_lapide_e_contabilizada(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        tabela.inserir("a", 1)
        tabela.remover("a")
        self.assertEqual(tabela.estatisticas()["lapides"], 1)
        # A lápide ocupa posição, então a tabela não está realmente vazia do
        # ponto de vista da ocupação.
        self.assertEqual(len(tabela), 0)
        self.assertGreater(tabela.fator_carga(), 0)

    def test_lapide_e_reaproveitada_na_insercao(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        tabela.inserir("a", 1)
        tabela.remover("a")
        tabela.inserir("a", 2)
        self.assertEqual(tabela.buscar("a"), 2)
        self.assertEqual(tabela.estatisticas()["lapides"], 0)

    def test_reinserir_chave_que_esta_depois_de_lapide(self):
        """
        O caso que a sondagem precisa tratar com cuidado.

        Ao inserir, a primeira lápide encontrada é um lugar possível, mas a
        busca tem de continuar: a chave pode já existir mais adiante. Parar na
        lápide criaria uma segunda cópia da mesma chave.
        """
        tabela = TabelaHashAberta(capacidade_inicial=11)
        a, b = chaves_que_colidem(11, 2)
        tabela.inserir(a, 1)
        tabela.inserir(b, 2)
        tabela.remover(a)

        tabela.inserir(b, 99)

        self.assertEqual(tabela.buscar(b), 99)
        self.assertEqual(len(tabela), 1)

    def test_lapides_somem_no_redimensionamento(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        for i in range(30):
            tabela.inserir(f"produto-{i}", i)
            tabela.remover(f"produto-{i}")
        # Muitas remoções forçam reconstrução, e ela limpa as lápides.
        self.assertLess(tabela.estatisticas()["lapides"], 30)


class TestRedimensionamento(unittest.TestCase):

    def test_nada_se_perde(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        for i in range(200):
            tabela.inserir(f"produto-{i}", f"valor-{i}")

        self.assertEqual(len(tabela), 200)
        for i in range(200):
            self.assertEqual(tabela.buscar(f"produto-{i}"), f"valor-{i}")

    def test_fator_de_carga_fica_sob_controle(self):
        tabela = TabelaHashAberta(capacidade_inicial=11)
        for i in range(200):
            tabela.inserir(f"produto-{i}", i)
        self.assertLessEqual(tabela.fator_carga(),
                             TabelaHashAberta.FATOR_CARGA_MAXIMO)


class TestEquivalenciaComOEncadeamento(unittest.TestCase):
    """
    As duas estratégias precisam ser indistinguíveis por fora.

    Se elas divergirem em comportamento, o benchmark estaria comparando coisas
    diferentes e os números não significariam nada.
    """

    def test_mesmo_resultado_nas_duas(self):
        encadeada = TabelaHash(capacidade_inicial=11)
        aberta = TabelaHashAberta(capacidade_inicial=11)

        for i in range(150):
            encadeada.inserir(f"produto-{i}", i)
            aberta.inserir(f"produto-{i}", i)
        for i in range(0, 150, 3):
            encadeada.remover(f"produto-{i}")
            aberta.remover(f"produto-{i}")

        self.assertEqual(len(encadeada), len(aberta))
        self.assertEqual(set(encadeada.chaves()), set(aberta.chaves()))
        for i in range(150):
            self.assertEqual(encadeada.buscar(f"produto-{i}"),
                             aberta.buscar(f"produto-{i}"))

    def test_custo_de_busca_existe_nas_duas(self):
        encadeada = TabelaHash(capacidade_inicial=11)
        aberta = TabelaHashAberta(capacidade_inicial=11)
        encadeada.inserir("tenis", 1)
        aberta.inserir("tenis", 1)
        self.assertEqual(encadeada.custo_de_busca("tenis"), 1)
        self.assertEqual(aberta.custo_de_busca("tenis"), 1)


if __name__ == "__main__":
    unittest.main()
