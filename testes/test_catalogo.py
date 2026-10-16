"""Testes do catálogo e do índice invertido."""

import unittest

from catalogo.catalogo import Catalogo


class TestCadastro(unittest.TestCase):

    def setUp(self):
        self.catalogo = Catalogo()

    def test_produto_recebe_identificador_sequencial(self):
        primeiro = self.catalogo.cadastrar("Tênis azul", "para corrida")
        segundo = self.catalogo.cadastrar("Camisa branca", "de algodão")
        self.assertEqual(primeiro.identificador, "P001")
        self.assertEqual(segundo.identificador, "P002")

    def test_produto_ja_nasce_com_tags(self):
        produto = self.catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
        self.assertIn("calcado", produto.tags)
        self.assertIn("corrida", produto.tags)

    def test_obter_pelo_identificador(self):
        produto = self.catalogo.cadastrar("Tênis azul", "para corrida")
        self.assertIs(self.catalogo.obter("P001"), produto)

    def test_identificador_inexistente_devolve_none(self):
        self.assertIsNone(self.catalogo.obter("P999"))

    def test_nome_vazio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            self.catalogo.cadastrar("   ", "descrição qualquer")

    def test_produto_sem_tag_reconhecida_ainda_e_cadastrado(self):
        # Não achar tag nenhuma não é erro: o produto existe, só não é
        # alcançável por busca de tag ainda.
        produto = self.catalogo.cadastrar("Xyzabc", "qwerty")
        self.assertEqual(produto.tags, [])
        self.assertEqual(len(self.catalogo), 1)


class TestBusca(unittest.TestCase):

    def setUp(self):
        self.catalogo = Catalogo()
        self.tenis = self.catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
        self.camisa = self.catalogo.cadastrar("Camisa azul", "de algodão")
        self.chuteira = self.catalogo.cadastrar("Chuteira preta", "para futebol na grama")

    def test_busca_por_tag_devolve_so_quem_tem_a_tag(self):
        achados = self.catalogo.buscar_por_tag("corrida")
        self.assertEqual(achados, [self.tenis])

    def test_tag_compartilhada_devolve_varios(self):
        achados = self.catalogo.buscar_por_tag("azul")
        self.assertCountEqual(achados, [self.tenis, self.camisa])

    def test_tag_inexistente_devolve_lista_vazia(self):
        self.assertEqual(self.catalogo.buscar_por_tag("submarino"), [])

    def test_busca_aceita_acento_e_maiuscula(self):
        """
        Caso real: o cliente digita "CALÇADO" com acento e maiúscula, mas a tag
        foi guardada como "calcado". Se a busca não normalizasse o termo, o
        hash seria outro e o produto não apareceria.
        """
        self.assertEqual(
            self.catalogo.buscar_por_tag("CALÇADO"),
            self.catalogo.buscar_por_tag("calcado"),
        )
        self.assertIn(self.tenis, self.catalogo.buscar_por_tag("CALÇADO"))

    def test_busca_por_varias_tags_exige_todas(self):
        # "azul" sozinho traz dois produtos; junto com "calcado", só o tênis.
        achados = self.catalogo.buscar_por_tags(["azul", "calcado"])
        self.assertEqual(achados, [self.tenis])

    def test_uma_tag_inexistente_zera_o_resultado(self):
        achados = self.catalogo.buscar_por_tags(["azul", "submarino"])
        self.assertEqual(achados, [])

    def test_lista_de_tags_vazia_devolve_vazio(self):
        self.assertEqual(self.catalogo.buscar_por_tags([]), [])
        self.assertEqual(self.catalogo.buscar_por_tags(["  "]), [])

    def test_busca_por_frase_livre(self):
        achados = self.catalogo.buscar_por_texto("tenis para corrida")
        self.assertEqual(achados, [self.tenis])

    def test_frase_sem_termo_conhecido_devolve_vazio(self):
        self.assertEqual(self.catalogo.buscar_por_texto("qwerty xyzabc"), [])


