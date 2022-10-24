"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

import RoteamentoTCC.util as util
from datetime import datetime
import cProfile


def main():

    # Leitura de arquivo e geração de arquivo sem tags desnecessárias
    # Invoca função para leitura do arquivo OSM
    util.le_arquivo(nome_arquivo)

    print("Arquivo {} lido com sucesso!".format(nome_arquivo))

    # Lê o arquivo que contém somente as tags interessantes e plota um mapa dos pontos e das ruas
    util.mapeia_ruas("saida/saida.osm")

    print("Mapeamento das ruas realizado com sucesso!")

    # Monta o grafo com base no mapa da cidade
    util.monta_grafo("saida/GrafoCidade.png")

    print("Grafo da cidade gerado com sucesso!")

    # Monta o dicionário com os pontos otimizados
    util.otimiza_grafo()

    # Adiciona as altitudes dos pontos
    util.adiciona_alturas()

    # Monta um grafo otimizado, que contém apenas pontos de maior interesse
    util.monta_grafo_otimizado(util.pontos_otimizados, "saida/GrafoCidadeOtimizado.png")

    print("Grafo otimizado da cidade gerado com sucesso!")

    # Gera as demandas aproximadas das ruas
    util.calcula_demandas("saida/GrafoCidadeDemandas.png")

    print("Demandas de lixo aproximadas das ruas calculadas!")

    print("Processando rotas...")

    melhor_front = util.processamento_rotas()

    for ind in melhor_front.individuals:
        print(ind.genome)


if __name__ == '__main__':

    print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
    print("Autor: Lucas Mateus Menezes Silva")
    print("Título: A utilização de heurísticas na otimização das rotas de coleta de lixo na cidade de Formiga/MG\n")
    print("")

    agora = datetime.now()
    print("Início: ", agora.strftime("%H:%M:%S"))

    # Arquivo OSM com os dados inicias
    # nome_arquivo = "entrada/entrada_pequena.osm"
    nome_arquivo = "entrada/entrada_grande.osm"

    # cProfile.run('main()', filename='saida/profiling.cprof')
    main()

    agora = datetime.now()
    print("Fim: ", agora.strftime("%H:%M:%S"))
