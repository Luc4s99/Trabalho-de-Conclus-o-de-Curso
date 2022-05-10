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
from RoteamentoTCC.Ponto import *
# Classe que define uma rua no mapa
from RoteamentoTCC.Rua import *
# Biblioteca que realiza operações com grafos
import networkx as nx
# Biblioteca para cálculos utilizando coordenadas geográficas
import geopy.distance
# Biblioteca para plotagem de gráficos e dados em geral
from matplotlib import pyplot as plt
# Biblioteca que contém úteis matemáticos
import numpy as np
# Biblioteca para a realização do agrupamento dos pontos
from sklearn.cluster import KMeans
# Biblioteca para limpeza de lixo de memória(garbage collector)
import gc
# Classe que define e executa o Non-dominated Sorting Genetic Algorithm II
from RoteamentoTCC.nsga.nsga2 import NSGA2

# Parâmetros para a plotagem de imagens
plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

# Armazena em um dicionario os pontos que foram mapeados na leitura do arquivo
pontos = {}

# Dicionário que armazena os pontos que restaram depois da otimização do grafo
pontos_otimizados = {}

# Armazena em um dicionario as ruas que foram mapeadas na leitura do arquivo
ruas = {}

# Grafo que será utilizado para representar o mapa da cidade já otimizado
grafo_cidade_otimizado = nx.Graph()

# Capacidade de lixo que um caminhão de lixo possuiem KG
CAPACIDADE_CAMINHAO = 10000

# Identifica o id ponto que representa o depósito
DEPOSITO = '3627233002'
# Identificador do depósito no arquivo utilizado para testes(Somente para testes)
# DEPOSITO = '7560818573'

# ID's de pontos que serão retirados "manualmente" para que o NSGA-II seja melhor calibrado
pontos_retirar_manual = ['2386701666', '2386701653', '353461444', '8256516317', '1344105186', '2386701633',
                         '7105572020', '8405717762', '5420412669', '353460735', '1344104828', '1826545975',
                         '4055552318', '5420412934', '7802750044', '3545678179', '4055552327', '7872173741']

# Quantidade total de lixo que foi gerada na cidade
quantidade_lixo_cidade = 0


def __init__():
    pass


# Realiza a leitura do arquivo de entrada
def le_arquivo(arquivo_entrada: str):

    # Criando uma instância para leitura do XML que foi passado como parâmetro
    arvore = ET.parse(arquivo_entrada)
    # Obtém a tag raiz do arquivo
    raiz = arvore.getroot()
    # Referencias de nós de caminhos para serem removidos
    referencias_nos = []

    # ID's de ruas que serão retiradas "manualmente" para que o grafo fique melhor organizado
    ruas_retirar_manual = ['171661658', '837763522', '844146081', '119717353', '835715874']

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
                ponto.id = ramo.get('id')
                ponto.latitude = ramo.get('lat')
                ponto.longitude = (ramo.get('lon'))

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
                    if v in remover or id_rua in ruas_retirar_manual:
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
                rua.id = id_rua

                # Percorre os nós daquele caminho
                for ref in aux_ref:

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

        # Chegando as tags de caminhos, nada mais precisa ser verificado
        if ramo.tag == 'way':
            break

    # Verifica se alguma rua que não será retirada possui o nó analisado
    # Se existir tal rua, o nó não poderá ser retirado
    for _, rua in ruas.items():

        # O dicionário 'ruas' contém todas as ruas que serão utilizadas e já estão validadas
        # Então se o ponto estiver em uma dessas ruas ele já não pode ser retirado
        for rua_ponto in rua.pontos:

            # Passa por todos os nós da lista de limpeza, verificando se alguns deles compõe a rua
            for no_limpar in limpar:

                # Se identificar que algum nó está na rua
                if no_limpar.attrib['id'] == rua_ponto.id:
                    # Ele é retirado da lista de limpeza
                    limpar.remove(no_limpar)

    # Passa pela lista de pontos retirando os nós que serão limpos
    # Como a lista 'limpar' foi verificada acima, todos os pontos que estão nessa lista com certeza serão eliminados
    for no_limpar in limpar:

        # Verifica antes se esta analisando um nó
        if no_limpar.tag == 'node':

            # Retira dos pontos mapeados os nós de caminhos excluídos e que não serão utilizados em outros caminhos
            if pontos.__contains__(no_limpar.attrib['id']):
                pontos.pop(no_limpar.attrib['id'])

    # Retira as tags do documento
    for item in limpar:
        raiz.remove(item)

    # Cria um documento de saída mais enxuto, sem tags que não serão utilizadas
    arvore.write('saida/saida.osm')

    print("Arquivo de saída gerado!")


