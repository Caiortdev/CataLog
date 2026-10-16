"""Testes da normalização de texto e da geração de tags."""

import unittest

from catalogo.tagger import GeradorDeTags
from catalogo.texto import normalizar, remover_acentos, singularizar, tokenizar


class TestNormalizacao(unittest.TestCase):

    def test_remove_acentos_preservando_a_letra(self):
        self.assertEqual(remover_acentos("tênis"), "tenis")
        self.assertEqual(remover_acentos("calção"), "calcao")
        self.assertEqual(remover_acentos("ÁÉÍÓÚ"), "AEIOU")

    def test_normalizar_baixa_caixa_e_tira_pontuacao(self):
        self.assertEqual(normalizar("Tênis, Azul!"), "tenis  azul ")

    def test_pontuacao_vira_espaco_e_nao_some(self):
        # Se a pontuação fosse apagada em vez de virar espaço, isto daria
        # a palavra inexistente "azulcorrida".
        self.assertEqual(tokenizar("azul,corrida"), ["azul", "corrida"])

    def test_tokenizar_descarta_stopwords(self):
        self.assertEqual(
            tokenizar("Tênis azul para corrida em asfalto"),
            ["tenis", "azul", "corrida", "asfalto"],
        )

    def test_tokenizar_ignora_espacos_sobrando(self):
        self.assertEqual(tokenizar("  tenis    azul  "), ["tenis", "azul"])

    def test_singularizar_e_seus_limites(self):
        self.assertEqual(singularizar("camisas"), "camisa")
        # Palavra curta é preservada para não destruir termos como "gas".
        self.assertEqual(singularizar("gas"), "gas")
        # Limitação assumida: "tenis" já é singular, mas a regra não sabe
        # disso. Quem protege contra isso é o GeradorDeTags, que só chama
        # esta função quando a palavra original não foi encontrada.
        self.assertEqual(singularizar("tenis"), "teni")


class TestGeracaoDeTags(unittest.TestCase):

    def setUp(self):
        self.gerador = GeradorDeTags()

    def test_exemplo_do_enunciado(self):
        """
        O caso que o professor vai testar primeiro.

        O enunciado dá as tags "calçado", "esporte", "corrida" e "azul" como
        exemplo, não como lista fechada ("ex:"). Por isso verificamos que elas
        estão presentes, e não que são exatamente as únicas — o sistema
        também deduz "cor", "asfalto" e "rua", que são tags legítimas e
        tornam a busca mais rica.
        """
        tags = self.gerador.gerar("Tênis azul", "para corrida em asfalto")

        for esperada in ("calcado", "esporte", "corrida", "azul"):
            self.assertIn(esperada, tags)

    def test_acento_e_caixa_nao_mudam_o_resultado(self):
        com_acento = self.gerador.gerar("Tênis Azul", "Corrida")
        sem_acento = self.gerador.gerar("tenis azul", "corrida")
        self.assertEqual(com_acento, sem_acento)

    def test_nao_repete_tag_vinda_de_palavras_diferentes(self):
        # "corrida" e "treino" disparam "esporte"; ela deve aparecer uma vez.
        tags = self.gerador.gerar("Tênis", "para corrida e treino")
        self.assertEqual(tags.count("esporte"), 1)

    def test_plural_e_reconhecido(self):
        tags = self.gerador.gerar("Camisas de algodão", "")
        self.assertIn("vestuario", tags)

    def test_cor_no_feminino_e_reconhecida(self):
        """
        Regressão encontrada rodando o programa, não escrevendo testes.

        "Chuteira preta" saía sem nenhuma tag de cor, porque a regra de
        singular não trata gênero e "preta" não estava no vocabulário. A
        correção foi listar as formas femininas; este teste existe para que o
        problema não volte sem ninguém perceber.
        """
        tags = self.gerador.gerar("Chuteira preta", "para futebol")
        self.assertIn("preto", tags)
        self.assertIn("calcado", tags)
        self.assertEqual(
            self.gerador.gerar("Camisa branca", ""),
            self.gerador.gerar("Camisa branco", ""),
        )

    def test_palavra_desconhecida_e_ignorada_sem_quebrar(self):
        tags = self.gerador.gerar("Xyzabc Qwerty", "produto sem vocabulario")
        self.assertEqual(tags, [])

    def test_texto_vazio_nao_quebra(self):
        self.assertEqual(self.gerador.gerar("", ""), [])

    def test_ordem_segue_a_descoberta_no_texto(self):
        # O nome vem antes da descrição, então as tags do nome vêm primeiro.
        tags = self.gerador.gerar("Tênis", "azul")
        self.assertLess(tags.index("calcado"), tags.index("azul"))

    def test_vocabulario_proprio_substitui_o_padrao(self):
        """
        Mostra por que o vocabulário é injetado no construtor: dá para testar
        o algoritmo isolado do conteúdo do arquivo de vocabulário.
        """
        gerador = GeradorDeTags([("guarda", ("protecao",))])
        self.assertEqual(gerador.gerar("Guarda chuva", ""), ["protecao"])
        self.assertEqual(gerador.termos_conhecidos(), 1)


class ProfessorFalso:
    """Devolve sempre a mesma categoria e conta quantas vezes foi consultado."""

    def __init__(self, categoria="brinquedo"):
        self.categoria = categoria
        self.consultas = 0

    def categoria_de(self, texto, usar_generalizacao=True):
        self.consultas += 1
        return self.categoria


