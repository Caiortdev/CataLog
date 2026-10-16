"""
Testes do professor do vocabulário.

Quase tudo aqui roda sem o modelo. Isso é proposital e é a mesma ideia do
desenho que está sendo testado: o conhecimento mora no arquivo de cache, não no
modelo. Então dá para verificar o comportamento inteiro — consulta, memória,
recusa, falha — alimentando o cache na mão.

Só a última classe chama o modelo de verdade, e ela se desativa sozinha quando
ele não está disponível.
"""

import json
import os
import pathlib
import tempfile
import unittest

from catalogo.professor import (BINARIO, CATEGORIAS, DESCONHECIDA,
                               FONTE_SWIFT, Professor, palavra_principal)
from catalogo.tagger import GeradorDeTags


class TestCacheEmDisco(unittest.TestCase):
    """
    O professor sem modelo nenhum, só com o que já foi aprendido antes.

    Este é o cenário da máquina de quem for avaliar o trabalho: sem Apple
    Intelligence, mas com o arquivo de aprendizado que veio junto com o
    projeto. Precisa funcionar.
    """

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "aprendido.json")

    def tearDown(self):
        self.pasta.cleanup()

    def escrever_cache(self, dados):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo)

    def test_aproveita_o_que_ja_foi_aprendido(self):
        self.escrever_cache({"cafeteira eletrica": "cozinha"})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(professor.categoria_de("Cafeteira elétrica"), "cozinha")

    def test_normaliza_antes_de_procurar(self):
        """
        A chave do cache passa pela mesma normalização do resto do projeto.

        Sem isso, "Cafeteira Elétrica" e "cafeteira eletrica" seriam duas
        entradas diferentes, e o cache perderia metade dos acertos.
        """
        self.escrever_cache({"cafeteira eletrica": "cozinha"})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(professor.categoria_de("CAFETEIRA ELÉTRICA!"), "cozinha")

    def test_desconhecida_nao_vira_tag(self):
        """
        Lembrar que o modelo não soube é diferente de ter uma resposta.

        Guardamos "desconhecida" no arquivo para não perguntar de novo sobre o
        mesmo produto, mas ela nunca vira tag: uma tag "desconhecida" apontaria
        para todos os produtos estranhos do catálogo e não ajudaria ninguém.
        """
        self.escrever_cache({"xyzabc qwerty": DESCONHECIDA})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertIsNone(professor.categoria_de("Xyzabc qwerty"))

    def test_sem_modelo_e_sem_cache_nao_inventa(self):
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertIsNone(professor.categoria_de("Produto nunca visto"))

    def test_cache_corrompido_nao_derruba_o_programa(self):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write("isto não é json")
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertIsNone(professor.categoria_de("qualquer coisa"))
        self.assertTrue(professor.avisos)

    def test_texto_vazio(self):
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertIsNone(professor.categoria_de("   "))


class TestIntegracaoComOGerador(unittest.TestCase):
    """
    Quando o gerador recorre ao professor, e quando não recorre.

    A regra é estreita de propósito: só quando o vocabulário não reconheceu
    nada. Os dois testes abaixo são as duas metades dessa regra.
    """

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "aprendido.json")
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump({"guardachuva dobravel": "acessorio",
                       "tenis azul": "esporte"}, arquivo)
        self.professor = Professor(self.caminho, consultar_modelo=False)
        self.gerador = GeradorDeTags(professor=self.professor)

    def tearDown(self):
        self.pasta.cleanup()

    def test_produto_desconhecido_recebe_a_categoria_aprendida(self):
        # Sem professor, "guarda-chuva" não gera tag nenhuma e o produto fica
        # invisível na busca.
        self.assertEqual(GeradorDeTags().gerar("Guarda-chuva dobravel", ""), [])
        self.assertEqual(self.gerador.gerar("Guarda-chuva dobravel", ""), ["acessorio"])

    def test_produto_conhecido_nao_consulta_o_professor(self):
        """
        O ponto mais importante do desenho.

        "Tenis azul" está no cache como "esporte", mas o vocabulário já
        reconhece a palavra. Se o professor fosse consultado mesmo assim, as
        tags do vocabulário seriam substituídas ou misturadas — e misturar as
        duas fontes é exatamente o que criava chaves divergentes na tabela
        hash ("calcado" de um lado, "calcados" do outro).
        """
        tags = self.gerador.gerar("Tenis azul", "para corrida")
        self.assertIn("calcado", tags)
        self.assertNotIn("esporte", [t for t in tags if t == "esporte"][1:])
        self.assertEqual(tags, GeradorDeTags().gerar("Tenis azul", "para corrida"))

    def test_gerador_sem_professor_continua_igual(self):
        """Garantia de que a mudança não alterou o comportamento antigo."""
        self.assertEqual(
            GeradorDeTags().gerar("Tenis azul", "para corrida em asfalto"),
            ["calcado", "esporte", "azul", "cor", "corrida", "asfalto", "rua"],
        )