def otimiza_grafo():
    # Percorre todos os nós que já foram obtidos
    for id_ponto, ponto in pontos.items():

        # Inicializa um contador para o ponto, se o mesmo aparecer mais de uma vez durante a iteração das ruas ele tem
        # grandes chances de ser uma esquina
        contador_ponto = 0

        # Verifica antes se o ponto é um dos que deve ser retirado "manualmente"
        if id_ponto in pontos_retirar_manual:
            continue

        # Primeiramente verifica se o ponto é o final de uma rua, se for deve ser inserido
        # O ponto que possui somente um vizinho, é considerado um final de rua
        if len(ponto.pontos_vizinhos) == 1:
            pontos_otimizados[id_ponto] = ponto

        # Se o ponto não foi inserido acima, existem mais testes a serem realizados
        if not pontos_otimizados.__contains__(ponto):

            # Percorre todas as ruas, verificando se aquele ponto está contido nela
            for id_rua, rua in ruas.items():

                # Verifica cada um dos pontos da rua, se bate com o ponto sendo analisado atualmente
                for ponto_rua in rua.pontos:

                    # Verifica se o ponto é válido
                    if ponto_rua is not None and ponto_rua.id != -1:

                        # Verifica se o id dos pontos bate
                        if ponto_rua.id == id_ponto:
                            # Incrementa o contador, pois o ponto faz parte da rua
                            contador_ponto = contador_ponto + 1

                        # Verifica se o contador está maior que 1, o que indica que o ponto pode ser uma esquina
                        if contador_ponto > 1:
                            # Insere o ponto na lista de pontos otimizados
                            pontos_otimizados[id_ponto] = ponto

                            # Encerra o for, pois o ponto já está na lista de otimizados
                            break


