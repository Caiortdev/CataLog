"""
Testes da tabela de dispersão.

Observação sobre o uso de dict neste arquivo: na função auxiliar abaixo usamos
um dicionário do Python para agrupar chaves por balde. Isso não contradiz a
decisão do projeto — aqui o dicionário é ferramenta de apoio do teste, não a
estrutura que está sendo avaliada. A estrutura testada é a nossa TabelaHash.
"""

import unittest

from catalogo.hashtable import TabelaHash, hash_djb2, _proximo_primo


def chaves_que_colidem(capacidade, quantidade=2, limite=20000):
    """
    Procura chaves diferentes que caem no mesmo balde.

    Colisão não é um acidente raro que a gente precisa torcer para acontecer:
    com 11 baldes e um alfabeto infinito de strings, ela é inevitável. Esta
    função só acha um exemplo concreto para o teste, por força bruta.
    """
    grupos = {}
    for i in range(limite):
        chave = f"chave-{i}"
        indice = hash_djb2(chave) % capacidade
        grupos.setdefault(indice, []).append(chave)
        if len(grupos[indice]) == quantidade:
            return grupos[indice]
    raise RuntimeError("não encontrou colisão dentro do limite de busca")


class TestFuncaoHash(unittest.TestCase):

    def test_hash_e_deterministico(self):
        # O ponto que justifica não usarmos hash() nativo: mesmo texto,
        # sempre o mesmo número.
        self.assertEqual(hash_djb2("tenis"), hash_djb2("tenis"))

    def test_textos_diferentes_dao_numeros_diferentes(self):
        self.assertNotEqual(hash_djb2("tenis"), hash_djb2("camisa"))

    def test_hash_cabe_em_32_bits(self):
        valor = hash_djb2("texto bem mais longo para forcar o acumulador a crescer")
        self.assertGreaterEqual(valor, 0)
        self.assertLess(valor, 2 ** 32)

    def test_proximo_primo(self):
        self.assertEqual(_proximo_primo(10), 11)
        self.assertEqual(_proximo_primo(11), 11)
        self.assertEqual(_proximo_primo(22), 23)


class TestOperacoesBasicas(unittest.TestCase):

    def setUp(self):
        self.tabela = TabelaHash(capacidade_inicial=11)

    def test_inserir_e_buscar(self):
        self.tabela.inserir("tenis", "Tênis de corrida")
        self.assertEqual(self.tabela.buscar("tenis"), "Tênis de corrida")

    def test_buscar_chave_inexistente_devolve_padrao(self):
        self.assertIsNone(self.tabela.buscar("nao-existe"))
        self.assertEqual(self.tabela.buscar("nao-existe", "vazio"), "vazio")

    def test_inserir_chave_repetida_atualiza_sem_duplicar(self):
        self.tabela.inserir("tenis", "versão antiga")
        self.tabela.inserir("tenis", "versão nova")
        self.assertEqual(self.tabela.buscar("tenis"), "versão nova")
        self.assertEqual(len(self.tabela), 1)

    def test_remover_devolve_valor_e_diminui_tamanho(self):
        self.tabela.inserir("tenis", "Tênis de corrida")
        removido = self.tabela.remover("tenis")
        self.assertEqual(removido, "Tênis de corrida")
        self.assertEqual(len(self.tabela), 0)
        self.assertIsNone(self.tabela.buscar("tenis"))

    def test_remover_chave_inexistente_levanta_erro(self):
        with self.assertRaises(KeyError):
            self.tabela.remover("nao-existe")

    def test_operador_in(self):
        self.tabela.inserir("tenis", 1)
        self.assertIn("tenis", self.tabela)
        self.assertNotIn("camisa", self.tabela)


class TestColisoes(unittest.TestCase):
    """
    O teste mais importante do arquivo.

    Uma tabela hash só é correta se chaves diferentes que caem no mesmo balde
    continuarem acessíveis de forma independente. Se o encadeamento estiver
    errado, uma sobrescreve a outra e o bug passa despercebido em testes
    comuns, porque colisão com poucos dados é rara.
    """

    def test_chaves_colidindo_convivem_no_mesmo_balde(self):
        tabela = TabelaHash(capacidade_inicial=11)
        primeira, segunda = chaves_que_colidem(capacidade=11, quantidade=2)

        tabela.inserir(primeira, "produto A")
        tabela.inserir(segunda, "produto B")

        self.assertEqual(tabela.buscar(primeira), "produto A")
        self.assertEqual(tabela.buscar(segunda), "produto B")
        self.assertEqual(len(tabela), 2)
        self.assertEqual(tabela.colisoes, 1)

    def test_remover_do_meio_da_corrente_nao_quebra_o_resto(self):
        tabela = TabelaHash(capacidade_inicial=11)
        a, b, c = chaves_que_colidem(capacidade=11, quantidade=3)

        tabela.inserir(a, 1)
        tabela.inserir(b, 2)
        tabela.inserir(c, 3)

        # Inserimos no início da corrente, então a ordem física é c -> b -> a.
        # Removendo b, testamos o religamento de ponteiros no meio.
        tabela.remover(b)

        self.assertEqual(tabela.buscar(a), 1)
        self.assertIsNone(tabela.buscar(b))
        self.assertEqual(tabela.buscar(c), 3)


class TestRedimensionamento(unittest.TestCase):

    def test_tabela_cresce_quando_passa_do_fator_de_carga(self):
        tabela = TabelaHash(capacidade_inicial=11)
        capacidade_inicial = tabela.estatisticas()["capacidade"]

        # 11 * 0.75 = 8.25, então o nono elemento dispara o redimensionamento.
        for i in range(9):
            tabela.inserir(f"produto-{i}", i)

        self.assertGreater(tabela.estatisticas()["capacidade"], capacidade_inicial)
        self.assertLessEqual(tabela.fator_carga(), TabelaHash.FATOR_CARGA_MAXIMO)

    def test_nenhum_elemento_se_perde_no_redimensionamento(self):
        """
        Este é o teste que pega o erro clássico: copiar os baldes para um vetor
        maior sem recalcular os índices. Os dados continuam na memória, mas a
        busca procura no lugar errado e não acha nada.
        """
        tabela = TabelaHash(capacidade_inicial=11)
        total = 200

        for i in range(total):
            tabela.inserir(f"produto-{i}", f"valor-{i}")

        self.assertEqual(len(tabela), total)
        for i in range(total):
            self.assertEqual(tabela.buscar(f"produto-{i}"), f"valor-{i}")

    def test_distribuicao_continua_saudavel_com_muitos_dados(self):
        """
        Checagem de qualidade da função de dispersão, não de correção.

        Com 200 chaves distribuídas em centenas de baldes, nenhuma corrente
        deveria ficar muito longa. Se a maior corrente passasse de 10,
        significaria que a djb2 está concentrando chaves e a busca deixaria de
        ser O(1) na prática.
        """
        tabela = TabelaHash(capacidade_inicial=11)
        for i in range(200):
            tabela.inserir(f"produto-{i}", i)

        self.assertLess(tabela.estatisticas()["maior_corrente"], 10)


class TestPercursos(unittest.TestCase):

    def test_chaves_e_itens_devolvem_tudo(self):
        tabela = TabelaHash(capacidade_inicial=11)
        esperado = {"a": 1, "b": 2, "c": 3}
        for chave, valor in esperado.items():
            tabela.inserir(chave, valor)

        self.assertEqual(set(tabela.chaves()), set(esperado))
        self.assertEqual(dict(tabela.itens()), esperado)


if __name__ == "__main__":
    unittest.main()