class TestCategorias(unittest.TestCase):

    def test_categorias_batem_com_o_enum_do_swift(self):
        """
        A mesma lista existe em dois lugares, em duas linguagens.

        O Python precisa saber quais tags são categorias para decidir se já
        sabe o que um produto é; o Swift precisa do enum para restringir o que
        o modelo pode responder. Se alguém acrescentar uma categoria de um lado
        e esquecer do outro, o erro é silencioso: o Python passaria a tratar a
        categoria nova como se fosse um atributo qualquer, e consultaria o
        modelo para produtos que já estavam classificados.

        Em vez de confiar na disciplina de quem edita, este teste lê o arquivo
        Swift e compara.
        """
        fonte = pathlib.Path(FONTE_SWIFT).read_text(encoding="utf-8")
        dentro_do_enum = fonte.split("enum Categoria: String {")[1].split("}")[0]

        do_swift = set()
        for linha in dentro_do_enum.splitlines():
            linha = linha.strip()
            if linha.startswith("case "):
                for nome in linha[len("case "):].split(","):
                    do_swift.add(nome.strip())

        # "desconhecida" existe só no Swift: é a recusa, não uma categoria de
        # produto, e por isso nunca vira tag.
        do_swift.discard("desconhecida")

        self.assertEqual(do_swift, CATEGORIAS)


class TestPalavraPrincipal(unittest.TestCase):
    """
    A regra que escolhe qual palavra nomeia o produto.

    Ela existe porque o modelo falhou nessa tarefa. Pedindo a ele que
    apontasse o substantivo principal, devolveu a frase inteira em sete de
    oito casos, mesmo instruído a copiar uma palavra só. A regra abaixo
    acertou dezesseis de dezesseis.
    """

    def test_pega_o_substantivo_do_comeco(self):
        self.assertEqual(palavra_principal("Frigideira antiaderente de ceramica"),
                         "frigideira")
        self.assertEqual(palavra_principal("Trena a laser digital"), "trena")

    def test_ignora_palavra_de_ligacao(self):
        # "Jogo de facas" não pode virar "de".
        self.assertEqual(palavra_principal("Jogo de facas de cozinha"), "jogo")

    def test_nome_composto_fica_inteiro(self):
        """
        Nomes com hífen viram uma palavra só, e não duas.

        Antes "Guarda-chuva" era truncado para "guarda", e isso tinha uma
        consequência ruim: "guarda-roupa" também começa com "guarda", mas é um
        móvel. As duas coisas colidiam na mesma chave, e a detecção de
        ambiguidade acabava descartando a generalização das duas.

        Juntando as partes, elas viram palavras distintas, que é o que de fato
        são. O teste abaixo verifica justamente que não colidem.
        """
        self.assertEqual(palavra_principal("Guarda-chuva dobravel"), "guardachuva")
        self.assertEqual(palavra_principal("Guarda-roupa de 6 portas"), "guardaroupa")
        self.assertEqual(palavra_principal("Micro-ondas com grill"), "microondas")

    def test_hifen_entre_numeros_nao_junta(self):
        """A regra vale só entre letras: "aro 15 - novo" não vira "15novo"."""
        self.assertEqual(palavra_principal("Pneu aro 15 - novo"), "pneu")

    def test_texto_sem_palavra_util(self):
        self.assertIsNone(palavra_principal("de para com"))
        self.assertIsNone(palavra_principal(""))