# Função que faz a interligação dos pontos obtidos no mapa, forma as ruas e as plota
def mapeia_ruas(arquivo):
    lat = []
    lon = []

    tuplas_latlon = []

    # Obtem os pontos para serem plotados
    for x in pontos:
        tuplas_latlon.append((pontos[x].latitude, pontos[x].longitude))
        lat.append(pontos[x].latitude)
        lon.append(pontos[x].longitude)

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
            rua.id = ramo.get('id')

            # Lista de tuplas com latitudes e longitudes dos pontos das ruas
            tuplas_rua = []

            # Ponto que está sendo analisado
            ponto_atual = Ponto(gera_label=False)

            # Ponto anterior ao atual, usado para identificar vizinhos
            ponto_anterior = Ponto(gera_label=False)

            # Percorrendo todas as tags de atributo da tag atual
            for filha_ramo in ramo:

                # Se a tag atributo for do tipo nd (nó)
                # Ela possui a referencia de um dos nós que compõe a rua
                if filha_ramo.tag == 'nd':

                    # Verifica se esse nó existe
                    if pontos.__contains__(filha_ramo.get('ref')):

                        # Salva o ponto atual, e insere suas coordenadas na lista de tuplas
                        ponto_atual = pontos[filha_ramo.get('ref')]
                        tuplas_rua.append((float(ponto_atual.latitude), float(ponto_atual.longitude)))

                        # Insere o ponto na lista de pontos da rua
                        rua.insere_ponto(ponto_atual)

                        # Se o ponto anterior ao atual possuir algum id
                        # Significa que existe uma ligação de pontos a ser realizada
                        if ponto_anterior.id != -1:
                            # Informa que o ponto atual possui ligação com o ponto anterior
                            pontos[filha_ramo.get('ref')].realiza_ligacao(ponto_anterior)

                            # E consequentemente o ponto anterior possui ligação com o ponto atual
                            pontos[ponto_anterior.id].realiza_ligacao(ponto_atual)

                        ponto_anterior = ponto_atual

                # Identifica o atributo 'tag' da tag atual
                if filha_ramo.tag == 'tag':

                    # Identifica a chave nome, que indica o nome da rua e atribui a rua atual
                    if filha_ramo.get('k') == 'name':
                        rua.nome = filha_ramo.get('v')

            # Verifica se a rua possui ao menos um ponto em sua formação
            # Se possuir, ela é inserida no dicionário de ruas
            if len(rua.pontos) != 0:
                ruas[rua.id] = rua

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
def monta_grafo_otimizado(pontos_grafo, nome_arquivo_saida):

    coordenadas_pontos = {}

    # Percorre todas as ruas do grafo
    for rua_id, rua in ruas.items():

        # Percorre cada um dos pontos que forma a rua
        for ponto_rua in rua.pontos:

            # Verifica se o ponto da rua que está sendo analisado é um ponto válido
            if ponto_rua.id in pontos_grafo.keys():

                # Esta variável indica qual o index do ponto que está sendo analisado
                index_ponto = rua.pontos.index(ponto_rua)

                # Insere cada um dos pontos no grafo para que sejam plotados
                grafo_cidade_otimizado.add_node(ponto_rua.id)

                # Percorre novamente todos os pontos que formam aquela rua
                for ponto_rua_ligar in rua.pontos:

                    # Porem só serão analisados pontos que estão a frente do ponto analisado atualmente
                    # E pontos válidos
                    if (rua.pontos.index(ponto_rua_ligar) > index_ponto) and (
                            ponto_rua_ligar.id in pontos_grafo.keys()):

                        # Se um ponto válido for encontrado para frente do que está sendo analisado
                        if ponto_rua_ligar.id in pontos_grafo.keys():
                            # Função que calcula a distância entre os pontos
                            distancia_pontos = calcula_distancia_real(rua_id, ponto_rua, ponto_rua_ligar)

                            # Insere a aresta no grafo
                            grafo_cidade_otimizado.add_edge(ponto_rua.id, ponto_rua_ligar.id,
                                                            weight=distancia_pontos)

                            # Para o for, pois a ligação desse ponto já foi encontrada
                            break

    # Após o grafo montado, realiza o cálculo de distância de todos os pontos até o depósito
    # for ponto in grafo_cidade_otimizado.nodes:
    for ponto in pontos_otimizados.values():
        # Pega o ponto atual e realiza o cálculo através do algoritmo de dijkstra até o depósito
        # Essa distância é armazenada no próprio ponto
        ponto.distancia_deposito = nx.dijkstra_path_length(grafo_cidade_otimizado, ponto.id, DEPOSITO)

    # Armazena as coordenadas dos pontos para que seja realizada a plotagem
    for node in nx.nodes(grafo_cidade_otimizado):
        coordenadas_pontos[node] = pontos[node].retorna_coordenadas()

    # Desenha a figura e salva com o nome definido
    nx.draw(grafo_cidade_otimizado, node_size=0.5, node_color='grey', alpha=0.5, with_labels=False,
            pos=coordenadas_pontos)
    plt.savefig(nome_arquivo_saida, dpi=500)

    # Limpa a figura para evitar que o marplotlib se "lembre" da figura
    plt.clf()

    # Fecha a instância do pyplot para que nenhum lixo de memória seja inserido na próxima imagem
    plt.close()

    # Realiza a coleta de lixo de memória
    gc.collect()


