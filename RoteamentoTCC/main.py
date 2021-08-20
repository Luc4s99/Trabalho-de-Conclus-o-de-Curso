"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

import util

if __name__ == '__main__':

    while True:
        print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
        print("Autor: Lucas Mateus Menezes Silva")
        print("Título: *Ainda a definir*\n")
        print("")

        print("1 - Inicializar")
        print("2 - Realizar plot no Google Maps")
        print("0 - Sair")

        opcao = int(input("=> "))

        # Opção para leitura de arquivo e geração de arquivo sem tags desnecessárias
        if opcao == 1:

            # Obtendo o arquivo de entrada
            arquivo_entrada = input("Informe o caminho do arquivo de entrada(.osm): ")

            # Verifica se o arquivo possui a extensão necessária
            if arquivo_entrada.endswith(".osm"):

                # Invoca função para leitura do arquivo OSM
                util.le_arquivo(arquivo_entrada)
            else:

                print("O arquivo precisa ser do tipo .osm!")

        # Opção para gerar plot do mapa obtido no google maps
        elif opcao == 2:
            util.plot_maps()

        else:
            print("Aplicação finalizada!")
            break