class TestGeneralizacao(unittest.TestCase):
    """
    O que torna o aprendizado útil: aprender uma vez, valer para sempre.

    Sem isto, o cache guardaria frases inteiras e "Frigideira de teflon" seria
    um produto totalmente novo, custando outra consulta ao modelo, apesar de
    ser quase igual a uma frigideira já conhecida.
    """

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "aprendido.json")

    def tearDown(self):
        self.pasta.cleanup()

    def professor_com(self, aprendizados):
        professor = Professor(self.caminho, consultar_modelo=False)
        for texto, categoria in aprendizados:
            professor.ensinar(texto, categoria)
        return professor

    def test_palavra_aprendida_vale_para_produto_novo(self):
        professor = self.professor_com([("Frigideira antiaderente", "cozinha")])
        # Produto nunca visto, mas que usa a mesma palavra.
        self.assertEqual(professor.categoria_de("Frigideira de teflon grande"),
                         "cozinha")

    def test_palavra_ambigua_para_de_generalizar(self):
        """
        O caso que justifica a detecção de conflito.

        "Jogo" aparece em ferramenta e em cozinha. Generalizar para qualquer
        uma das duas faria o outro produto ser classificado errado, então a
        palavra é descartada como atalho e os dois passam a depender da frase.
        """
        professor = self.professor_com([
            ("Jogo de chaves de fenda", "ferramenta"),
            ("Jogo de facas de cozinha", "cozinha"),
        ])
        self.assertIn("jogo", professor.ambiguas)
        self.assertEqual(professor.categoria_de("Jogo de chaves de fenda"), "ferramenta")
        self.assertEqual(professor.categoria_de("Jogo de facas de cozinha"), "cozinha")
        # Um "jogo" novo não herda nenhuma das duas: seria chute.
        self.assertIsNone(professor.categoria_de("Jogo de tabuleiro"))

    def test_conflito_gera_aviso(self):
        professor = self.professor_com([
            ("Jogo de chaves de fenda", "ferramenta"),
            ("Jogo de facas de cozinha", "cozinha"),
        ])
        self.assertTrue(any("jogo" in aviso for aviso in professor.avisos))

    def test_frase_tem_precedencia_sobre_palavra(self):
        """
        Uma correção feita à mão precisa valer mesmo contra a palavra genérica.

        Aqui "panela" generaliza para cozinha, mas alguém registrou que esta
        panela específica é decoração. O registro específico ganha.
        """
        professor = self.professor_com([
            ("Panela de pressao", "cozinha"),
            ("Panela decorativa de parede", "decoracao"),
        ])
        self.assertEqual(professor.categoria_de("Panela decorativa de parede"),
                         "decoracao")

    def test_desconhecida_nunca_generaliza(self):
        """
        Se o modelo não reconheceu um produto, a culpa pode ser do texto e não
        da palavra. Marcar a palavra como "não significa nada" seria exagerado.
        """
        professor = self.professor_com([("Xyzabc qwerty", DESCONHECIDA)])
        self.assertEqual(professor.palavras_aprendidas, 0)

    def test_aprendizado_sobrevive_ao_arquivo(self):
        self.professor_com([("Frigideira antiaderente", "cozinha")])
        outro = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(outro.categoria_de("Frigideira de teflon"), "cozinha")

    def test_ambiguidade_sobrevive_ao_arquivo(self):
        """A marca de ambígua precisa persistir, senão o conflito volta."""
        self.professor_com([
            ("Jogo de chaves de fenda", "ferramenta"),
            ("Jogo de facas de cozinha", "cozinha"),
        ])
        outro = Professor(self.caminho, consultar_modelo=False)
        self.assertIn("jogo", outro.ambiguas)
        self.assertIsNone(outro.categoria_de("Jogo de tabuleiro"))

    def test_formato_antigo_e_convertido(self):
        """
        O arquivo já existia em um formato mais simples, só com frases. Jogar
        fora o que foi aprendido porque o formato mudou obrigaria a consultar o
        modelo de novo para tudo.
        """
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump({"frigideira antiaderente": "cozinha"}, arquivo)
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(professor.aprendidos, 1)
        self.assertEqual(professor.categoria_de("Frigideira de teflon"), "cozinha")


