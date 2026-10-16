// Classificador de produtos em categorias fechadas.
//
// Este programa substitui a primeira tentativa (ia/TagsIA.swift, que pedia
// tags em texto livre). A diferença e a lição do projeto estão em duas
// escolhas:
//
// 1. A resposta é um ENUM, não uma string.
//    Pedindo texto livre, o modelo devolvia "calcado" para um produto e
//    "calcados" para outro. Para uma tabela hash isso são duas chaves sem
//    relação nenhuma, e metade dos calçados sumia da busca. Declarando a
//    resposta como um conjunto fechado de valores, o modelo fica
//    estruturalmente incapaz de inventar uma variação: a geração guiada do
//    framework só permite escolher entre os casos que existem.
//
//    Isso resolveu o problema sem treinar nada. Medimos: seis calçados
//    diferentes, seis vezes a mesma categoria.
//
// 2. A pergunta é sobre o PRODUTO INTEIRO, não sobre cada palavra.
//    A primeira versão perguntava palavra por palavra, e o resultado foi
//    desastroso: "dobravel" foi classificado como calçado, "automatico" como
//    eletrônico, e "xyzabc" — uma palavra que não existe — também como
//    calçado. O modelo quase nunca usava a opção "não é um produto".
//
//    Perguntando sobre a frase completa, ele tem contexto e acerta. É a
//    diferença entre "o que é 'dobravel'?", que não tem resposta, e "que tipo
//    de produto é um guarda-chuva dobrável automático?", que tem.
//
// Protocolo:
//   entrada : uma linha por produto, em stdin
//   saída   : uma linha JSON por produto
//             {"categoria": "acessorio"}  ou  {"erro": "descrição"}
//
// Compilar com:
//   swiftc -O ia/ClassificaProduto.swift -o ia/classifica-produto

import Foundation
import FoundationModels

// O conjunto fechado de respostas possíveis.
//
// Estes valores precisam existir também como tags no vocabulário local
// (catalogo/vocabulario.py). Os dois lados têm que concordar, senão o
// catálogo teria tags que só aparecem quando o modelo está disponível, e a
// busca daria resultados diferentes em máquinas diferentes.
@Generable
enum Categoria: String {
    case calcado, vestuario, acessorio
    case eletronico, informatica, audio
    case movel, cozinha, decoracao
    case esporte, brinquedo, livro
    case beleza, ferramenta, automotivo
    case papelaria, pet, alimento
    case desconhecida
}

@Generable
struct Resposta {
    @Guide(description: """
        A categoria do produto descrito. \
        Use desconhecida somente se o texto não descrever nenhum produto \
        reconhecível.
        """)
    let categoria: Categoria
}

// Temperatura zero: o modelo escolhe sempre a opção mais provável, em vez de
// sortear entre as prováveis. Sem isso, o mesmo produto recebia categorias
// diferentes em execuções diferentes, e o catálogo ficaria dependendo de sorte.
let opcoes = GenerationOptions(temperature: 0.0)
let instrucoes = "Você classifica produtos de e-commerce em uma categoria."

// Quantas vezes perguntar a mesma coisa, com --amostras N.
//
// Temperatura zero esconde uma informação útil. Ela faz o modelo responder
// sempre igual, mas não diz NADA sobre o quanto ele estava seguro: uma
// classificação óbvia e um chute entre duas opções parecidas saem com a mesma
// cara de certeza.
//
// Perguntando várias vezes com temperatura alta, isso aparece. Se as respostas
// concordam mesmo quando o modelo tem liberdade para variar, a classificação é
// firme. Se elas se espalham, ele estava em cima do muro — e é justamente aí
// que vale alguém olhar antes de gravar como verdade.
//
// É uma medida indireta de confiança. O framework não expõe as probabilidades
// internas do modelo, então a estabilidade da resposta é o que dá para medir
// de fora.
let amostras: Int = {
    let args = CommandLine.arguments
    guard let i = args.firstIndex(of: "--amostras"),
          i + 1 < args.count,
          let n = Int(args[i + 1]), n > 0 else { return 1 }
    return min(n, 9)
}()

let opcoesAmostragem = GenerationOptions(temperature: 1.0)

func emitir(_ objeto: [String: Any]) {
    if let dados = try? JSONSerialization.data(withJSONObject: objeto),
       let linha = String(data: dados, encoding: .utf8) {
        print(linha)
    } else {
        print("{\"erro\": \"falha ao serializar resposta\"}")
    }
    // Sem isto, a saída fica presa no buffer quando o programa escreve para um
    // cano em vez de para o terminal, e o Python do outro lado espera para
    // sempre uma linha que nunca chega.
    fflush(stdout)
}

switch SystemLanguageModel.default.availability {
case .available:
    break
case .unavailable(let motivo):
    let explicacao: String
    switch motivo {
    case .deviceNotEligible:
        explicacao = "este aparelho não é compatível com Apple Intelligence"
    case .appleIntelligenceNotEnabled:
        explicacao = "Apple Intelligence está desligado nos Ajustes do sistema"
    case .modelNotReady:
        explicacao = "o modelo ainda está sendo baixado; tente de novo em alguns minutos"
    @unknown default:
        explicacao = "o modelo não está disponível"
    }
    emitir(["erro": explicacao])
    exit(2)
@unknown default:
    emitir(["erro": "não foi possível determinar a disponibilidade do modelo"])
    exit(2)
}

// Uma sessão por produto. Reaproveitar a mesma faz o histórico da conversa
// crescer até estourar a janela de contexto — vimos o erro "4091 de 4096
// tokens" em um texto de dez palavras, por acúmulo. Sessão nova também garante
// que um produto não influencie a classificação do seguinte.
while let linha = readLine(strippingNewline: true) {
    let texto = linha.trimmingCharacters(in: .whitespacesAndNewlines)
    if texto.isEmpty {
        emitir(["categoria": Categoria.desconhecida.rawValue])
        continue
    }
    do {
        // A resposta oficial continua vindo de temperatura zero, para o
        // catálogo seguir determinístico. As amostras servem só para medir a
        // firmeza dela, e não substituem o resultado.
        let sessao = LanguageModelSession(instructions: instrucoes)
        let resposta = try await sessao.respond(to: texto,
                                                generating: Resposta.self,
                                                options: opcoes)
        let categoria = resposta.content.categoria.rawValue

        if amostras <= 1 {
            emitir(["categoria": categoria])
            continue
        }

        var vistas: [String] = []
        for _ in 1...amostras {
            let s = LanguageModelSession(instructions: instrucoes)
            if let r = try? await s.respond(to: texto,
                                            generating: Resposta.self,
                                            options: opcoesAmostragem) {
                vistas.append(r.content.categoria.rawValue)
            }
        }
        emitir(["categoria": categoria, "amostras": vistas])
    } catch {
        emitir(["erro": "\(error)"])
    }
}
