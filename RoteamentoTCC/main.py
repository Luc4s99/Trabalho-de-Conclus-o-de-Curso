"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

import RoteamentoTCC.util as util
import RoteamentoTCC.nsga.nsga2 as NSGA2

if __name__ == '__main__':

    print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
    print("Autor: Lucas Mateus Menezes Silva")
    print("Título: *Ainda a definir*\n")
    print("")

    # Arquivo OSM com os dados inicias
    nome_arquivo = "entrada/entrada.osm"

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
    util.k_means()

    # Algoritmo NSGA-II

    # Número de genes que cada cromossomo carrega
    # O máximo de genes que um indivíduo pode carregar está relacionado a quatidade de nós no grafo da cidade
    # Pois um indivíduo(caminhão) vai passar no máximo em todos os pontos de coleta, não contando o depósito
    #NUMERO_GENES = util.grafo_cidade.number_of_nodes() - 1

    # Número de geracoes que serão percorridas
    GERACOES = 10

    # Número total de indivíduos que compõe uma população
    TAMANHO_POPULACAO = 5

    # Menor valor que um gene pode assumir ao compor o genoma
    GENE_MINIMO = 1

    # Maior valor que um gene pode assumir ao compor o genoma
    # Esse label indica quantos pontos foram mapeados, então é gerado mais um e decrementado para se obter o total
    # de pontos
    # GENE_MAXIMO = util.Ponto.novo_label - 1

    # Capacidade média de carga de cada caminhão em quilos
    CAPACIDADE_CAMINHAO = 9000

    # Cria uma instância da classe do NSGA-II
    # nsga = NSGA2.NSGA2(NUMERO_GENES, GERACOES, TAMANHO_POPULACAO, GENE_MINIMO, GENE_MAXIMO, 5, 0.9, CAPACIDADE_CAMINHAO)

    # Roda o loop principal do NSGA2
    # nsga.run()
