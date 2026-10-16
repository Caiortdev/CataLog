"""O produto em si. É só um agrupamento de dados, sem lógica."""


class Produto:
    """
    Guarda o que um item do catálogo tem: identificador, nome, descrição e as
    tags geradas a partir do texto.

    Não é uma dataclass de propósito. O __init__ escrito à mão deixa explícito
    o que cada campo é, e em uma disciplina de estrutura de dados é melhor que
    nada apareça por mágica do decorador.

    O produto não sabe gerar as próprias tags, e isso é intencional. Quem gera
    é o GeradorDeTags, quem guarda é o Catalogo. Se o produto fizesse as três
    coisas, trocar a estratégia de tags obrigaria a mexer na classe de dados.
    """

    def __init__(self, identificador, nome, descricao, tags):
        self.identificador = identificador
        self.nome = nome
        self.descricao = descricao
        self.tags = tags

    def __repr__(self):
        return f"Produto({self.identificador}, {self.nome!r})"

    def resumo(self):
        """Uma linha legível, usada pelo menu do terminal."""
        tags = ", ".join(self.tags) if self.tags else "sem tags"
        return f"[{self.identificador}] {self.nome} — {tags}"
