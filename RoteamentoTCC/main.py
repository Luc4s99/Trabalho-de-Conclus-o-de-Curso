"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

import RoteamentoTCC.util as util

if __name__ == '__main__':

    # Capacidade de lixo que um caminhão de lixo possuiem KG
    CAPACIDADE_CAMINHAO = 10000

    print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
    print("Autor: Lucas Mateus Menezes Silva")
    print("Título: *Ainda a definir*\n")
    print("")

    # Arquivo OSM com os dados inicias
    nome_arquivo = "entrada/teste2.osm"

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

    # Monta um grafo otimizado, que contém apenas pontos de maior interesse
    util.monta_grafo_otimizado(util.pontos_otimizados, "saida/GrafoCidadeOtimizado.png")

    print("Grafo otimizado da cidade gerado com sucesso!")

    # Gera as demandas aproximadas das ruas
    util.calcula_demandas("saida/GrafoCidadeDemandas.png")

    print("Demandas de lixo aproximadas das ruas calculadas!")

    # Realiza o agrupamento dos pontos por meio do k-means
    pontos_agrupados = util.k_means(CAPACIDADE_CAMINHAO)

    print("Agrupamentos gerados com sucesso!")

    print("Processando rotas...")
    # Após organizados e realizados os agrupamentos, é feito o processamento das rotas em cada um deles
    util.processamento_rotas(pontos_agrupados, CAPACIDADE_CAMINHAO)