# Função que calcula a distância real entre dois pontos de uma rua
# A distância real neste caso, é a distância considerando todos os pontos da rua, até os pontos que foram retirados pela
# otimização
def calcula_distancia_real(rua_id, ponto_inicial, ponto_final):

    # Obtem a rua do dicionário de ruas
    rua = ruas[rua_id]

    # Inicia a variável que aramzena a distância total entre os pontos
    distancia_total_pts = 0

    # Indica que o ponto inicial foi encontrado e que as distâncias podem começar a serem somadas
    achou_ponto_inicial = False

    # Percorre todos os pontos da rua, até achar o ponto inicial
    for ponto_rua in rua.pontos:

        # Verifica se o ponto corresponde ao ponto inicial
        if ponto_rua.id == ponto_inicial.id:
            achou_ponto_inicial = True

        # Se o ponto inicial foi encontrado, as distâncias podem ser somadas
        if achou_ponto_inicial:

            # Vai adicionando as distâncias até o próximo ponto a distância total final
            distancia_total_pts += calcula_distancia_pontos(ponto_inicial.latitude, ponto_inicial.longitude,
                                                            ponto_rua.latitude, ponto_rua.longitude)

            # Se o ponto sendo analisado atualmente for o ponto final, então deve ser parada a iteração
            if ponto_rua.id == ponto_final.id:
                break

    # Adiciona o tamanho do segmento de rua calculado, ao total da rua
    # Ao final de todas as iteraçãoes dessa função, todas as ruas terão seus tamanhos totais já calculados
    rua.tamanho_rua += distancia_total_pts

    # Retorna a distância total
    return distancia_total_pts


# Função que monta o grafo que representa o mapa e o plota
def monta_grafo(nome_arquivo):
    # Grafo que será utilizado para representar o mapa da cidade
    grafo_cidade = nx.Graph()

    coordenadas_pontos = {}

    # Percorre todos os pontos definidos
    for pnt in pontos:

        # Insere cada um dos pontos no grafo para que sejam plotados
        grafo_cidade.add_node(pontos[pnt].id)

        # Verifica cada vizinho de ponto para que sejam montadas as arestas
        for pnt_ligado in pontos[pnt].pontos_vizinhos:
            # Calcula a distância entre os pontos, que será utilizada como peso para a aresta
            distancia_pontos = calcula_distancia_pontos(pontos[pnt].latitude, pontos[pnt].longitude,
                                                        pnt_ligado.latitude, pnt_ligado.longitude)

            # Insere a aresta no grafo
            grafo_cidade.add_edge(pontos[pnt].id, pnt_ligado.id, weight=distancia_pontos)

    # Armazena as coordenadas dos pontos para que seja realizada a plotagem
    for node in nx.nodes(grafo_cidade):
        coordenadas_pontos[node] = pontos[node].retorna_coordenadas()

    # Desenha a figura e salva com o nome definido
    nx.draw(grafo_cidade, node_size=0.5, node_color='grey', alpha=0.5, with_labels=False, pos=coordenadas_pontos)
    plt.savefig(nome_arquivo, dpi=500)

    # Limpa a figura para evitar que o marplotlib se "lembre" da figura
    plt.clf()

    # Fecha a instância do pyplot para que nenhum lixo de memória seja inserido na próxima imagem
    plt.close()

    # Realiza a coleta de lixo de memória
    gc.collect()


