# Arquivo com métodos úteis para a aplicação
from ponto import Ponto


def __init__(self, primeiro_vertice, ultimo_vertice):

    # Representação da população
    self.populacao = list()

    # Número do primeiro vértice do grafo que representa o caminho
    self.primeiro_vertice = primeiro_vertice

    # Número do último vértice do grafo que representa o caminho
    self.ultimo_vertice = ultimo_vertice


# Cria a população com um determinado número de individuos
def inicia_populacao(self, tam_populacao):

    # For que cria o numero de individuos passado para a populacao
    for _ in range(tam_populacao):

        pass


# Cria um único indivíduo
def cria_individuo(self):
    pass


# Realiza a leitura do arquivo de entrada
def le_arquivo(arquivo_entrada: str):

    # Abertura do arquivo para leitura
    arquivo = open(arquivo_entrada, "r")
    # Lê a primeira linha do arquivo
    linha = arquivo.readline().strip()
    # Instancia um novo ponto, para ser adicionado a lista de pontos
    ponto = Ponto()
    # Lista com as linhas necessárias para a montagem da matriz de distâncias
    pontos = list()

    # Laço para ler todas as linhas do arquivo, enquanto possuir algo na linha o laço continua
    while linha:

        # Identifica um ponto de interesse no arquivo
        if linha.__contains__("<Placemark"):

            # A próxima linha do arquivo contém o nome do ponto
            linha = arquivo.readline().strip()

            # Formata a linha para recuperar o nome do ponto
            linha = linha.replace("<name>", "")
            linha = linha.replace("</name>", "")
            # Atribui nome ao ponto
            ponto.nome = linha

        elif linha.__contains__("<coordinates>"):

            linha = linha.replace("<coordinates>", "")
            linha = linha.replace("</coordinates>", "")

            # Separa as coordenadas pela ,
            linha = linha.split(",")

            # Atribui as coordenadas ao ponto
            ponto.coord_x = linha[0]
            ponto.coord_y = linha[1]

            # Insere o novo ponto na lista de pontos
            pontos.append(ponto)

            # Reinicia o ponto
            ponto = Ponto()

        linha = arquivo.readline().strip()

    # Fechando o arquivo de entrada
    arquivo.close()
