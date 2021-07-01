# Arquivo com métodos úteis para a aplicação
# Biblioteca para leitura do arquivo OSM
import xml.etree.cElementTree as ET


def __init__(self, primeiro_vertice, ultimo_vertice):
    pass


# Cria a população com um determinado número de individuos
def inicia_populacao(self, tam_populacao):
    pass


# Cria um único indivíduo
def cria_individuo(self):
    pass


# Realiza a leitura do arquivo de entrada
def le_arquivo(arquivo_entrada: str):

    # Criando uma instância para leitura do XML que foi passado como parâmetro
    arvore = ET.parse(arquivo_entrada)
    raiz = arvore.getroot()

    remover = []

    # Percorre todos as ramificações da árvore XML
    for ramo in raiz:
        if ramo.tag == 'node':
            remover.append(ramo)

    for item in remover:
        raiz.remove(item)

    arvore.write('saida.osm')