class TestQuandoConsultarOProfessor(unittest.TestCase):
    """
    O critério que decide se o modelo precisa ser chamado.

    Ele mudou depois de um defeito visto rodando o programa: "Violão acústico
    com cordas de nylon" saía como "nylon, material" e nada mais, porque
    reconhecer uma palavra da descrição contava como "já temos tags" e o
    modelo nunca era consultado.
    """

    def test_produto_sem_categoria_consulta_o_professor(self):
        professor = ProfessorFalso("brinquedo")
        gerador = GeradorDeTags(professor=professor)

        tags = gerador.gerar("Violao acustico", "com cordas de nylon")

        self.assertEqual(professor.consultas, 1)
        # A categoria soma às tags do vocabulário, não as substitui.
        self.assertIn("nylon", tags)
        self.assertIn("material", tags)
        self.assertIn("brinquedo", tags)

    def test_produto_com_categoria_nao_consulta(self):
        """
        "Tênis azul" já tem "calcado", que diz o que o produto é. Consultar o
        modelo aqui seria gastar meio segundo para não aprender nada.
        """
        professor = ProfessorFalso()
        gerador = GeradorDeTags(professor=professor)

        gerador.gerar("Tenis azul", "para corrida em asfalto")

        self.assertEqual(professor.consultas, 0)

    def test_produto_sem_tag_nenhuma_consulta(self):
        professor = ProfessorFalso("acessorio")
        gerador = GeradorDeTags(professor=professor)

        self.assertEqual(gerador.gerar("Xyzabc qwerty", ""), ["acessorio"])
        self.assertEqual(professor.consultas, 1)

    def test_categoria_repetida_nao_duplica(self):
        professor = ProfessorFalso("material")
        gerador = GeradorDeTags(professor=professor)

        tags = gerador.gerar("Violao acustico", "com cordas de nylon")

        self.assertEqual(tags.count("material"), 1)

    def test_sem_professor_o_comportamento_e_o_de_antes(self):
        self.assertEqual(
            GeradorDeTags().gerar("Violao acustico", "com cordas de nylon"),
            ["nylon", "material"],
        )


class TestIaComoCaminhoPrincipal(unittest.TestCase):
    """
    O modo que segue o item 2 do enunciado ao pé da letra.

    Aqui o modelo analisa todo produto, e não só os que o vocabulário não
    reconhece. A divisão de trabalho entre os dois continua, mas invertida na
    ordem: a categoria vem do modelo e encabeça a lista; cor, material e uso
    vêm do vocabulário.

    Essa divisão não é arbitrária. O modelo acerta categorias, inclusive de
    palavras que ninguém cadastrou, e erra atributos — chegou a atribuir a cor
    azul a uma "Camisa de algodão" que não menciona cor nenhuma.
    """

    def test_consulta_o_modelo_mesmo_quando_o_vocabulario_sabe(self):
        """
        A diferença em relação ao modo complementar.

        "Tênis azul" já receberia "calcado" do vocabulário. No modo
        complementar isso bastaria e o modelo não seria chamado; aqui ele é.
        """
        professor = ProfessorFalso("esporte")
        gerador = GeradorDeTags(professor=professor, ia_primeiro=True)

        gerador.gerar("Tenis azul", "para corrida em asfalto")

        self.assertEqual(professor.consultas, 1)

    def test_categoria_do_modelo_vem_primeiro(self):
        professor = ProfessorFalso("esporte")
        gerador = GeradorDeTags(professor=professor, ia_primeiro=True)

        tags = gerador.gerar("Tenis azul", "para corrida em asfalto")

        self.assertEqual(tags[0], "esporte")

    def test_atributos_do_vocabulario_sao_preservados(self):
        """
        O modelo entra para dizer a categoria, não para substituir o resto.

        Se ele apagasse as tags do vocabulário, perderíamos cor e material —
        e justamente esses o modelo erra.
        """
        professor = ProfessorFalso("esporte")
        gerador = GeradorDeTags(professor=professor, ia_primeiro=True)

        tags = gerador.gerar("Tenis azul", "para corrida em asfalto")

        for esperada in ("azul", "cor", "corrida", "asfalto"):
            self.assertIn(esperada, tags)

    def test_as_quatro_tags_do_enunciado_continuam_saindo(self):
        """O caso exato do slide, no modo que o slide descreve."""
        professor = ProfessorFalso("esporte")
        gerador = GeradorDeTags(professor=professor, ia_primeiro=True)

        tags = gerador.gerar("Tênis azul", "para corrida em asfalto")

        for esperada in ("calcado", "esporte", "corrida", "azul"):
            self.assertIn(esperada, tags)

    def test_categoria_repetida_nao_duplica(self):
        # O modelo diz "calcado" e o vocabulário também; a tag aparece uma vez.
        professor = ProfessorFalso("calcado")
        gerador = GeradorDeTags(professor=professor, ia_primeiro=True)

        tags = gerador.gerar("Tenis azul", "para corrida")

        self.assertEqual(tags.count("calcado"), 1)

    def test_modelo_sem_resposta_nao_derruba_o_cadastro(self):
        """
        Quando o modelo não responde, o vocabulário assume sozinho.

        É o que mantém o trabalho rodando em uma máquina sem Apple
        Intelligence: o modo pode ser pedido e o programa continua funcionando.
        """
        class ProfessorMudo(ProfessorFalso):
            def categoria_de(self, texto, usar_generalizacao=True):
                self.consultas += 1
                return None

        gerador = GeradorDeTags(professor=ProfessorMudo(), ia_primeiro=True)
        tags = gerador.gerar("Tenis azul", "para corrida em asfalto")

        self.assertIn("calcado", tags)
        self.assertIn("azul", tags)


if __name__ == "__main__":
    unittest.main()