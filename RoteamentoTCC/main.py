"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

import util
import nsga.nsga2 as NSGA2

if __name__ == '__main__':

    print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
    print("Autor: Lucas Mateus Menezes Silva")
    print("Título: *Ainda a definir*\n")
    print("")

    # Arquivo OSM com os dados inicias
    '''nome_arquivo = "entrada/entrada.osm"

    # Leitura de arquivo e geração de arquivo sem tags desnecessárias
    # Invoca função para leitura do arquivo OSM
    util.le_arquivo(nome_arquivo)

    print("Arquivo {} lido com sucesso!".format(nome_arquivo))

    # Lê o arquivo que contém somente as tags interessantes e plota um mapa dos pontos e das ruas
    util.mapeia_ruas("saida/saida.osm")

    print("Mapeamento das ruas realizado com sucesso!")

    # Monta o grafo com base no mapa da cidade
    util.monta_grafo()'''

    # TESTES NSGA-II
    # Cria uma instância da classe do NSGA-II
    nsga = NSGA2.NSGA2(10, 5, 1, 10, 5, 0.9)

    nsga.run()
