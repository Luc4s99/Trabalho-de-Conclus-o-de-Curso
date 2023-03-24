"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Thales Otávio
Link do GitHub: https://github.com/thalesorp/NSGA-II

E também possui partes desenvolvidas e baseadas em código desenvolvido por Mateus Soares
Link do GitHub: https://github.com/MateusSoares/Wireless-Access-Point-Optimization
"""
import sys
import random
from pygmo import hypervolume
import networkx as nx
import matplotlib.pyplot as plt
import RoteamentoTCC.util as util
from RoteamentoTCC.Rota import *

# Importando métodos úteis da classe população
from RoteamentoTCC.nsga.population import Population
# Importação do normalizador de dados
from sklearn.preprocessing import MaxAbsScaler
# Biblioteca para medição de tempo
import time
# Biblioteca com comandos úteis do sistema operacional
import os


# Classe que define o algoritmo NSGA-II
class NSGA2:

    # PARÂMETROS
    # generations: Número de gerações que o algortimo genético irá executar
    # population_size: Quantidade de indivíduos por população
    # mutation_rate: Probabilidade de ocorrer uma mutação em um indivíduo
    # crossover_rate: Probabilidade de ocorrer crossover
    # max_caminhoes: Quantidade máxima de caminhões que poderão ser gerados no gene de um indivíduo
    # max_clusters: Quantidade máxima de clusters que poderão ser gerados no gene de um indivíduo
    def __init__(self, generations, population_size, mutation_rate,
                 crossover_rate, max_caminhoes, min_clusters, max_clusters):

        self.generations = generations

        self.population_size = population_size

        self.crossover_rate = crossover_rate

        self.mutation_rate = mutation_rate

        self.max_caminhoes = max_caminhoes

        self.min_clusters = min_clusters

        self.max_clusters = max_clusters

        self.front = []

        self.population_file_name = "population_evolution.txt"

        # Identifica a configuração do arquivo
        config_arquivo = ""

        config_arquivo += "1" if generations == 200 else "2"
        config_arquivo += "1" if population_size == 100 else "2"
        config_arquivo += "1" if mutation_rate == 0.40 else "2"
        config_arquivo += "1" if crossover_rate == 0.60 else "2"

        self.factorial_file_name = f'{config_arquivo}_{generations}g-{population_size}p-{mutation_rate}m-{crossover_rate}c'

        self.runtime = 0

        # self.create_front_file("[1.1, 1.1, 1.1, 1.1]")
        self.create_front_file("[3, 3, 3]")

        # Depende da forma que será feita a mutação
        # self.genotype_mutation_probability = 0.5

        # Inicializacao da população
        self.population = Population(max_caminhoes, min_clusters, max_clusters)

        # Indica qual geração o algoritmo está executando
        self.geracao = 1

    # Método principal que executa o NSGA-II
    def run(self):

        start_time = time.time()

        # Criando a população inicial Pt
        self.population.initiate(self.population_size // 2)

        # Avalia os indivíduos gerados na população
        self.evaluate(self.population)

        # Armazena as fronteiras selecionadas pela ordenação de dominância
        self.fast_non_dominated_sort()

        # População originada do cruzamento dos indivíduos da primeira metade da população
        offspring_population = self.usual_crossover()

        self.evaluate(offspring_population)

        # Variável que irá armazenar a melhor fronteira
        best_front = None

        # Passa pelo número de gerações definido
        for i in range(self.generations):

            print(f"\t-> Geração {i + 1}")

            # Realiza a união entre as duas populações
            # A população agora tem seu tamanho completo
            self.population.union(offspring_population)

            # Separa a população em fronteiras, onde cada fronteira tem populações
            fronts = self.fast_non_dominated_sort()

            """# Como as fronteiras são ordenadas pelos melhores indivíduos
            # A primeira fronteira sempre terá as populações com os melhores indivíduos
            best_front = fronts[0]"""

            # Cálculo do crowding distance
            self.crowding_distance_assignment(fronts)

            # Depois de realizadas as operações, é gerada a próxima população, que deve ter tamanho igual a primeira
            # Essa população é chamada de Pt+1
            next_population = self.new_population()

            # Obtém indivíduos das fronterias até que a quantidade de indivíduos necessária seja alcançada
            for front in fronts:

                if next_population.size < self.population_size // 2:

                    # Ordena os indivíduos do front pelo crowding distance
                    self.sort_by_crowded_comparison(front)

                    for ind in front.individuals:

                        # Insere indivíduos na fronteira até que seu tamanho seja igual a Pt
                        if next_population.size < self.population_size // 2:

                            next_population.insert(ind)
                        else:

                            break

            # Como as fronteiras são ordenadas pelos melhores indivíduos
            # A primeira fronteira sempre terá as populações com os melhores indivíduos
            best_front = fronts[0]

            # Obtém a nova população Pt para a continuação do loop
            self.population = next_population

            # Monta a nova população Qt para a continuação do loop
            offspring_population = self.usual_crossover()
            self.evaluate(offspring_population)

            # Armazena a melhor fronteira para ser calculado o hypervolume
            self.add_population_to_file(best_front)

        self.runtime = time.time() - start_time

        self.calculate_hypervolume()

        # Gerando arquivos de saída
        self.gera_resultados(best_front)

        return best_front

    # Função que avalia um indivíduo de acordo com as métricas propostas
    def evaluate_individual(self, individual):

        # Armazena a variação de altitude
        variacao_altitude = 0

        # Inicializa a lista de pontos que o trajeto se iniciará em cada cluster
        individual.genome[2] = ([-1 for _ in range(individual.genome[1])])

        # Lista que representa o tempo gasto pelos caminhoes, a lista inicia com zero
        tempo_caminhoes = [0 for _ in range(individual.genome[0])]

        pontos_clusterizados = util.cache_mapas_eulerizados[individual.genome[1]][0]

        # Indica qual caminhão será analisado
        vez = 0

        # Lista que indica os pontos onde o lixo já foi recolhido
        recolhido = []

        # Realiza o processamento de rota para cada um dos clusters
        for id_cluster, cluster in pontos_clusterizados.items():

            distancia_cluster = 0
            quantidade_lixo_caminhao = 0

            rota_caminhao = Rota()

            # Termina a montagem do indivíduo, selecionando os pontos de onde começarão os trajetos nos clusters
            ponto_inicio = random.choice(cluster)

            individual.genome[2][id_cluster] = ponto_inicio

            grafo_cluster = util.cache_mapas_eulerizados[individual.genome[1]][1][id_cluster]

            # Realiza a rota euleriana pelo grafo
            # Começa pelo ponto selecionado para início da rota
            rota = list(util.nx.eulerian_path(grafo_cluster, source=ponto_inicio.id))
            rota_caminhao.rota.extend(rota)

            if len(rota) != 0:

                # Calcula a ida do caminhão até o cluster
                dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, util.DEPOSITO, rota[0][0])

                rota_caminhao.ida.extend(caminho)
                rota_caminhao.formata_rota_ida()

                # Incrementa a distância
                distancia_cluster += dist

            # Percorre a rota, calcula o tempo e verifica o lixo coletado
            for pnt_coleta in rota:

                # Incrementa a distância percorrida na rua atual
                distancia_cluster += grafo_cluster[pnt_coleta[0]][pnt_coleta[1]][0]["weight"]

                # Verifica se esses pontos já não foram visitados por esse indivíduo e coleta
                if pnt_coleta[0] not in recolhido:

                    individual.quantidade_lixo += util.pontos_otimizados[pnt_coleta[0]].quantidade_lixo

                    # Verifica antes se a capacidade do veículo vai ser ultrapassada ao recolher aquele ponto
                    if quantidade_lixo_caminhao + util.pontos_otimizados[pnt_coleta[0]].quantidade_lixo < util.CAPACIDADE_CAMINHAO:

                        quantidade_lixo_caminhao += util.pontos_otimizados[pnt_coleta[0]].quantidade_lixo
                        recolhido.append(pnt_coleta[0])
                    else:

                        # Se o caminhão encher, deve voltar ao depósito, depositar o lixo e voltar
                        # Ida do caminhão ao depósito
                        dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, pnt_coleta[0],
                                                                  util.DEPOSITO)

                        distancia_cluster += dist

                        # Volta do depósito até o ponto onde foi interrompida a coleta
                        dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, util.DEPOSITO,
                                                                  pnt_coleta[0])

                        distancia_cluster += dist

                        quantidade_lixo_caminhao = 0

                        # Recolhe finalmente o lixo
                        quantidade_lixo_caminhao += util.pontos_otimizados[pnt_coleta[0]].quantidade_lixo
                        recolhido.append(pnt_coleta[0])
                        # break

                if pnt_coleta[1] not in recolhido:

                    individual.quantidade_lixo += util.pontos_otimizados[pnt_coleta[1]].quantidade_lixo

                    # Verifica antes se a capacidade do veículo vai ser ultrapassada ao recolher aquele ponto
                    if quantidade_lixo_caminhao + util.pontos_otimizados[pnt_coleta[1]].quantidade_lixo < util.CAPACIDADE_CAMINHAO:

                        quantidade_lixo_caminhao += util.pontos_otimizados[pnt_coleta[1]].quantidade_lixo
                        recolhido.append(pnt_coleta[1])
                    else:

                        # Se o caminhão encher, deve voltar ao depósito, depositar o lixo e voltar
                        # Ida do caminhão ao depósito
                        dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, pnt_coleta[1],
                                                                  util.DEPOSITO)

                        distancia_cluster += dist

                        # Volta do depósito até o ponto onde foi interrompida a coleta
                        dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, util.DEPOSITO,
                                                                  pnt_coleta[1])

                        distancia_cluster += dist

                        quantidade_lixo_caminhao = 0

                        # Recolhe finalmente o lixo
                        quantidade_lixo_caminhao += util.pontos_otimizados[pnt_coleta[1]].quantidade_lixo
                        recolhido.append(pnt_coleta[1])

                # Incrementa a variação de altitude
                variacao_altitude += (util.pontos_otimizados[pnt_coleta[0]].altitude - util.pontos_otimizados[pnt_coleta[1]].altitude) / grafo_cluster[pnt_coleta[0]][pnt_coleta[1]][0]["weight"]

            if len(rota) != 0:

                # Calcula a volta do caminhao ao depósito
                dist, caminho = nx.single_source_dijkstra(util.grafo_cidade_simplificado, rota[-1][1], util.DEPOSITO)

                rota_caminhao.volta.extend(caminho)
                rota_caminhao.formata_rota_volta()

                # Incrementa a distância
                distancia_cluster += dist

            # Registra a rota feita pelo veículo para depois ser exibida
            if vez not in individual.rotas:

                individual.rotas[vez] = [rota_caminhao]
            else:

                individual.rotas[vez].append(rota_caminhao)

            # E incrementa no tempo do caminhão correspondente
            if vez == len(tempo_caminhoes):

                vez = 0

            # Realiza uma simulação do tempo gasto pelo caminhão para recolher o lixo com base na distância
            tempo_caminhoes[vez] += distancia_cluster
            vez += 1

        # Retorna a soma de tempo dos caminhões: Métrica de minimização
        # O valor absoluto da variação de altitude: Métrica de minimização
        # A quantidade de caminhões: Minimização
        return [sum(tempo_caminhoes), abs(variacao_altitude), individual.genome[0]]

    # Função que avalia os indivíduos gerados na população
    def evaluate(self, population):

        # Para a normalização os dados precisam estar no formato de uma matriz
        matrix_normalizar = []

        # Iterando sobre todos os indivíduos gerados na população
        for individual in population.individuals:

            # Verifica se o indivíduo já foi avaliado antes
            if not individual.solutions:

                # Avalia e retorna as soluções não normalizadas
                individual.non_normalized_solutions = self.evaluate_individual(individual)

            """matrix_normalizar = [[individual.non_normalized_solutions[0]], [individual.non_normalized_solutions[1]],
                                             [individual.non_normalized_solutions[2]], [individual.non_normalized_solutions[3]]]"""
            matrix_normalizar.append([individual.non_normalized_solutions[0],
                                      individual.non_normalized_solutions[1],
                                      individual.non_normalized_solutions[2]])

        # Instancia o escalar para fazer a normalização MIN/MAX dos dados
        escalar = MaxAbsScaler()

        escalar.fit(matrix_normalizar)

        # Percorre os indivíduos
        for individual in population.individuals:

            # Realiza a normalização dos dados do indivíduo em questão
            # normalizado = escalar.transform(matrix_normalizar)
            normalizado = escalar.transform([individual.non_normalized_solutions])

            # Insere o resultado nas soluções normalizadas do indivíduo
            individual.solutions = [normalizado[0][0], normalizado[0][1], normalizado[0][2]]

        self.geracao += 1

    # Retorna uma nova população vazia
    def new_population(self):

        return Population(self.max_caminhoes, self.min_clusters, self.max_clusters)

    # Ordena os indivíduos de acordo com suas dominâncias e os ordena em fronteiras
    def fast_non_dominated_sort(self):

        # Inicializa os indicadores de dominância de cada indivíduo
        self.population.reset_fronts()

        # Inicializando a lista de fronteiras e a primeira fronteira, que corresponde a primeira população
        fronts = list()
        fronts.append(self.new_population())

        # Verificação de dominância entre todos os indivíduos
        for i in range(self.population.size):

            # Obtém o indivíduo atual que será comparado aos demais
            individuo_atual = self.population.individuals[i]

            # Outro loop para passar por todos os indivíduos
            for j in range(self.population.size):

                # Obtém os indivíduos que serão comparados
                outro_individuo = self.population.individuals[j]

                # Verificação para que o indivíduo não compare a si mesmo
                if i != j:

                    # Verifica se domina ou é dominado pelos outros indivíduos
                    if individuo_atual.dominates(outro_individuo):

                        # Se ele domina, o outro indivíduo é inserido na lista de indivíduos dominados por ele
                        individuo_atual.dominated_by.append(outro_individuo)
                    elif outro_individuo.dominates(individuo_atual):

                        # Senão, a contagem de indivíduos que o dominam é incrementada
                        individuo_atual.domination_count += 1

            # Checa se o indivíduo atual é bom o suficiente para entrar na primeira fronteira
            # Na primeira fronteira estão os indivíduos que não são dominados por ninguém
            if individuo_atual.domination_count == 0:

                if individuo_atual not in fronts[0].individuals:
                    individuo_atual.rank = 1

                    fronts[0].insert(individuo_atual)

        i = 0

        # Loop que vai preenchendo as fronteiras com os indivíduos
        # Quando todos os indivíduos forem distribuídos, a última fronteira terá 0 indivíduos, e então o loop para
        while len(fronts[i].individuals) > 0:

            # Com a primeira fronteira montada, agora os indivíduos devem ser distribuídos nas demais
            fronts.append(self.new_population())

            for individual in fronts[i].individuals:

                # Para cada indivíduo que é dominado por um membro da fronteira acima da atual
                for dominated_individual in individual.dominated_by:

                    # O seu rank é diminuído em 1
                    dominated_individual.domination_count -= 1

                    # Se seu rank - 1 for igual a zero, significa que ele não é dominado por mais ninguém
                    if dominated_individual.domination_count == 0:
                        # Então o seu rank é reestabelicido e ele é adicionado na fronteira
                        # "+1" becasue "i" is index value, and rank starts from 1 and not 0
                        # "+1" because the rank it's for the next front
                        dominated_individual.rank = i + 2
                        fronts[len(fronts) - 1].insert(dominated_individual)
            i += 1

        # Retira a última fronteira que está vazia, devido ao loop acima
        del fronts[len(fronts) - 1]

        # Retorna todas as fronteiras com seus respectivos indivíduos
        return fronts

    # Calcula para cada indivíduo qual o valor do seu crowding distance
    def crowding_distance_assignment(self, fronts):

        # Percorre as populações presentes nas fronteiras
        for population in fronts:

            last_individual_index = len(population.individuals) - 1

            # Reseta o valor da crowding distance dos indivíduos
            for individual in population.individuals:
                individual.crowding_distance = 0

            # Percorre as soluções do indivíduo
            for solution_index in range(len(population.individuals[0].solutions)):

                # Ordenando a população de acordo com a solução de cada um
                population.individuals.sort(key=lambda x: x.solutions[solution_index])

                # O primeiro e último indivíduo da população atual recebem infinito como valor no crowding
                population.individuals[0].crowding_distance = sys.maxsize
                population.individuals[last_individual_index].crowding_distance = sys.maxsize

                min_value, max_value = population.get_extreme_neighbours(solution_index)

                # Calcula o crowding distance de cada solução para todos os indivíduos
                for i in range(1, last_individual_index):

                    right_neighbour_value = population.individuals[i + 1].solutions[solution_index]
                    left_neighbour_value = population.individuals[i - 1].solutions[solution_index]

                    # Evita casos de divisão por 0
                    if (max_value - min_value) == 0:

                        population.individuals[i].crowding_distance += (
                                    (right_neighbour_value - left_neighbour_value) / 1)
                    else:

                        population.individuals[i].crowding_distance += (
                                    (right_neighbour_value - left_neighbour_value) / (max_value - min_value))

    # Retorna o melhor indivíduo de acordo com o operador de crowding
    def crowded_comparison(self, individual_A, individual_B):

        if ((individual_A.rank < individual_B.rank)
                or ((individual_A == individual_B)
                    and (individual_A.crowding_distance > individual_B.crowding_distance))):
            return individual_A
        return individual_B

    # Ordena a população de acordo com o operador de crowding, utilizando o bubble sort
    def sort_by_crowded_comparison(self, population):

        for i in range(len(population.individuals) - 2):

            worst = population.individuals[i]

            for j in range(1, len(population.individuals) - i):
                worst = self.crowded_comparison(worst, population.individuals[j])

            population.individuals.remove(worst)
            population.individuals.append(worst)

        worst = population.individuals[0]
        population.individuals.remove(worst)
        population.individuals.append(worst)

    def tournament_selection(self):
        """Binary tournament selection according to crowded comparison operator"""

        first_candidate = self.population.get_random_individual()
        second_candidate = self.population.get_random_individual()

        return self.crowded_comparison(first_candidate, second_candidate)

    # Retorna o melhor indivíduo dentre dois sorteados aleatoriamente
    def usual_tournament_selection(self):

        # Seleciona dois indivíduos aleatórios da população
        primeiro_candidato = self.population.get_random_individual()
        segundo_candidato = self.population.get_random_individual()

        # Variáveis que armazenam a pontuação de cada um deles
        pontuacao_primeiro_candidato = 0
        pontuacao_segundo_candidato = 0

        # Compara os dois indivíduos para retornar o melhor
        # Primeiro verifica qual dos dois possui o menor tempo de percurso
        if primeiro_candidato.solutions[0] < segundo_candidato.solutions[0]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1

        # Depois verifica qual possui o menor percentual de lixo não recolhido
        """if primeiro_candidato.solutions[1] < segundo_candidato.solutions[1]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1"""

        # Verifica qual deles possui a menor variação de altitude
        # if primeiro_candidato.solutions[2] < segundo_candidato.solutions[2]:
        if primeiro_candidato.solutions[1] < segundo_candidato.solutions[1]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1

        # E por fim verifica qual possui a quantidade de caminhões mais otimizada
        # if primeiro_candidato.solutions[3] < segundo_candidato.solutions[3]:
        if primeiro_candidato.solutions[2] < segundo_candidato.solutions[2]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1

        # Após as pontuações realizadas, verifica qual obteve maior pontuação e o retorna
        if pontuacao_primeiro_candidato > pontuacao_segundo_candidato:
            return primeiro_candidato

        return segundo_candidato

    # Realiza o cruzamento entre dois pais para a geração de dois novos indivíduos
    # No momento o crossover utilizado é um crossover uniforme simples
    def crossover(self, pai1, pai2):

        # Listas que representam o genoma das proles
        child1_genome = list()
        child2_genome = list()

        # Probabilidade de 50% de pegar algum dos pais
        if random.random() < 0.5:

            # O genoma de index 1 e 2, devem vir sempre do mesmo pai pois eles possuem relação
            child1_genome.append(pai1.genome[0])
            child1_genome.append(pai2.genome[1])
            child1_genome.append(pai2.genome[2])

            child2_genome.append(pai2.genome[0])
            child2_genome.append(pai1.genome[1])
            child2_genome.append(pai1.genome[2])

            # Após a geração das proles, é feita a mutação
            child1_genome = self.mutation(child1_genome)
            child2_genome = self.mutation(child2_genome)
        else:

            child2_genome.append(pai1.genome[0])
            child2_genome.append(pai2.genome[1])
            child2_genome.append(pai2.genome[2])

            child1_genome.append(pai2.genome[0])
            child1_genome.append(pai1.genome[1])
            child1_genome.append(pai1.genome[2])

            child1_genome = self.mutation(child1_genome)
            child2_genome = self.mutation(child2_genome)

        # Retorna os dois indivíduos resultantes do cruzamento
        return child1_genome, child2_genome

    # Seleciona os pais para a realização do crossover e geração dos filhos
    def usual_crossover(self):

        genomes_list = list()

        # O loop conta de 2 em 2 pois cada iteração gera 2 indivíduos
        # for _ in range(0, self.population_size, 2):
        for _ in range(0, self.population_size // 2, 2):

            # Seleciona dois pais bons para realizarem o crossover
            parent1 = self.usual_tournament_selection()
            parent2 = self.usual_tournament_selection()

            # Verifica se será realizado o crossover entre os pais
            # Isso é feito para que alguns indivíduos acabem sendo mantidos
            if random.random() < self.crossover_rate:

                # Realiza o crossover entre os pais e gera o genoma dos filhos
                child1_genome, child2_genome = self.crossover(parent1, parent2)

            # Se o crossover não for realizado, então é feita uma cópia dos pais que serão mantidos na população
            else:

                child1_genome = parent1.genome
                child2_genome = parent2.genome

            # Adiciona o genoma dos filhos na lista
            genomes_list.append(child1_genome)
            genomes_list.append(child2_genome)

        # Verifica se não foram gerados indivíduos a mais
        if len(genomes_list) > self.population_size // 2:

            genomes_list.pop()

        # Cria a população filha
        offspring_population = self.new_population()

        # Adiciona cada uma das crias geradas a população
        for child_genome in genomes_list:

            offspring_population.new_individual(child_genome)

        return offspring_population

    # Método que realiza mutação no genoma do indivíduo
    def mutation(self, genome):

        # Verifica se a mutação irá ocorrer
        if random.uniform(0, 1) > self.mutation_rate:

            # Se a mutação não for ocorrer, então o genoma é apenas retornado sem nenhuma modificação
            return genome

        # Verifica se será o primeiro ou o segundo gene a sofrer a mutação
        if random.random() < 0.5:

            # Sorteia se será somado ou subtraído do gene
            if random.random() < 0.5:

                genome[0] += random.randint(1, 10)
            else:

                genome[0] -= random.randint(1, 10)

            # Garante que o intervalo não ficará zerado, negativo ou maior do que deve
            if genome[0] < 1:

                genome[0] = 1

            elif genome[0] > self.max_caminhoes:

                genome[0] = self.max_caminhoes

            # Busca pela clusterização armazenada em cache
            pnts_clusterizados = util.cache_mapas_eulerizados[genome[1]][0]

            # Percorre os pontos de início dos cluster para aplicar mutação
            for i, ponto_inicio in enumerate(genome[2]):

                if random.random() < 0.5:

                    genome[2][i] = random.choice(pnts_clusterizados[i])

        else:

            # Sorteia se será somado ou subtraído do gene
            if random.random() < 0.5:

                genome[1] += random.randint(1, 10)
            else:

                genome[1] -= random.randint(1, 10)

            # Garante que o intervalo não ficará zerado, negativo ou maior do que deve
            if genome[1] < self.min_clusters:

                genome[1] = self.min_clusters

            elif genome[1] > self.max_clusters:

                genome[1] = self.max_clusters

            # Já que houve alteração, devem ser gerados outros pontos de início
            genome[2] = []
            genome[2] = [-1 for _ in range(genome[1])]

            # Busca pela clusterização armazenada em cache
            pnts_clusterizados = util.cache_mapas_eulerizados[genome[1]][0]

            # Realiza o sorteio dos pontos novamente
            for i in range(len(genome[2])):

                genome[2][i] = random.choice(pnts_clusterizados[i])

        return genome

    # Cria o arquivo do front e insere o ponto de referência para o cálculo do hypervolume
    def create_front_file(self, reference_point):

        with open(self.population_file_name, "w") as file_:

            file_.write(reference_point + "\n")

    # Insere no arquivo a melhor front para o formato que será utilizado no cálculo do hypervolume
    def add_population_to_file(self, front):

        with open(self.population_file_name, "a") as file_:

            objectives = "["

            for individual in front.individuals:

                objectives += str(individual.solutions) + ", "

            objectives = objectives[:-2] + "]\n"

            file_.write(objectives)

    # Executa o cálculo de hypervolume e salva num arquivo
    def calculate_hypervolume(self):

        population_file_name = "population_evolution.txt"
        output_file_name = "saida/Resultados/output_" + self.factorial_file_name + ".txt"

        fronts = []
        result = []

        with open(population_file_name, 'r') as f:
            hv_ref = eval(f.readline())
            for line in f:
                fronts.append(eval(line))

        # Calcula o hypervolume dos fronts
        for front in fronts:
            hv = hypervolume(front)
            result.append(hv.compute(hv_ref))

        # Gera o arquivo com os resultados
        # Primeira coluna representa o valor do hypervolume, segunda o tempo de execução
        try:

            with open(output_file_name, "a") as f:

                line = str(result[-1]) + "," + str(self.runtime) + "\n"
                f.write(line)
        except IOError:

            with open(output_file_name, "w") as f:

                line = "hv\ttime\n"
                f.write(line)
                line = str(result[-1]) + "," + str(self.runtime) + "\n"
                f.write(line)

        file_path = os.path.realpath(__file__)
        # directory = file_path[:-5]
        directory = file_path[:-2]

        plt.plot(range(1, len(result) + 1), result, 'ro')
        plt.ylabel("hypervolume Score")
        plt.xlabel("Generations")
        plt.savefig(directory + self.factorial_file_name + "_hypervolume.png")

        # Limpa a figura para evitar que o matplotlib se "lembre" da figura
        plt.clf()

        # Fecha a instância do pyplot para que nenhum lixo de memória seja inserido na próxima imagem
        plt.close()

    # Gera um arquivo com os resultados obtidos pelo algoritmo
    """def gera_resultados(self, front):

        with open("saida/resultados/dados_coleta.txt", "w") as arq:

            arq.write("*** RESULTADOS OBTIDOS DA COLETA ***\n")

            # Resultados de lixo recolhido
            arq.write(f"\nQuantidade de lixo recolhido(kg): {front.individuals[0].quantidade_lixo} ({round((front.individuals[0].quantidade_lixo * 100) / util.quantidade_lixo_cidade)}%)")

            # Resultados sobre os parâmetros utilizados
            arq.write(f"\nNúmero de caminhões utilizados para a realização da coleta: {front.individuals[0].genome[0]}")
            arq.write(f"\nNúmero de agrupamentos realizados pelo mapa: {front.individuals[0].genome[1]}")

        # Para cada caminhão utilizado na coleta, gera um mapa com a rota a ser realizada por ele
        for caminhao, rotas_caminhao in front.individuals[0].rotas.items():

            # Percorre cada uma das rotas do caminhão para realizar o plot
            for rota in rotas_caminhao:

                pontos_lat_lon = []
                mapa_plot = None
                ruas_lat_lon = []

                # Em cada rota, percorre os pontos que a formam
                for pnt in rota:

                    # Obtém a latitude e longitude dos pontos a serem plotados
                    pontos_lat_lon.append((util.pontos[pnt[0]].latitude, util.pontos[pnt[0]].longitude))
                    pontos_lat_lon.append((util.pontos[pnt[1]].latitude, util.pontos[pnt[1]].longitude))

                    # Obtém a rua referente a aresta representada pelos pontos
                    rua = util.grafo_cidade_simplificado[pnt[0]][pnt[1]][0]["rua"]

                    for pnt_rua in rua.pontos:

                        ruas_lat_lon.append((float(pnt_rua.latitude), float(pnt_rua.longitude)))

                    if mapa_plot is None:

                        # Adiciona o local inicial a plotagem
                        mapa_plot = util.gmplot.GoogleMapPlotter(util.pontos[pnt[0]].latitude,
                                                                 util.pontos[pnt[0]].longitude, 13)

                    rua_lat, rua_lon = zip(*ruas_lat_lon)
                    mapa_plot.scatter(rua_lat, rua_lon, '#3B0B39', size=5, marker=False)
                    mapa_plot.plot(rua_lat, rua_lon, 'cornflowerblue', edge_width=3)

                draw_lat, draw_lon = zip(*pontos_lat_lon)
                mapa_plot.scatter(draw_lat, draw_lon, '#3B0B39', size=5, marker=False)
                mapa_plot.draw(f'saida/Resultados/rotas/rota_{caminhao}.html')"""

    """def gera_resultados(self, front):

        # Arquivo com algumas informações gerais da coleta
        with open("saida/resultados/dados_coleta.txt", "w") as arq:

            arq.write("*** RESULTADOS OBTIDOS DA COLETA ***\n")

            # Resultados de lixo recolhido
            arq.write(
                f"\nQuantidade de lixo recolhido(kg): {front.individuals[0].quantidade_lixo} ({round((front.individuals[0].quantidade_lixo * 100) / util.quantidade_lixo_cidade)}%)")

            # Resultados sobre os parâmetros utilizados
            arq.write(f"\nNúmero de caminhões utilizados para a realização da coleta: {front.individuals[0].genome[0]}")
            arq.write(f"\nNúmero de agrupamentos realizados pelo mapa: {front.individuals[0].genome[1]}")

        # Para cada caminhão utilizado na coleta, gera um mapa com a rota a ser realizada por ele
        for caminhao, rotas_caminhao in front.individuals[0].rotas.items():

            # Percorre cada uma das rotas do caminhão para realizar o plot
            for num_rota, rota in enumerate(rotas_caminhao):

                # Abre os arquivos que irão descrever a rota do caminhão
                with open(f"saida/resultados/rotas/caminhao{caminhao}_rota_{num_rota}.kml", "w") as arq, \
                        open(f"saida/resultados/rotas/caminhao{caminhao}_rota_{num_rota}.txt", "w") as txt:

                    # Para o arquivo kml, o cabeçalho é padrão, muda somente o nome
                    arq.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                              "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n"
                              "<Document>\n"
                              f"<name>Rota {num_rota} caminhão {caminhao}</name>\n"
                              "<Style id=\"icon-1899-DB4436-nodesc-normal\">\n"
                              "<IconStyle>\n"
                              "<color>ff3644db</color>\n"
                              "<scale>1</scale>\n"
                              "<Icon>\n"
                              "<href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>\n"
                              "</Icon>\n"
                              "<hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>\n"
                              "</IconStyle>\n"
                              "<LabelStyle>\n"
                              "<scale>0</scale>\n"
                              "</LabelStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<Style id=\"icon-1899-DB4436-nodesc-highlight\">\n"
                              "<IconStyle>\n"
                              "<color>ff3644db</color>\n"
                              "<scale>1</scale>\n"
                              "<Icon>\n"
                              "<href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>\n"
                              "</Icon>\n"
                              "<hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>\n"
                              "</IconStyle>\n"
                              "<LabelStyle>\n"
                              "<scale>1</scale>\n"
                              "</LabelStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<StyleMap id=\"icon-1899-DB4436-nodesc\">\n"
                              "<Pair>\n"
                              "<key>normal</key>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc-normal</styleUrl>\n"
                              "</Pair>\n"
                              "<Pair>\n"
                              "<key>highlight</key>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc-highlight</styleUrl>\n"
                              "</Pair>\n"
                              "</StyleMap>\n"
                              "<Style id=\"line-1267FF-5000-nodesc-normal\">\n"
                              "<LineStyle>\n"
                              "<color>ffff6712</color>\n"
                              "<width>5</width>\n"
                              "</LineStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<Style id=\"line-1267FF-5000-nodesc-highlight\">\n"
                              "<LineStyle>\n"
                              "<color>ffff6712</color>\n"
                              "<width>7.5</width>\n"
                              "</LineStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<StyleMap id=\"line-1267FF-5000-nodesc\">\n"
                              "<Pair>\n"
                              "<key>normal</key>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc-normal</styleUrl>\n"
                              "</Pair>\n"
                              "<Pair>\n"
                              "<key>highlight</key>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc-highlight</styleUrl>\n"
                              "</Pair>\n"
                              "</StyleMap>\n"
                              "<Placemark>\n"
                              f"<name>Rota {num_rota} caminhão {caminhao}</name>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc</styleUrl>\n"
                              "<LineString>\n"
                              "<tessellate>1</tessellate>\n"
                              "<coordinates>\n")

                    # Variável que permite que o primeiro ponto da tupla seja escrito, para que a rota fique correta
                    # Isso é feito pois as tuplas da rota vem da seguinte maneira:
                    # [(1, 2), (2, 3), (3, 4), (4, 5)]
                    primeiro_pnt = True

                    # Em cada rota, percorre os pontos que a formam
                    for pnt in rota:

                        if util.grafo_cidade_simplificado.has_edge(pnt[0], pnt[1]):

                            # Escreve os detalhes da rota num arquivo txt
                            rua = util.grafo_cidade_simplificado[pnt[0]][pnt[1]][0]["rua"]

                            if rua.nome is not None and rua.nome is not "":

                                # TODO VOLTAR
                                # txt.write(rua.nome + " -> ")
                                pass

                        txt.write(f"{pnt} -> ")

                        if primeiro_pnt:

                            arq.write(f"{util.pontos[pnt[0]].longitude}, {util.pontos[pnt[0]].latitude}, 0\n")
                            arq.write(f"{util.pontos[pnt[1]].longitude}, {util.pontos[pnt[1]].latitude}, 0\n")
                            primeiro_pnt = False
                        else:

                            arq.write(f"{util.pontos[pnt[1]].longitude}, {util.pontos[pnt[1]].latitude}, 0\n")

                    arq.write("</coordinates>\n"
                              "</LineString>\n"
                              "</Placemark>\n"
                              "<Placemark>\n"
                              "<name>DEPÓSITO</name>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc</styleUrl>\n"
                              "<Point>\n"
                              "<coordinates>\n"
                              f"{util.pontos[util.DEPOSITO].longitude}, {util.pontos[util.DEPOSITO].latitude}, 0\n"
                              "</coordinates>\n"
                              "</Point>\n"
                              "</Placemark>\n"
                              "</Document>\n"
                              "</kml>\n")"""

    def gera_resultados(self, front):

        # Arquivo com algumas informações gerais da coleta
        with open("saida/resultados/dados_coleta.txt", "w") as arq:

            arq.write("*** RESULTADOS OBTIDOS DA COLETA ***\n")

            # Resultados de lixo recolhido
            arq.write(
                f"\nQuantidade de lixo recolhido(kg): {front.individuals[0].quantidade_lixo} ({round((front.individuals[0].quantidade_lixo * 100) / util.quantidade_lixo_cidade)}%)")

            # Resultados sobre os parâmetros utilizados
            arq.write(f"\nNúmero de caminhões utilizados para a realização da coleta: {front.individuals[0].genome[0]}")
            arq.write(f"\nNúmero de agrupamentos realizados pelo mapa: {front.individuals[0].genome[1]}")

        # Para cada caminhão utilizado na coleta, gera um mapa com a rota a ser realizada por ele
        for caminhao, rotas_caminhao in front.individuals[0].rotas.items():

            # Percorre cada uma das rotas do caminhão para realizar o plot
            for num_rota, rota in enumerate(rotas_caminhao):

                # Abre os arquivos que irão descrever a rota do caminhão
                with open(f"saida/resultados/rotas/caminhao{caminhao}_rota_{num_rota}.kml", "w") as arq, \
                        open(f"saida/resultados/rotas/caminhao{caminhao}_rota_{num_rota}.txt", "w") as txt:

                    # Para o arquivo kml, o cabeçalho é padrão, muda somente o nome
                    arq.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                              "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n"
                              "<Document>\n"
                              f"<name>Rota {num_rota} caminhão {caminhao}</name>\n"
                              "<Style id=\"icon-1899-DB4436-nodesc-normal\">\n"
                              "<IconStyle>\n"
                              "<color>ff3644db</color>\n"
                              "<scale>1</scale>\n"
                              "<Icon>\n"
                              "<href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>\n"
                              "</Icon>\n"
                              "<hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>\n"
                              "</IconStyle>\n"
                              "<LabelStyle>\n"
                              "<scale>0</scale>\n"
                              "</LabelStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<Style id=\"icon-1899-DB4436-nodesc-highlight\">\n"
                              "<IconStyle>\n"
                              "<color>ff3644db</color>\n"
                              "<scale>1</scale>\n"
                              "<Icon>\n"
                              "<href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>\n"
                              "</Icon>\n"
                              "<hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>\n"
                              "</IconStyle>\n"
                              "<LabelStyle>\n"
                              "<scale>1</scale>\n"
                              "</LabelStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<StyleMap id=\"icon-1899-DB4436-nodesc\">\n"
                              "<Pair>\n"
                              "<key>normal</key>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc-normal</styleUrl>\n"
                              "</Pair>\n"
                              "<Pair>\n"
                              "<key>highlight</key>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc-highlight</styleUrl>\n"
                              "</Pair>\n"
                              "</StyleMap>\n"
                              "<Style id=\"line-1267FF-5000-nodesc-normal\">\n"
                              "<LineStyle>\n"
                              "<color>ffff6712</color>\n"
                              "<width>5</width>\n"
                              "</LineStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<Style id=\"line-1267FF-5000-nodesc-highlight\">\n"
                              "<LineStyle>\n"
                              "<color>ffff6712</color>\n"
                              "<width>7.5</width>\n"
                              "</LineStyle>\n"
                              "<BalloonStyle>\n"
                              "<text><![CDATA[<h3>$[name]</h3>]]></text>\n"
                              "</BalloonStyle>\n"
                              "</Style>\n"
                              "<StyleMap id=\"line-1267FF-5000-nodesc\">\n"
                              "<Pair>\n"
                              "<key>normal</key>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc-normal</styleUrl>\n"
                              "</Pair>\n"
                              "<Pair>\n"
                              "<key>highlight</key>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc-highlight</styleUrl>\n"
                              "</Pair>\n"
                              "</StyleMap>\n"
                              "<Placemark>\n"
                              f"<name>Rota {num_rota} caminhão {caminhao}</name>\n"
                              "<styleUrl>#line-1267FF-5000-nodesc</styleUrl>\n"
                              "<LineString>\n"
                              "<tessellate>1</tessellate>\n"
                              "<coordinates>\n")

                    # Variável que permite que o primeiro ponto da tupla seja escrito, para que a rota fique correta
                    # Isso é feito pois as tuplas da rota vem da seguinte maneira:
                    # [(1, 2), (2, 3), (3, 4), (4, 5)]
                    primeiro_pnt = True

                    # Em cada rota, percorre os pontos que a formam
                    for pnt in rota.rota:

                        if util.grafo_cidade_simplificado.has_edge(pnt[0], pnt[1]):

                            # Escreve os detalhes da rota num arquivo txt
                            rua = util.grafo_cidade_simplificado[pnt[0]][pnt[1]][0]["rua"]

                            if rua.nome is not None and rua.nome is not "":

                                txt.write(rua.nome + " -> ")

                        if primeiro_pnt:

                            arq.write(f"{util.pontos[pnt[0]].longitude}, {util.pontos[pnt[0]].latitude}, 0\n")
                            arq.write(f"{util.pontos[pnt[1]].longitude}, {util.pontos[pnt[1]].latitude}, 0\n")
                            primeiro_pnt = False
                        else:

                            arq.write(f"{util.pontos[pnt[1]].longitude}, {util.pontos[pnt[1]].latitude}, 0\n")

                    arq.write("</coordinates>\n"
                              "</LineString>\n"
                              "</Placemark>\n")

                    # Escreve a rota de ida
                    if rota.ida:

                        arq.write("<Placemark>\n"
                                  f"<name> Ida do depósito a Rota {num_rota} do caminhão {caminhao}</name>\n"
                                  "<styleUrl>#line-1267FF-5000-nodesc</styleUrl>\n"
                                  "<LineString>\n"
                                  "<tessellate>1</tessellate>\n"
                                  "<coordinates>\n")

                        primeiro_pnt = True

                        for ponto_ida in rota.ida:

                            if primeiro_pnt:

                                arq.write(f"{util.pontos[ponto_ida[0]].longitude}, {util.pontos[ponto_ida[0]].latitude}, 0\n")
                                arq.write(f"{util.pontos[ponto_ida[1]].longitude}, {util.pontos[ponto_ida[1]].latitude}, 0\n")
                                primeiro_pnt = False
                            else:

                                arq.write(f"{util.pontos[ponto_ida[1]].longitude}, {util.pontos[ponto_ida[1]].latitude}, 0\n")

                        arq.write("</coordinates>\n"
                                  "</LineString>\n"
                                  "</Placemark>\n")

                    # Escreve a rota de volta
                    if rota.volta:

                        arq.write("<Placemark>\n"
                                  f"<name> Volta da Rota {num_rota} do caminhão {caminhao} ao depósito</name>\n"
                                  "<styleUrl>#line-1267FF-5000-nodesc</styleUrl>\n"
                                  "<LineString>\n"
                                  "<tessellate>1</tessellate>\n"
                                  "<coordinates>\n")

                        primeiro_pnt = True

                        for ponto_volta in rota.volta:

                            if primeiro_pnt:

                                arq.write(f"{util.pontos[ponto_volta[0]].longitude}, {util.pontos[ponto_volta[0]].latitude}, 0\n")
                                arq.write(f"{util.pontos[ponto_volta[1]].longitude}, {util.pontos[ponto_volta[1]].latitude}, 0\n")
                                primeiro_pnt = False
                            else:

                                arq.write(f"{util.pontos[ponto_volta[1]].longitude}, {util.pontos[ponto_volta[1]].latitude}, 0\n")

                        arq.write("</coordinates>\n"
                                  "</LineString>\n"
                                  "</Placemark>\n")

                    arq.write("<Placemark>\n"
                              "<name>DEPÓSITO</name>\n"
                              "<styleUrl>#icon-1899-DB4436-nodesc</styleUrl>\n"
                              "<Point>\n"
                              "<coordinates>\n"
                              f"{util.pontos[util.DEPOSITO].longitude}, {util.pontos[util.DEPOSITO].latitude}, 0\n"
                              "</coordinates>\n"
                              "</Point>\n"
                              "</Placemark>\n"
                              "</Document>\n"
                              "</kml>\n")