class TestRemocao(unittest.TestCase):
    """
    O teste que justifica a existência do método remover() por completo.

    O erro clássico é apagar o produto só da primeira tabela. A listagem fica
    certa e parece que funcionou, mas o identificador continua pendurado no
    índice de tags. Aí a busca devolve um produto fantasma ou, pior, um None
    que explode na hora de exibir.
    """

    def setUp(self):
        self.catalogo = Catalogo()
        self.tenis = self.catalogo.cadastrar("Tênis azul", "para corrida")
        self.camisa = self.catalogo.cadastrar("Camisa azul", "de algodão")

    def test_produto_removido_some_da_busca_por_identificador(self):
        self.catalogo.remover("P001")
        self.assertIsNone(self.catalogo.obter("P001"))
        self.assertEqual(len(self.catalogo), 1)

    def test_produto_removido_some_do_indice_de_tags(self):
        self.catalogo.remover("P001")
        self.assertEqual(self.catalogo.buscar_por_tag("azul"), [self.camisa])
        self.assertNotIn(None, self.catalogo.buscar_por_tag("azul"))

    def test_tag_que_ficou_sem_ninguem_sai_do_indice(self):
        # "corrida" só existia por causa do tênis.
        self.assertIn("corrida", self.catalogo.tags_conhecidas())
        self.catalogo.remover("P001")
        self.assertNotIn("corrida", self.catalogo.tags_conhecidas())

    def test_remover_identificador_inexistente_levanta_erro(self):
        with self.assertRaises(KeyError):
            self.catalogo.remover("P999")


class TestIndiceDeTexto(unittest.TestCase):
    """
    O índice literal, que busca pelas palavras escritas no produto.

    Ele existe por causa de uma lacuna medida: um produto classificado pelo
    modelo recebe uma única tag ("cozinha"), enquanto um reconhecido pelo
    vocabulário recebe cinco ou sete. Quem procurasse por "ceramica" não
    achava a frigideira, embora a palavra estivesse escrita nela.
    """

    def setUp(self):
        self.catalogo = Catalogo()
        self.tenis = self.catalogo.cadastrar("Tênis azul", "para corrida em asfalto")
        self.camisa = self.catalogo.cadastrar("Camisa", "de algodão com bolso frontal")

    def test_acha_palavra_que_nao_e_tag(self):
        # "bolso" não é tag de nada; só existe no texto da camisa.
        self.assertEqual(self.catalogo.buscar_por_tag("bolso"), [])
        self.assertEqual(self.catalogo.buscar_por_palavra("bolso"), [self.camisa])

    def test_tag_semantica_nao_esta_no_indice_literal(self):
        """
        O outro lado da moeda: "calcado" não está escrito no produto.

        Achá-lo exige saber que tênis é um calçado, e isso só o índice de tags
        faz. Nenhum dos dois índices substitui o outro.
        """
        self.assertEqual(self.catalogo.buscar_por_tag("calcado"), [self.tenis])
        self.assertEqual(self.catalogo.buscar_por_palavra("calcado"), [])

    def test_palavra_presente_nos_dois_indices(self):
        # "corrida" está escrita no texto e também é tag.
        self.assertEqual(self.catalogo.buscar_por_tag("corrida"), [self.tenis])
        self.assertEqual(self.catalogo.buscar_por_palavra("corrida"), [self.tenis])

    def test_busca_literal_normaliza_o_termo(self):
        self.assertEqual(self.catalogo.buscar_por_palavra("ALGODÃO"), [self.camisa])

    def test_palavra_de_ligacao_nao_entra_no_indice(self):
        # "de" e "para" aparecem nos textos, mas apontariam para o catálogo
        # inteiro e não serviriam para filtrar nada.
        self.assertEqual(self.catalogo.buscar_por_palavra("de"), [])
        self.assertEqual(self.catalogo.buscar_por_palavra("para"), [])

    def test_remocao_limpa_o_indice_literal(self):
        """
        Mesmo cuidado que o índice de tags exige: remover só da tabela de
        produtos deixaria identificadores órfãos apontando para o nada.
        """
        self.catalogo.remover(self.camisa.identificador)
        self.assertEqual(self.catalogo.buscar_por_palavra("bolso"), [])
        self.assertNotIn(None, self.catalogo.buscar_por_palavra("algodao"))


class TestEscala(unittest.TestCase):

    def test_catalogo_grande_continua_consistente(self):
        """
        Enche o catálogo o bastante para forçar vários redimensionamentos das
        duas tabelas, e confere que nada se perdeu no caminho.
        """
        catalogo = Catalogo()
        for i in range(300):
            catalogo.cadastrar(f"Tênis modelo {i}", "para corrida em asfalto")

        self.assertEqual(len(catalogo), 300)
        self.assertEqual(len(catalogo.buscar_por_tag("corrida")), 300)
        self.assertEqual(len(catalogo.todos()), 300)

        estatisticas = catalogo.estatisticas()
        self.assertLessEqual(estatisticas["produtos"]["fator_carga"], 0.75)
        self.assertLess(estatisticas["produtos"]["maior_corrente"], 10)


if __name__ == "__main__":
    unittest.main()
