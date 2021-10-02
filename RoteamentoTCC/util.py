"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Saulo Ricardo
Link do GitHub: https://github.com/SauloRicardo/TCC_Final

"""

# Arquivo com métodos úteis para a aplicação
# Biblioteca para leitura do arquivo OSM
import xml.etree.cElementTree as ET
# Biblioteca para plotagem de dados no google maps
import gmplot
# Classe que define um ponto no mapa
from Ponto import *
# Classe que define uma rua no mapa
from Rua import *
# Biblioteca que realiza operações com grafos
import networkx as nx
# Biblioteca para cálculos utilizando coordenadas geográficas
import geopy.distance
# Biblioteca para plotagem de gráficos e dados em geral
from matplotlib import pyplot as plt

# TESTE
plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

# Armazena em um dicionario os pontos que foram mapeados na leitura do arquivo
pontos = {}

# Armazena em um dicionario as ruas que foram mapeadas na leitura do arquivo
ruas = {}

# Grafo que será utilizado para representar o mapa da cidade
grafo_cidade = nx.Graph()


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
    # Obtém a tag raiz do arquivo
    raiz = arvore.getroot()
    # Referencias de nós de caminhos para serem removidos
    referencias_nos = []

    # Lista de itens que serão removidos, esses itens não são interessantes para o trabalho
    # Ex: Rios, ferrovias, montanhas, morros, sinais de trânsito, estabelecimentos
    remover = ['traffic_signals', 'place_of_worship', 'church', 'supermarket', 'educational_institution', 'school',
               'hospital', 'atm', 'bakery', 'bank', 'pharmacy', 'bus_station', 'hotel', 'convenience', 'taxi',
               'restaurant', 'library', 'police', 'furniture', 'sports_centre', 'tower', 'fast_food', 'peak', 'river',
               'rail', 'wood', 'statue', 'clothes', 'fuel', 'gate', 'cattle_grid', 'track', 'path', 'water', 'unpaved']

    # Armazena as tags que serão retiradas
    limpar = []

    # Percorre todos as tags filhas da tag raiz
    for ramo in raiz:

        # Se a tag do ramo for um nó, possui informações a serem tratadas
        if ramo.tag == 'node':

            # Variável que indica se aquele nó foi removido
            isremovida = False

            # Percorre todas as tags filhas da tag ramo
            for filha_ramo in ramo:

                # Se alguma filha possuir a tag 'tag'
                if filha_ramo.tag == 'tag':

                    # Obtém o valor do atributo 'v' dessa tag
                    v = filha_ramo.get('v')

                    # Se contiver alguma informação da lista de remoção, esse nó será retirado
                    if v in remover:

                        # Verifica se o ramo já não foi colocado na lista
                        if ramo not in limpar:
                            limpar.append(ramo)
                            isremovida = True

            # Se aquele nó não será removido, então ele é mapeado
            if not isremovida:
                ponto = Ponto()

                # Obtém o id do nó, latitude e longitude
                ponto.set_id(ramo.get('id'))
                ponto.set_latitude(ramo.get('lat'))
                ponto.set_longitude((ramo.get('lon')))

                # Insere no dicionário de pontos
                pontos[ramo.get('id')] = ponto

        # Se o ramo for um caminho, possui informação a ser tratada
        elif ramo.tag == 'way':

            # Guardando o id da rua
            id_rua = ramo.get('id')

            # Identifica se aquela tag será retirada
            isremovida = False

            # Lista auxiliar para nós dos caminhos
            aux_ref = []

            # Percorre todas as tags filhas da tag ramo
            for filha_ramo in ramo:

                # Tag que possui as informações dos nós que formam a rua
                if filha_ramo.tag == 'nd':

                    # Insere o nó na lista auxiliar de referências daquele caminho
                    aux_ref.append(filha_ramo.get('ref'))

                # Se alguma filha possuir a tag 'tag'
                elif filha_ramo.tag == 'tag':

                    # Obtém o valor do atributo 'v' dessa tag
                    v = filha_ramo.get('v')

                    # Se contiver alguma informação da lista de remoção, esse nó será retirado
                    if v in remover:

                        # Marca a tag para ser removida
                        isremovida = True

            # Se a tag estiver marcada, ela é colocada na lista de limpeza
            if isremovida:

                # Nós da lista de referencia são passados para a lista final
                for no in aux_ref:
                    referencias_nos.append(no)

                # Se o ramo já não estiver na lista de limpeza, ele é adicionado
                if ramo not in limpar:
                    limpar.append(ramo)

            # Senão a rua é inserida no dicionário de ruas
            else:

                # Instancia uma rua
                rua = Rua()

                # Seta o id da rua
                rua.set_id(id_rua)

                for ref in referencias_nos:

                    # Verifica se o nó existe na lista de nós
                    if ref in pontos.keys():

                        # Insere na lista de nós da rua
                        # O ponto é buscado na lista de pontos com base na chave, que é seu id
                        rua.insere_ponto(pontos[ref])

                # Define a chave(id da rua) e insere no dicionário
                ruas[id_rua] = rua

    # Percorrendo o arquivo novamente retirando nós remanescentes
    for ramo in raiz:

        # Limpa as tags de caminhos que não serão utilizados
        if ramo.tag == 'node':

            # Se o id desse nó estiver nos nós remanescentes, ele será excluído
            if ramo.get('id') in referencias_nos:

                limpar.append(ramo)

                # Retira dos pontos mapeados os nós de caminhos excluídos
                if pontos.__contains__(ramo.get('id')):
                    pontos.pop(ramo.get('id'))

        # Chegando as tags de caminhos, nada mais precisa ser verificado
        if ramo.tag == 'way':
            break

    # Retira as tags do documento
    for item in limpar:
        raiz.remove(item)

    # Cria um documento de saída mais enxuto, sem tags que não serão utilizadas
    arvore.write('saida/saida.osm')

    print("Arquivo de saída gerado!")


# Função que faz a interligação dos pontos obtidos no mapa, forma as ruas e as plota
def mapeia_ruas(arquivo):

    lat = []
    lon = []

    tuplas_latlon = []

    # Obtem os pontos para serem plotados
    for x in pontos:
        tuplas_latlon.append((pontos[x].get_latitude(), pontos[x].get_longitude()))
        lat.append(pontos[x].get_latitude())
        lon.append(pontos[x].get_longitude())

    # Adiciona o local inicial a plotagem
    mapa_plot = gmplot.GoogleMapPlotter(lat[0], lon[0], 13)

    # Criando uma instância para leitura do XML que foi passado como parâmetro
    arvore = ET.parse(arquivo)
    # Obtém a tag raiz do arquivo
    raiz = arvore.getroot()

    # Começa a leitura das tags do arquivo
    for ramo in raiz:

        # Se a tag for um caminho, então ela será analisada
        if ramo.tag == 'way':

            # Realiza a instância de uma rua
            rua = Rua()

            # Usa o mesmo id da rua do arquivo de parâmetro na rua instanciada
            rua.set_id(ramo.get('id'))

            # Lista de tuplas com latitudes e longitudes dos pontos das ruas
            tuplas_rua = []

            # Ponto que está sendo analisado
            ponto_atual = Ponto()

            ponto_anterior = Ponto()

            # Percorrendo todas as tags de atributo da tag atual
            for filha_ramo in ramo:

                # Se a tag atributo for do tipo nd (nó)
                # Ela possui a referencia de um dos nós que compõe a rua
                if filha_ramo.tag == 'nd':

                    # Verifica se esse nó existe
                    if pontos.__contains__(filha_ramo.get('ref')):

                        # Salva o ponto atual, e insere suas coordenadas na lista de tuplas
                        ponto_atual = pontos[filha_ramo.get('ref')]
                        tuplas_rua.append((float(ponto_atual.get_latitude()), float(ponto_atual.get_longitude())))

                        # Insere o ponto na lista de pontos da rua
                        rua.insere_ponto(ponto_atual)

                        # Se o ponto anterior ao atual possuir algum id
                        # Significa que existe uma ligação de pontos a ser realizada
                        if ponto_anterior.get_id() != -1:

                            pontos[filha_ramo.get('ref')].realiza_ligacao(ponto_anterior)

                        ponto_anterior = ponto_atual

                # Identifica o atributo 'tag' da tag atual
                if filha_ramo.tag == 'tag':

                    # Identifica a chave nome, que indica o nome da rua e atribui a rua atual
                    if filha_ramo.get('k') == 'name':

                        rua.set_nome(filha_ramo.get('v'))

            # Verifica se a rua possui ao menos um ponto em sua formação
            # Se possuir, ela é inserida no dicionário de ruas
            if len(rua.get_pontos()) != 0:

                ruas[rua.get_id()] = rua

            # Se existir algo na lista de tuplas, significa que existem dados a serem exibidos
            if len(tuplas_rua) != 0:

                # Adiciona ao mapa de plotagem as coordenadas das ruas
                rua_lat, rua_lon = zip(*tuplas_rua)
                mapa_plot.scatter(rua_lat, rua_lon, '#3B0B39', size=5, marker=False)
                mapa_plot.plot(rua_lat, rua_lon, 'cornflowerblue', edge_width=3)

    # Adiciona ao mapa de plotagem as coordenadas dos pontos e gera o arquivo
    draw_lat, draw_lon = zip(*tuplas_latlon)
    mapa_plot.scatter(draw_lat, draw_lon, '#3B0B39', size=5, marker=False)
    mapa_plot.draw('saida/mapa.html')


# Função que monta o grafo que representa o mapa e o plota
def monta_grafo():

    coordenadas_pontos = {}

    for pnt in pontos:

        grafo_cidade.add_node(pontos[pnt].get_id())

        for pnt_ligado in pontos[pnt].get_pontos_vizinhos():

            distancia_pontos = calcula_distancia_pontos(pontos[pnt].get_latitude(), pontos[pnt].get_longitude(),
                                                        pnt_ligado.get_latitude(), pnt_ligado.get_longitude())

            grafo_cidade.add_edge(pontos[pnt].get_id(), pnt_ligado.get_id(), weight=distancia_pontos * distancia_pontos)

    for node in nx.nodes(grafo_cidade):

        coordenadas_pontos[node] = pontos[node].retorna_coordenadas()

    nx.draw(grafo_cidade, node_size=0.5, node_color='grey', alpha=0.5, with_labels=False, pos=coordenadas_pontos)
    plt.savefig("saida/GrafoCidade.png", dpi=1000)


# Função que calcula a distância entre dois pontos, utilizando a função pronta da biblioteca geopy
def calcula_distancia_pontos(lat_ponto1, lon_ponto1, lat_ponto2, lon_ponto2):

    # Converte as coordenadas em tuplas
    coord_pnt1 = (lat_ponto1, lon_ponto1)
    coord_pnt2 = (lat_ponto2, lon_ponto2)

    return geopy.distance.geodesic(coord_pnt1, coord_pnt2).m