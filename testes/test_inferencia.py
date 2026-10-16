"""Testes da inferência de regras a partir do catálogo."""

import unittest

from catalogo.catalogo import Catalogo
from catalogo.inferencia import formatar, inferir_regras


class GeradorFixo:
    """
    Gerador de tags controlado, para os testes não dependerem do vocabulário.

    Com ele, cada produto recebe exatamente as tags que o teste determinou, e
    fica claro o que está sendo verificado: a inferência, e não a qualidade do
    vocabulário.
    """

    def __init__(self, por_nome):
        self._por_nome = por_nome

    def gerar(self, nome, descricao=""):
        return list(self._por_nome.get(nome, []))

    def termos_conhecidos(self):
        return 0


class TestInferencia(unittest.TestCase):

    def montar(self, produtos, tags_por_nome):
        catalogo = Catalogo(gerador_de_tags=GeradorFixo(tags_por_nome))
        for nome, descricao in produtos:
            catalogo.cadastrar(nome, descricao)
        return catalogo

    def test_descobre_regra_quando_todos_concordam(self):
        catalogo = self.montar(
            [("Panela de pressao", "de inox"),
             ("Panela wok", "de inox"),
             ("Frigideira grande", "de inox")],
            {"Panela de pressao": ["cozinha"], "Panela wok": ["cozinha"],
             "Frigideira grande": ["cozinha"]},
        )
        sugestoes = inferir_regras(catalogo, minimo=3)
        self.assertIn(("inox", "cozinha", 3), sugestoes)

    def test_nao_sugere_quando_um_produto_discorda(self):
        """
        O critério é "todos", não "a maioria", e de propósito.

        Uma regra que vale em dois de três casos vai classificar o terceiro
        errado — e em silêncio, que é o pior jeito de errar.
        """
        catalogo = self.montar(
            [("Panela de inox", ""), ("Frigideira de inox", ""),
             ("Parafuso de inox", "")],
            {"Panela de inox": ["cozinha"], "Frigideira de inox": ["cozinha"],
             "Parafuso de inox": ["ferramenta"]},
        )
        sugestoes = inferir_regras(catalogo, minimo=3)
        self.assertEqual([s for s in sugestoes if s[0] == "inox"], [])

    def test_respeita_o_minimo_de_produtos(self):
        """
        Com dois produtos, qualquer coincidência viraria regra. O mínimo existe
        para que a concordância signifique alguma coisa.
        """
        catalogo = self.montar(
            [("Panela de inox", ""), ("Frigideira de inox", "")],
            {"Panela de inox": ["cozinha"], "Frigideira de inox": ["cozinha"]},
        )
        self.assertEqual(inferir_regras(catalogo, minimo=3), [])
        self.assertTrue(inferir_regras(catalogo, minimo=2))

    def test_ignora_palavras_que_o_vocabulario_ja_conhece(self):
        """Sugerir que "tenis" significa "calcado" não informa nada a ninguém."""
        catalogo = self.montar(
            [("Tenis de corrida", ""), ("Tenis de caminhada", ""),
             ("Tenis casual", "")],
            {"Tenis de corrida": ["calcado"], "Tenis de caminhada": ["calcado"],
             "Tenis casual": ["calcado"]},
        )
        sugestoes = inferir_regras(catalogo, minimo=3)
        self.assertEqual([s for s in sugestoes if s[0] == "tenis"], [])
        # Sem o filtro, a regra apareceria.
        sugestoes = inferir_regras(catalogo, minimo=3, ignorar_conhecidas=False)
        self.assertIn(("tenis", "calcado", 3), sugestoes)

    def test_nao_sugere_palavra_que_e_a_propria_tag(self):
        catalogo = self.montar(
            [("Item esportivo um", "para corrida"),
             ("Item esportivo dois", "para corrida"),
             ("Item esportivo tres", "para corrida")],
            {f"Item esportivo {n}": ["corrida"] for n in ("um", "dois", "tres")},
        )
        sugestoes = inferir_regras(catalogo, minimo=3)
        # A regra "corrida -> corrida" não acrescenta nada. As outras palavras
        # do texto podem sugerir a tag "corrida" legitimamente, e sugerem —
        # é só a identidade entre palavra e tag que é descartada.
        self.assertEqual([s for s in sugestoes if s[0] == s[1]], [])
        self.assertTrue(any(s[1] == "corrida" for s in sugestoes))

    def test_catalogo_vazio(self):
        self.assertEqual(inferir_regras(Catalogo()), [])

    def test_ordena_pela_quantidade_de_evidencia(self):
        catalogo = self.montar(
            [("Panela de inox", "resistente"), ("Frigideira de inox", "resistente"),
             ("Jarra de inox", "resistente"), ("Travessa de inox", "")],
            {n: ["cozinha"] for n in ["Panela de inox", "Frigideira de inox",
                                      "Jarra de inox", "Travessa de inox"]},
        )
        sugestoes = inferir_regras(catalogo, minimo=3)
        # "inox" aparece em 4 produtos, "resistente" em 3.
        self.assertEqual(sugestoes[0][0], "inox")

    def test_formatar_sem_sugestoes(self):
        self.assertIn("Nenhuma regra", formatar([])[0])

    def test_formatar_produz_linha_colavel(self):
        """A saída é copiável direto para o vocabulario.py."""
        linhas = formatar([("inox", "cozinha", 3)])
        self.assertTrue(any('("inox", ("cozinha",)),' in l for l in linhas))


if __name__ == "__main__":
    unittest.main()
