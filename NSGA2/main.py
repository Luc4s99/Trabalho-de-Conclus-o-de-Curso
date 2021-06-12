import util

if __name__ == '__main__':

    while True:
        print("***** TRABALHO DE CONCLUSÃO DE CURSO *****")
        print("Autor: Lucas Mateus Menezes Silva")
        print("Título: *Ainda a definir*\n")

        print("1 - Inserir arquivo de entrada")
        print("0 - Sair")

        opcao = int(input("=> "))

        if opcao == 1:

            # Obtendo o arquivo de entrada
            arquivo_entrada = input("Informe o caminho do arquivo de entrada(.kml): ")

            # Verifica se o arquivo possui a extensão necessária
            if arquivo_entrada.endswith(".kml"):

                # Invoca função para leitura do arquivo KML
                util.le_arquivo(arquivo_entrada)
            else:

                print("O arquivo precisa ser do tipo .kml!")
        else:
            print("Aplicação finalizada!")
            break