# Função que calcula a demanda aproximada de lixo de cada rua e divide entre seus pontos
def calcula_demandas(nome_arquivo):
    # Identifica a variável global que armazena a quantidade de lixo total gerada na cidade
    global quantidade_lixo_cidade

    # Passa por todas as ruas
    for _, rua in ruas.items():

        # Gera a demanda de lixo aproximada da rua
        # Para a geração da demanda utiliza a distribuição de Weibull, que é uma distribuição de cauda longa
        # O parâmetro 10 é o tamanho médio de lote de casa para a cidade analisada, logo o tamanho da rua / 10 resulta
        # no total de casas aproximado que aquela rua contém
        # Multiplicado por 2 pois os dois lados da rua possuem casas
        # Isso é multiplicado por 3 pois, a média de pessoas por família é de 3 e a média de produção de lixo por pessoa
        # é de 1kg
        rua.quantidade_lixo_rua = int((np.random.weibull(5.) * rua.tamanho_rua / 10) * 2) * 3

        # A quantidade total de lixo da cidade é incrementada
        quantidade_lixo_cidade += rua.quantidade_lixo_rua

        # Divide de forma uniforme entre os pontos da rua a quantidade de lixo estimada
        qtd_lixo_ponto = rua.quantidade_lixo_rua / len(rua.pontos)

        # Percorre todos os pontos da rua atribuindo a quantidade de lixo
        for ponto in rua.pontos:

            # Se o ponto analisado for o próprio depósito, não será atribuída demanda de lixo para ele
            if ponto.id == DEPOSITO:
                continue

            ponto.quantidade_lixo = qtd_lixo_ponto

    coordenadas_pontos = {}

    # Armazena as coordenadas dos pontos para que seja realizada a plotagem
    for node in nx.nodes(grafo_cidade_otimizado):
        coordenadas_pontos[node] = pontos[node].retorna_coordenadas()

    # Após gerar as demandas será printado o grafo com novos dados
    # Cores que serão utilizadas nos nós
    cores = []
    # Tamanho dos nós que serão plotados no grafo
    tamanhos = []

    # Percorre os nós para adicionar informações nas duas listas acima
    for node in grafo_cidade_otimizado:

        # Se o nó for o depósito, recebe uma coloração e tamanho único
        if node == DEPOSITO:

            cores.append('blue')
            tamanhos.append(20)
        # Senão, as cores e tamanhos serão definidos a partir da quantidade de lixo que aquele ponto possui
        else:

            qtd_lixo = pontos_otimizados.get(node).quantidade_lixo

            if qtd_lixo <= 10:

                cores.append('green')
                tamanhos.append(2)
            elif 10 < qtd_lixo <= 20:

                cores.append('yellow')
                tamanhos.append(5)
            else:

                cores.append('red')
                tamanhos.append(10)

    # Desenha a figura e salva com o nome, cores e tamanho definidos
    nx.draw(grafo_cidade_otimizado, node_size=tamanhos, node_color=cores, alpha=0.5, with_labels=False,
            pos=coordenadas_pontos)
    plt.savefig(nome_arquivo, dpi=500)

    # Limpa a figura para evitar que o marplotlib se "lembre" da figura
    plt.clf()

    # Fecha a instância do pyplot para que nenhum lixo de memória seja inserido na próxima imagem
    plt.close()

    # Realiza a coleta de lixo de memória
    gc.collect()


# Função que realiza o agrupamento de pontos próximos
def k_means():
    # Define o número de clusters
    # Definido pela quantidade total de lixo gerada dividida pela capacidade de um caminhão
    numero_clusters = round(quantidade_lixo_cidade / CAPACIDADE_CAMINHAO)
    # numero_clusters = 5

    # Monta a matriz com as coordenadas
    matriz = []

    # Passa por todos os pontos otimizados
    for _, ponto in pontos_otimizados.items():

        # Garante que o depósito não será levado em conta no agrupamento
        if ponto.id == DEPOSITO:
            continue

        # Insere as coordenadas na matriz
        matriz.append([float(ponto.latitude), float(ponto.longitude)])

    # Cria o array pela biblioteca do numpy
    coordenadas_pontos = np.array(matriz)

    # Realiza uma instância do algoritmo do kmeans
    kmeans = KMeans(numero_clusters, init='k-means++', n_init=10, max_iter=300)

    # Executa o kmeans para encontrar a localização que devem ficar os agrupamentos
    pred_y = kmeans.fit_predict(coordenadas_pontos)

    # Dicionário que agrupa os pontos com base nos seus respectivos agrupamentos
    pontos_agrupados = {}

    # Associa o dicionário de pontos aos seus respectivos agrupamentos
    cont = 0

    # Nesse loop cada ponto será identificado com seu respectivo agrupamento
    # E também serão organizados os pontos com o mesmo agrupamento
    for ponto in pontos_otimizados.values():

        # Pula o depósito pois ele foi ignorado ao fazer os agrupamentos
        if ponto.id == DEPOSITO:
            continue

        # Verifica antes se o ponto já não está associado a um agrupamento
        if ponto.id_agrupamento == -1:

            ponto.id_agrupamento = pred_y[cont]

            # Se o dicionário que agrupa os pontos ainda não tiver aquela chave
            # Significa que nenhum ponto daquele cluster foi inserido ainda
            if ponto.id_agrupamento not in pontos_agrupados.keys():

                # Insere a chave do cluster e o seu respectivo ponto
                pontos_agrupados[ponto.id_agrupamento] = [ponto]
            else:

                # Senão o agrupamento já existe no dicionário
                # Então o ponto é simplesmente inserido
                pontos_agrupados[ponto.id_agrupamento].append(ponto)

        # Incrementa o contador
        cont += 1

    # Gera uma imagem dos agrupamentos gerados pelo k-means
    # Utilizada somente para testes
    """plt.scatter(coordenadas_pontos[:, 1], coordenadas_pontos[:, 0], c=pred_y)

    plt.grid()

    plt.scatter(kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 0], s=70, c='red', )

    plt.show()"""

    # Retorna os pontos divididos pelos agrupamentos
    return pontos_agrupados


