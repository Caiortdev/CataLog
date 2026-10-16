"""
O professor do vocabulário.

A ideia deste módulo veio de uma pergunta: já que existe um modelo de
linguagem rodando na máquina, por que não usá-lo no lugar do vocabulário
escrito à mão?

A resposta curta é que medimos e não funcionou — mas o caminho até essa
resposta mudou o projeto para melhor. A história completa está no documento 6;
o resumo do que sobrou é este arquivo.

O desenho final divide o trabalho entre quem faz bem cada parte:

  - o vocabulário manda, porque é rápido e nunca varia;
  - uma regra determinística escolhe a palavra que nomeia o produto;
  - o modelo diz a categoria, que é a única coisa que ele faz melhor que uma
    regra;
  - tudo vai para um arquivo, e o arquivo é que viaja junto com o projeto.

Essa divisão não é arbitrária, é medida. Pedindo ao modelo que apontasse a
palavra principal do produto, ele devolveu a frase inteira em sete de oito
casos, mesmo instruído a copiar uma palavra só. A regra "primeira palavra
significativa do nome" acertou dezesseis de dezesseis. Em português, nome de
produto começa pelo substantivo: *Frigideira* antiaderente, *Esteira*
ergométrica, *Trena* a laser.
"""

import json
import os
import subprocess

from catalogo.hashtable import TabelaHash
from catalogo.texto import normalizar, tokenizar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE_SWIFT = os.path.join(RAIZ, "ia", "ClassificaProduto.swift")
BINARIO = os.path.join(RAIZ, "ia", "classifica-produto")
CACHE = os.path.join(RAIZ, "dados", "aprendido.json")

# Categoria que o modelo devolve quando não reconhece produto nenhum no texto.
# Nunca vira tag: seria uma tag que não ajuda ninguém a achar nada.
DESCONHECIDA = "desconhecida"

# As categorias que o modelo pode devolver — o mesmo conjunto declarado como
# enum em ia/ClassificaProduto.swift.
#
# Ter a lista nos dois lugares é um risco conhecido: se alguém acrescentar uma
# categoria no Swift e esquecer daqui, o Python passaria a tratá-la como se não
# fosse categoria. Por isso existe o teste
# `test_categorias_batem_com_o_enum_do_swift`, que lê o arquivo Swift e compara
# os dois lados.
#
# Esta lista responde a uma pergunta específica: "já sabemos QUE COISA este
# produto é?". Tags como "azul" ou "material" descrevem o produto, mas não
# dizem o que ele é; só as categorias fazem isso.
CATEGORIAS = {
    "calcado", "vestuario", "acessorio",
    "eletronico", "informatica", "audio",
    "movel", "cozinha", "decoracao",
    "esporte", "brinquedo", "livro",
    "beleza", "ferramenta", "automotivo",
    "papelaria", "pet", "alimento",
}

TEMPO_LIMITE = 60


def palavra_principal(texto):
    """
    A palavra que nomeia o produto, pela regra da primeira palavra significativa.

    Funciona porque o texto que chega é "nome + descrição" e, em português,
    nome de produto começa pelo substantivo. As palavras de ligação já foram
    removidas pelo tokenizador, então "Jogo de facas" dá "jogo", não "de".

    A regra erra em nomes compostos: "Guarda-chuva" vira "guarda" e
    "Micro-ondas" vira "micro". Isso é menos grave do que parece, porque a
    palavra truncada continua servindo de chave — qualquer guarda-chuva cai na
    mesma entrada. E quando o truncamento junta coisas diferentes, como
    "guarda-chuva" e "guarda-roupa", a detecção de ambiguidade abaixo resolve.
    """
    palavras = tokenizar(texto)
    return palavras[0] if palavras else None