class TestFilaDeRevisao(unittest.TestCase):
    """
    A fila de produtos que o modelo classificou de forma hesitante.

    Ela vem da auto-consistência: perguntar a mesma coisa várias vezes com o
    modelo livre para variar e ver se ele muda de ideia. É importante entender
    o que esse sinal vale, porque medimos: contra sete classificações que uma
    pessoa teve de corrigir, a instabilidade apontou três, deixou quatro passar
    e ainda acusou um acerto. Na reconstrução seguinte da base, marcou quatro
    produtos — todos classificados corretamente.

    Ou seja: é uma ordem de prioridade para revisar, não um detector de erro.
    Os testes abaixo verificam o mecanismo da fila, não a qualidade do sinal.
    """

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "aprendido.json")

    def tearDown(self):
        self.pasta.cleanup()

    def escrever(self, dados):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo)

    def test_fila_persiste_no_arquivo(self):
        self.escrever({"frases": {"colchao de solteiro": "movel"},
                       "revisar": ["colchao de solteiro"]})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(professor.para_revisar, ["colchao de solteiro"])

    def test_corrigir_tira_da_fila(self):
        """
        Corrigir É revisar. Deixar o produto na fila depois que alguém decidiu
        a categoria dele seria pedir o mesmo trabalho duas vezes.
        """
        self.escrever({"frases": {"colchao de solteiro": "acessorio"},
                       "revisar": ["colchao de solteiro"]})
        professor = Professor(self.caminho, consultar_modelo=False)
        professor.ensinar("Colchao de solteiro", "movel")
        self.assertEqual(professor.para_revisar, [])
        self.assertEqual(professor.categoria_de("Colchao de solteiro"), "movel")

    def test_marcar_revisado_sem_mudar_categoria(self):
        """Para quando a pessoa olha e conclui que já estava certo."""
        self.escrever({"frases": {"tapete de sala": "decoracao"},
                       "revisar": ["tapete de sala"]})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertTrue(professor.marcar_revisado("Tapete de sala"))
        self.assertEqual(professor.para_revisar, [])
        self.assertEqual(professor.categoria_de("Tapete de sala"), "decoracao")

    def test_marcar_revisado_de_quem_nao_esta_na_fila(self):
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertFalse(professor.marcar_revisado("Produto qualquer"))

    def test_arquivo_sem_a_secao_revisar(self):
        """Arquivos gerados antes desta seção existir precisam continuar válidos."""
        self.escrever({"frases": {"panela de pressao": "cozinha"}})
        professor = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(professor.para_revisar, [])
        self.assertEqual(professor.categoria_de("Panela de pressao"), "cozinha")


def modelo_disponivel():
    if not os.path.exists(BINARIO):
        return False
    try:
        # Com o gerenciador de contexto, a pasta é apagada mesmo se a consulta
        # falhar. A primeira versão usava mkdtemp() e deixava lixo em /tmp a
        # cada execução dos testes.
        with tempfile.TemporaryDirectory() as pasta:
            professor = Professor(os.path.join(pasta, "x.json"))
            return professor.categoria_de("Cafeteira eletrica italiana") is not None
    except Exception:
        return False


@unittest.skipUnless(modelo_disponivel(),
                     "modelo local indisponível (precisa de Mac com Apple "
                     "Intelligence ligado e da ponte Swift compilada)")
class TestModeloDeVerdade(unittest.TestCase):
    """
    Os únicos testes que chamam o modelo.

    São frouxos de propósito: não dá para exigir uma categoria exata de um
    modelo de linguagem, porque a Apple pode atualizá-lo em qualquer versão do
    sistema. Verificamos propriedades que precisam valer sempre.
    """

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "aprendido.json")
        self.professor = Professor(self.caminho)

    def tearDown(self):
        self.pasta.cleanup()

    def test_aprende_e_grava_em_disco(self):
        categoria = self.professor.categoria_de("Cafeteira eletrica italiana")
        self.assertIsNotNone(categoria)
        self.assertTrue(os.path.exists(self.caminho))

        # Um professor novo, lendo o mesmo arquivo, já sabe a resposta sem
        # precisar do modelo. É isso que torna o aprendizado portátil.
        outro = Professor(self.caminho, consultar_modelo=False)
        self.assertEqual(outro.categoria_de("Cafeteira eletrica italiana"), categoria)

    def test_a_segunda_consulta_nao_chama_o_modelo(self):
        self.professor.categoria_de("Guarda-chuva dobravel automatico")
        antes = self.professor.novidades
        self.professor.categoria_de("Guarda-chuva dobravel automatico")
        self.assertEqual(self.professor.novidades, antes)

    def test_recusa_texto_sem_produto(self):
        """
        O teste que justifica perguntar sobre a frase, não sobre a palavra.

        Perguntando palavra por palavra, o modelo classificava "xyzabc" como
        calçado. Com a frase inteira, ele responde que não reconhece produto
        nenhum.
        """
        self.assertIsNone(self.professor.categoria_de("xyzabc qwerty zzz"))

    def test_categoria_sempre_em_forma_canonica(self):
        """
        A propriedade que não pode falhar: a categoria vai virar chave de uma
        tabela hash, então precisa estar normalizada.
        """
        categoria = self.professor.categoria_de("Cafeteira eletrica italiana")
        self.assertEqual(categoria, categoria.lower())
        self.assertTrue(categoria.isascii())
        self.assertNotIn(" ", categoria)


if __name__ == "__main__":
    unittest.main()