# Função que realiza o processamento das rotas nos agrupamentos gerados
def processamento_rotas(pontos_agrupados):
    # Realiza o processamento de rota para cada um dos clusters
    # Em cada um deles é executado o NSGA-II
    for id_cluster, cluster in pontos_agrupados.items():

        # Executa o algoritmo do NSGA-II
        NSGA2(10, 15, cluster, 0.05, 0.6, CAPACIDADE_CAMINHAO, grafo_cidade_otimizado).run()


# Função que calcula a distância entre dois pontos, utilizando a função pronta da biblioteca geopy
def calcula_distancia_pontos(lat_ponto1, lon_ponto1, lat_ponto2, lon_ponto2):
    # Converte as coordenadas em tuplas
    coord_pnt1 = (lat_ponto1, lon_ponto1)
    coord_pnt2 = (lat_ponto2, lon_ponto2)

    return geopy.distance.geodesic(coord_pnt1, coord_pnt2).m


# Funçã que retorna a soma das distâncias entre todos os pontos que formam um indivíduo
def calcula_metricas(individuo):

    # Armazena a distância total do indivíduo
    distancia_total = 0
    # Armazena o número total de ruas utilizadas pelo indivíduo
    total_ruas = 0
    # Total de ruas que possuem conexão
    total_ruas_con = 0
    # Lista auxiliar para detectar ruas repetidas
    ruas_encontradas = []
    # Auxiliar para detecção de ruas conectadas
    rua_ant = None

    if len(individuo.genome) > 0:

        # Verifica todas as tuplas de pontos que o indivíduo contém
        for cont, rua in enumerate(individuo.genome):

            # Adiciona a distância do depósito até o primeiro e último ponto do genoma
            if cont == 0 or cont == (len(individuo.genome) - 1):

                distancia_total += rua[0].distancia_deposito

            # Primeiro, se calcula a distância
            if grafo_cidade_otimizado.get_edge_data(rua[0].id, rua[1].id) is not None:

                distancia_total += grafo_cidade_otimizado.get_edge_data(rua[0].id, rua[1].id).get("weight")

            # Em seguida, é verificada a métrica do total de ruas
            # Se a rua já foi encontrada ela não entra para a conta
            if rua not in ruas_encontradas:

                total_ruas += 1
            else:

                ruas_encontradas.append(rua)

            # Por último é verificada a quantidade de ruas que possuem ligação
            if cont == 0:

                rua_ant = rua
            else:

                # Se o primeiro ponto da rua atual for vizinho do último ponto da rua anterior
                # Significa que essas ruas possuem uma ligação
                if rua[0] in rua_ant[1].pontos_vizinhos:

                    total_ruas_con += 1

                rua_ant = rua

    return [distancia_total, total_ruas, total_ruas_con]


def retorna_maior_label():
    return Ponto.novo_label