class Professor:
    """
    Guarda o que o modelo ensinou, em três estruturas com papéis diferentes.

    `palavras` é o que torna o aprendizado útil: "frigideira" -> "cozinha"
    vale para qualquer frigideira, não só para a que foi cadastrada. Sem isso,
    cada produto novo custaria uma consulta ao modelo, mesmo sendo quase igual
    a outro já visto.

    `frases` guarda o texto completo. Serve de resposta exata, que tem
    precedência sobre a palavra, e é o único recurso quando a palavra não pode
    ser usada.

    `ambiguas` é a defesa contra o caso que estraga tudo. "Jogo de chaves de
    fenda" é ferramenta e "jogo de facas de cozinha" é cozinha; generalizar
    "jogo" para qualquer uma das duas faria o outro produto ser classificado
    errado. Quando a mesma palavra aparece com duas categorias, ela é marcada
    aqui e deixa de generalizar — aqueles produtos voltam a depender da frase
    inteira.

    As três são tabelas hash, pela razão de sempre: a consulta acontece antes
    de toda chamada ao modelo e não pode custar mais que a chamada que está
    tentando evitar.
    """

    def __init__(self, caminho_cache=CACHE, consultar_modelo=True, amostras=1):
        self._palavras = TabelaHash()
        self._frases = TabelaHash()
        self._ambiguas = TabelaHash()
        self._caminho_cache = caminho_cache
        self._consultar_modelo = consultar_modelo
        # Quantas vezes perguntar a mesma coisa ao modelo para medir se ele
        # está seguro. Vale 1 no uso normal, porque custa tempo e não muda a
        # resposta; quem monta a base usa mais, para marcar os instáveis.
        self._amostras = max(1, int(amostras))
        self._revisar = TabelaHash()
        self._avisos = []
        self._novidades = 0
        self._modelo_falhou = False
        self._carregar_cache()

    # ------------------------------------------------------------------
    # Arquivo
    # ------------------------------------------------------------------

    def _carregar_cache(self):
        if not os.path.exists(self._caminho_cache):
            return
        try:
            with open(self._caminho_cache, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (OSError, ValueError) as erro:
            self._avisos.append(f"não foi possível ler o aprendizado: {erro}")
            return

        # O formato antigo era um mapa simples de frase para categoria. Ele é
        # reconhecido e convertido, em vez de descartado: jogar fora o que já
        # foi aprendido só porque o formato mudou obrigaria a consultar o
        # modelo de novo para tudo.
        if dados and all(isinstance(v, str) for v in dados.values()):
            for frase, categoria in dados.items():
                self._registrar(frase, categoria, contar=False)
            return

        # As chaves são renormalizadas na leitura, em vez de usadas como estão.
        #
        # Isso existe porque a normalização mudou uma vez: "Guarda-chuva"
        # produzia "guarda chuva" e passou a produzir "guardachuva". Sem
        # renormalizar, as entradas gravadas com a regra antiga ficariam
        # órfãs — continuariam no arquivo, mas nenhuma busca as encontraria, e
        # o modelo seria consultado de novo sobre produtos já conhecidos.
        #
        # Com isto, qualquer ajuste futuro na normalização migra o arquivo
        # sozinho, na primeira vez que ele for aberto.
        # Só as frases são lidas. As seções "palavras" e "ambiguas" do arquivo
        # existem para quem abre o JSON entender o que o sistema aprendeu, mas
        # são derivadas das frases — e derivadas é como elas voltam a ser aqui.
        #
        # Ler as três do arquivo abriria espaço para o estado divergir: bastaria
        # alguém corrigir uma frase à mão e esquecer de ajustar a palavra
        # correspondente, e o programa passaria a usar uma generalização que
        # nenhum produto sustenta.
        for frase, categoria in dados.get("frases", {}).items():
            chave = normalizar(frase).strip()
            if chave:
                self._frases.inserir(chave, categoria)

        for frase in dados.get("revisar", []):
            chave = normalizar(frase).strip()
            if chave:
                self._revisar.inserir(chave, True)

        self._reconstruir_palavras(avisar=False)

    def salvar(self):
        """
        Grava o aprendizado.

        As três seções são ordenadas por chave de propósito. Não é estética:
        ordem estável produz diferenças pequenas e legíveis quando o arquivo
        muda, em vez de embaralhar tudo a cada gravação.
        """
        if self._novidades == 0:
            return
        dados = {
            "palavras": {c: v for c, v in sorted(self._palavras.itens())},
            "frases": {c: v for c, v in sorted(self._frases.itens())},
            "ambiguas": sorted(self._ambiguas.chaves()),
            "revisar": sorted(self._revisar.chaves()),
        }
        try:
            os.makedirs(os.path.dirname(self._caminho_cache), exist_ok=True)
            with open(self._caminho_cache, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
                arquivo.write("\n")
        except OSError as erro:
            self._avisos.append(f"não foi possível gravar o aprendizado: {erro}")

    # ------------------------------------------------------------------
    # Consulta
    # ------------------------------------------------------------------

    def categoria_de(self, texto, usar_generalizacao=True):
        """
        A categoria do produto, ou None se não houver resposta útil.

        A ordem das tentativas é o coração do desenho, e vai do mais específico
        ao mais caro:

          1. a frase exata, se já foi vista antes;
          2. a palavra que nomeia o produto, se ela não for ambígua;
          3. o modelo, que é a única etapa que custa tempo de verdade.

        A frase vem antes da palavra porque é mais específica: se alguém
        corrigiu à mão a categoria de um produto, essa correção precisa valer
        mesmo que a palavra genérica diga outra coisa.

        Sobre `usar_generalizacao`: desligá-lo pula a etapa 2 e vai direto ao
        modelo quando a frase é nova. Isso parece um desperdício, e no uso
        normal seria — mas ele conserta um problema que descobrimos montando a
        base de aprendizado.

        O atalho da palavra responde antes de o modelo ser consultado, e isso
        impede o sistema de descobrir que o atalho está errado. Foi o que
        aconteceu com "jogo": o jogo de facas foi aprendido primeiro e ensinou
        que "jogo" é cozinha; quando o jogo de chaves de fenda chegou, a
        generalização respondeu "cozinha" sem perguntar nada, a frase nunca foi
        gravada, e a ambiguidade entre os dois nunca apareceu. Todo jogo
        passou a ser cozinha, inclusive os de tabuleiro.

        É um caso em que a otimização cega a detecção do próprio erro. Por isso
        quem constrói a base de aprendizado desliga o atalho: ali o objetivo
        não é responder rápido, é ouvir o modelo sobre cada produto para que os
        conflitos tenham chance de aparecer.
        """
        frase = normalizar(texto).strip()
        if not frase:
            return None

        lembrada = self._frases.buscar(frase)
        if lembrada is not None:
            return self._como_tag(lembrada)

        if usar_generalizacao:
            palavra = palavra_principal(texto)
            if palavra and palavra not in self._ambiguas:
                por_palavra = self._palavras.buscar(palavra)
                if por_palavra is not None:
                    return self._como_tag(por_palavra)

        if not self._consultar_modelo or self._modelo_falhou:
            return None

        categoria = self._perguntar_ao_modelo(frase)
        if categoria is None:
            return None

        # Gravamos inclusive a resposta "desconhecida". Lembrar que o modelo
        # não soube é tão útil quanto lembrar que ele soube: evita perguntar de
        # novo, toda vez, sobre o mesmo produto.
        self._registrar(texto, categoria)
        self.salvar()
        return self._como_tag(categoria)

    @staticmethod
    def _como_tag(categoria):
        return None if categoria == DESCONHECIDA else categoria

    # ------------------------------------------------------------------
    # Registro e detecção de ambiguidade
    # ------------------------------------------------------------------

    def _registrar(self, texto, categoria, contar=True):
        """
        Guarda a categoria e tenta generalizá-la para a palavra do produto.

        A generalização é o que faz o aprendizado valer a pena, mas ela só
        acontece quando é segura. Três situações impedem:

        A categoria é "desconhecida". Generalizar que uma palavra não significa
        nada seria arriscado — o texto é que podia estar ruim, não a palavra.

        A palavra já foi marcada como ambígua antes.

        A palavra já tem outra categoria. Aí descobrimos o conflito agora:
        ela é removida das generalizações e marcada como ambígua. Os dois
        produtos continuam corretos, porque suas frases completas ficaram
        guardadas.
        """
        frase = normalizar(texto).strip()
        if not frase:
            return

        self._frases.inserir(frase, categoria)
        if contar:
            self._novidades += 1

        self._reconstruir_palavras()

    def _reconstruir_palavras(self, avisar=True):
        """
        Recalcula todas as generalizações a partir das frases guardadas.

        A primeira versão atualizava as palavras de forma incremental, a cada
        produto novo, e tinha um defeito que só apareceu olhando o resultado:
        as sete categorias corrigidas à mão foram todas marcadas como
        ambíguas. O modelo tinha dito que "cafeteira" era eletrônico; a
        correção disse cozinha; e o código leu isso como "a palavra aparece com
        duas categorias" em vez de "alguém consertou esta frase".

        A distinção que faltava é esta: a mesma frase mudando de categoria é
        uma correção, e deve substituir; frases diferentes com a mesma palavra
        e categorias distintas é ambiguidade de verdade, e deve descartar.

        Dava para remendar a lógica incremental com um caso especial, mas a
        causa raiz era ela acumular estado em vez de derivá-lo. Recalcular do
        zero custa O(n) sobre algumas dezenas de entradas — irrelevante — e em
        troca o resultado passa a depender só do conteúdo atual das frases,
        nunca da ordem em que elas foram aprendidas ou corrigidas.
        """
        categorias_por_palavra = TabelaHash()

        for frase, categoria in self._frases.itens():
            if categoria == DESCONHECIDA:
                # Se o modelo não reconheceu o produto, a culpa pode ser do
                # texto e não da palavra. Marcar a palavra como "não significa
                # nada" seria exagerado.
                continue
            palavra = palavra_principal(frase)
            if not palavra:
                continue
            vistas = categorias_por_palavra.buscar(palavra)
            if vistas is None:
                categorias_por_palavra.inserir(palavra, [categoria])
            elif categoria not in vistas:
                vistas.append(categoria)

        self._palavras = TabelaHash()
        self._ambiguas = TabelaHash()

        for palavra, categorias in categorias_por_palavra.itens():
            if len(categorias) == 1:
                self._palavras.inserir(palavra, categorias[0])
            else:
                self._ambiguas.inserir(palavra, True)
                # Na leitura do arquivo o aviso é omitido: as ambiguidades já
                # conhecidas não são novidade, e repeti-las a cada abertura do
                # programa afogaria os avisos que de fato importam.
                if avisar:
                    aviso = (
                        f"a palavra {palavra!r} aparece como "
                        + " e como ".join(repr(c) for c in sorted(categorias))
                        + "; não serve para generalizar"
                    )
                    # A reconstrução roda a cada produto aprendido, então o
                    # mesmo aviso sairia repetido uma vez por produto. Avisar
                    # seis vezes da mesma ambiguidade não informa mais que
                    # avisar uma.
                    if aviso not in self._avisos:
                        self._avisos.append(aviso)

    def ensinar(self, texto, categoria):
        """
        Grava uma categoria direto, sem perguntar ao modelo.

        É assim que uma pessoa corrige o que o modelo errou. O aprendizado
        deste projeto é um arquivo de texto legível, não um conjunto de pesos,
        e essa diferença é prática: dá para revisar linha por linha e consertar
        um caso específico sem mexer em nenhum outro.

        Devolve True se algo mudou, para quem chama poder relatar.
        """
        frase = normalizar(texto).strip()
        if not frase or self._frases.buscar(frase) == categoria:
            return False
        self._registrar(texto, categoria)
        # Corrigir é a própria revisão: não faz sentido o produto continuar na
        # fila de "alguém precisa olhar isto" depois que alguém olhou.
        chave_revisao = normalizar(texto).strip()
        if chave_revisao in self._revisar:
            self._revisar.remover(chave_revisao)
        self.salvar()
        return True

    # ------------------------------------------------------------------
    # Modelo
    # ------------------------------------------------------------------

    def _perguntar_ao_modelo(self, texto):
        if not os.path.exists(BINARIO) and not self._compilar():
            return None

        comando = [BINARIO]
        if self._amostras > 1:
            comando += ["--amostras", str(self._amostras)]

        try:
            resultado = subprocess.run(
                comando, input=texto + "\n", capture_output=True,
                text=True, encoding="utf-8", timeout=TEMPO_LIMITE * self._amostras,
            )
        except (OSError, subprocess.TimeoutExpired) as erro:
            self._desistir(f"o modelo não respondeu: {erro}")
            return None

        linhas = resultado.stdout.strip().splitlines()
        if not linhas:
            self._desistir(resultado.stderr.strip()[:200] or "o modelo não respondeu")
            return None

        try:
            dados = json.loads(linhas[0])
        except ValueError:
            self._desistir("o modelo devolveu algo que não é JSON")
            return None

        if "erro" in dados:
            self._desistir(dados["erro"])
            return None

        # Quando pedimos várias amostras, a divergência entre elas é o sinal de
        # que o modelo não estava seguro. Ele não é um sinal forte: medindo
        # contra sete classificações que uma pessoa teve de corrigir, a
        # instabilidade apontou três, deixou quatro passar e ainda acusou um
        # acerto. Serve para priorizar o que revisar primeiro, não para decidir
        # o que é certo.
        amostras = dados.get("amostras") or []
        if len(set(amostras)) > 1:
            chave = normalizar(texto).strip()
            if chave:
                self._revisar.inserir(chave, True)
                self._avisos.append(
                    f"classificação instável para {texto!r}: o modelo respondeu "
                    + ", ".join(sorted(set(amostras)))
                    + " — vale revisar"
                )

        return dados.get("categoria")

    def _desistir(self, motivo):
        """
        Registra a falha e para de tentar pelo resto da execução.

        Sem isso, um modelo desligado faria cada produto esperar o tempo limite
        inteiro antes de desistir, e cadastrar dez produtos levaria minutos
        para no fim não aprender nada.
        """
        self._avisos.append(motivo)
        self._modelo_falhou = True

    def _compilar(self):
        if not os.path.exists(FONTE_SWIFT):
            self._desistir(f"fonte Swift não encontrada em {FONTE_SWIFT}")
            return False
        try:
            resultado = subprocess.run(
                ["swiftc", "-O", FONTE_SWIFT, "-o", BINARIO],
                capture_output=True, text=True, timeout=300,
            )
        except (OSError, subprocess.TimeoutExpired) as erro:
            self._desistir(f"não foi possível compilar a ponte Swift: {erro}")
            return False
        if resultado.returncode != 0:
            self._desistir(f"a ponte Swift não compilou: {resultado.stderr.strip()[:300]}")
            return False
        return True

    # ------------------------------------------------------------------
    # Informação para quem usa
    # ------------------------------------------------------------------

    @property
    def avisos(self):
        return list(self._avisos)

    @property
    def modelo_falhou(self):
        """
        Se o modelo parou de responder nesta execução.

        É diferente de "há avisos". Nem todo aviso é falha: descobrir que uma
        palavra é ambígua também gera aviso, e isso é o sistema funcionando,
        não quebrando. Confundir os dois custou caro uma vez — o script que
        monta a base tratava qualquer aviso como falha fatal e parava o lote na
        primeira ambiguidade encontrada, deixando metade dos produtos de fora.
        """
        return self._modelo_falhou

    @property
    def aprendidos(self):
        """Quantos produtos distintos já foram vistos."""
        return len(self._frases)

    @property
    def palavras_aprendidas(self):
        """Quantas palavras generalizam para qualquer produto que as use."""
        return len(self._palavras)

    @property
    def ambiguas(self):
        return sorted(self._ambiguas.chaves())

    @property
    def para_revisar(self):
        """
        Produtos cuja classificação o modelo deu de forma instável.

        É uma fila de trabalho humano, não uma lista de erros. Alguns destes
        estão certos; e vários dos erros reais não estão aqui, porque o modelo
        errou com convicção. A lista diz onde olhar primeiro, só isso.
        """
        return sorted(self._revisar.chaves())

    def marcar_revisado(self, texto):
        """Tira um produto da fila, depois que alguém olhou."""
        chave = normalizar(texto).strip()
        if chave in self._revisar:
            self._revisar.remover(chave)
            self._novidades += 1
            self.salvar()
            return True
        return False

    @property
    def novidades(self):
        return self._novidades
