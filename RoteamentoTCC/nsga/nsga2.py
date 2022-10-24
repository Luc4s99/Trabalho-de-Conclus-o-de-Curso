"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Thales Otávio
Link do GitHub: https://github.com/thalesorp/NSGA-II

E também possui partes desenvolvidas e baseadas em código desenvolvido por Mateus Soares
Link do GitHub: https://github.com/MateusSoares/Wireless-Access-Point-Optimization
"""
import copy
from sys import maxsize
import random

import networkx as nx

import RoteamentoTCC.util as util

# Importando métodos úteis da classe população
from RoteamentoTCC.nsga.population import Population

from sklearn.preprocessing import MinMaxScaler


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

        # Depende da forma que será feita a mutação
        # self.genotype_mutation_probability = 0.5

        # Inicializacao da população
        self.population = Population(max_caminhoes, min_clusters, max_clusters)

        # Indica qual geração o algoritmo está executando
        self.geracao = 1

    # Método principal que executa o NSGA-II
    def run(self):

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

            print(f"    -> Geração {i + 1}")

            # Realiza a união entre as duas populações
            # A população agora tem seu tamanho completo
            self.population.union(offspring_population)

            # Separa a população em fronteiras, onde cada fronteira tem populações
            fronts = self.fast_non_dominated_sort()

            # Como as fronteiras são ordenadas pelos melhores indivíduos
            # A primeira fronteira sempre terá as populações com os melhores indivíduos
            best_front = fronts[0]

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

            # Obtém a nova população Pt para a continuação do loop
            self.population = next_population

            # Monta a nova população Qt para a continuação do loop
            offspring_population = self.usual_crossover()
            self.evaluate(offspring_population)

        return best_front

    # Função que avalia um indivíduo de acordo com as métricas propostas
    def evaluate_individual(self, individual):

        # Indica a porcentagem de lixo recolhida
        porcentagem_lixo_recolhido = 0

        # Armazena a variação de altitude
        variacao_altitude = 0

        # Inicializa a lista de pontos que o trajeto se iniciará em cada cluster
        individual.genome[2] = ([-1 for _ in range(individual.genome[1])])

        # Lista que representa o tempo gasto pelos caminhoes, a lista inicia com zero
        tempo_caminhoes = [0 for _ in range(individual.genome[0])]

        # Realiza o agrupamento dos pontos de acordo com o parâmetro do indivíduo
        pontos_clusterizados = util.k_means(individual.genome[1])

        # Armazena a distribuição dos pontos em cluster do individuo
        individual.pontos_clusterizados = pontos_clusterizados

        # Indica qual caminhão será analisado
        vez = 0

        # Lista que indica os pontos onde o lixo já foi recolhido
        recolhido = []

        # Realiza o processamento de rota para cada um dos clusters
        for id_cluster, cluster in pontos_clusterizados.items():

            distancia_cluster = 0
            quantidade_lixo_cluster = 0

            # Termina a montagem do indivíduo, selecionando os pontos de onde começarão os trajetos nos clusters
            ponto_inicio = random.choice(cluster)

            individual.genome[2][id_cluster] = ponto_inicio

            # Primeiramente é montado um subgrafo com os pontos do cluster
            grafo_cluster = util.grafo_cidade_simplificado.subgraph(ponto.id for ponto in cluster).copy()

            # Verifica se o subgrafo é euleriano
            if not nx.is_eulerian(grafo_cluster):

                # Transforma em um grafo euleriano
                grafo_cluster = util.converte_grafo_euleriano(grafo_cluster)

            # Realiza a rota euleriana pelo grafo
            # Começa pelo ponto selecionado para início da rota
            rota = list(util.nx.eulerian_path(grafo_cluster, source=ponto_inicio.id))

            # Verifica se foi gerado algo na rota
            if len(rota) == 0:

                print("TAMANHO DA ROTA É ZERO!")

            else:

                # Calcula a ida do caminhão até o cluster
                distancia_cluster += nx.dijkstra_path_length(util.grafo_cidade_simplificado, rota[0][0], util.DEPOSITO)

                # Calcula a volta do caminhao ao depósito
                distancia_cluster += nx.dijkstra_path_length(util.grafo_cidade_simplificado,
                                                             rota[len(rota) - 1][0], util.DEPOSITO)

            # Percorre a rota, calcula o tempo e verifica o lixo coletado
            for pnt_coleta in rota:

                # Incrementa a distância percorrida na rua atual
                distancia_cluster += grafo_cluster[pnt_coleta[0]][pnt_coleta[1]][0]["weight"]

                # Verifica se esses pontos já não foram visitados por esse indivíduo e coleta
                if pnt_coleta[0] not in recolhido:

                    quantidade_lixo_cluster += util.pontos_otimizados[pnt_coleta[0]].quantidade_lixo
                    recolhido.append(pnt_coleta[0])

                if pnt_coleta[1] not in recolhido:
                    quantidade_lixo_cluster += util.pontos_otimizados[pnt_coleta[1]].quantidade_lixo
                    recolhido.append(pnt_coleta[1])

                # Incrementa a variação de altitude
                variacao_altitude += (util.pontos_otimizados[pnt_coleta[0]].altitude - util.pontos_otimizados[pnt_coleta[1]].altitude) / grafo_cluster[pnt_coleta[0]][pnt_coleta[1]][0]["weight"]

                # Verifica se a carga do veículo foi ultrapassada
                if quantidade_lixo_cluster > util.CAPACIDADE_CAMINHAO:

                    break

            # Incrementa a quantidade de lixo total com a quantidade do cluster
            porcentagem_lixo_recolhido += quantidade_lixo_cluster

            # Converte a distância para tempo(levando em conta que o caminhão coleta a 5km/h) em minutos
            # E incrementa no tempo do caminhão correspondente
            if vez == len(tempo_caminhoes):

                vez = 0

            # Realiza uma simulação do tempo gasto pelo caminhão para recolher o lixo com base na distância
            # tempo_caminhoes[vez] += (distancia_cluster * 60) / 5000
            tempo_caminhoes[vez] += distancia_cluster
            vez += 1

        # Retorna a soma de tempo dos caminhões: Métrica de minimização
        # A porcentagem de lixo não recolhida: Métrica de minimização
        # A variação de altitude: Métrica de minimização
        # A quantidade de caminhões = |(lixo total / capacidade caminhao) - quantidade gerada|: Minimização
        return [sum(tempo_caminhoes), round(100 - (porcentagem_lixo_recolhido * 100) / util.quantidade_lixo_cidade),
                variacao_altitude, abs((util.quantidade_lixo_cidade / util.CAPACIDADE_CAMINHAO) - individual.genome[0])]

    # Função que avalia os indivíduos gerados na população
    def evaluate(self, population):

        # Iterando sobre todos os indivíduos gerados na população
        for individual in population.individuals:

            # Verifica se o indivíduo já foi avaliado antes
            if not individual.solutions:

                # Avalia e retorna as soluções não normalizadas
                individual.non_normalized_solutions = self.evaluate_individual(individual)

        # Instancia o escalar para fazer a normalização MIN/MAX dos dados
        escalar = MinMaxScaler()

        # Percorre os indivíduos
        for individual in population.individuals:

            # Para a normalização os dados precisam estar no formato de uma matriz
            matrix_normalizar = [[individual.non_normalized_solutions[0]], [individual.non_normalized_solutions[1]],
                                 [individual.non_normalized_solutions[2]], [individual.non_normalized_solutions[3]]]

            # Realiza a normalização dos dados do indivíduo em questão
            escalar.fit(matrix_normalizar)
            normalizado = escalar.transform(matrix_normalizar)

            # Insere o resultado nas soluções normalizadas do indivíduo
            individual.solutions = [normalizado[0][0], normalizado[1][0], normalizado[2][0], normalizado[3][0]]

        # Usado para calibrar, depois descomentar e plotar os gráficos do hypervolume
        # self.add_population_to_file(population)

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

                        # Se ele domina, o outro indivíduo é inserido na lista que indivíduos dominados por ele
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
                population.individuals[0].crowding_distance = maxsize
                population.individuals[last_individual_index].crowding_distance = maxsize

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

    def crowded_comparison(self, individual_A, individual_B):
        """Return the best individual according to the crowded comparison operator
        in NSGA-II paper"""

        if ((individual_A.rank < individual_B.rank)
                or ((individual_A == individual_B)
                    and (individual_A.crowding_distance > individual_B.crowding_distance))):
            return individual_A
        return individual_B

    def sort_by_crowded_comparison(self, population):
        """Sort "population" with crowded comparison operator. Bubble sort"""

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
        if primeiro_candidato.solutions[1] < segundo_candidato.solutions[1]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1

        # Verifica qual deles possui a menor variação de altitude
        if primeiro_candidato.solutions[2] < segundo_candidato.solutions[2]:

            pontuacao_primeiro_candidato += 1
        else:

            pontuacao_segundo_candidato += 1

        # E por fim verifica qual possui a quantidade de caminhões mais otimizada
        if primeiro_candidato.solutions[3] < segundo_candidato.solutions[3]:

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

        if random.random() < 0.5:

            child1_genome.append(pai1.genome[0])
            child1_genome.append(pai2.genome[1])
            child1_genome.append(pai2.genome[2])

            child2_genome.append(pai2.genome[0])
            child2_genome.append(pai1.genome[1])
            child2_genome.append(pai1.genome[2])

            child1_genome = self.mutation(child1_genome, pai2.pontos_clusterizados)
            child2_genome = self.mutation(child2_genome, pai1.pontos_clusterizados)
        else:

            child2_genome.append(pai1.genome[0])
            child2_genome.append(pai2.genome[1])
            child2_genome.append(pai2.genome[2])

            child1_genome.append(pai2.genome[0])
            child1_genome.append(pai1.genome[1])
            child1_genome.append(pai1.genome[2])

            child1_genome = self.mutation(child1_genome, pai1.pontos_clusterizados)
            child2_genome = self.mutation(child2_genome, pai2.pontos_clusterizados)

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

    # Método de crossover entre dois indivíduos
    """def simulated_binary_crossover(self, parent1, parent2):

        # Distribution index. "nc" in NSGA-II paper
        crossover_constant = self.crossover_constant

        # Lista que representa o genoma das proles
        child1_genome = list()
        child2_genome = list()

        for j in range(self.genotype_quantity):

            # Each genotype has a 50% chance of changing its value
            # TODO: This should be removed when dealing with one-dimensional solutions
            '''
            if (random.random() > 0.5) and (self.genotype_quantity != 1):
                # In this case, the children will get the value of the parents
                child1_genome.append(parent1.genome[j])
                child2_genome.append(parent2.genome[j])
                continue
            '''

            # "y1" is the lowest value between parent1 and parent2. "y2" gets the other value
            if parent1.genome[j] < parent2.genome[j]:
                y1 = parent1.genome[j]
                y2 = parent2.genome[j]
            else:
                y1 = parent2.genome[j]
                y2 = parent1.genome[j]

            # EPS: precision error tolerance, its value is 1.0e-14 (global constant)
            eps = 0.000000000000010 #1.0e-14
            # If the value in parent1 is not the same of parent2
            if abs(parent1.genome[j] - parent2.genome[j]) > eps:
                # Lower and upper limit of genotype of an individual
                lower_bound = self.genome_min_value
                upper_bound = self.genome_max_value

                u = random.random()

                # Calculation of the first child
                beta = 1 + (2 / (y2 - y1)) * min((y1 - lower_bound), (upper_bound - y2))
                alpha = 2 - pow(beta, -(crossover_constant + 1))
                if u <= (1/alpha):
                    beta_bar = pow(alpha * u, 1/(crossover_constant + 1))
                else:
                    beta_bar = pow(1/(2 - (alpha * u)), 1/(crossover_constant + 1))
                child1_genotype = 0.5 * ((y1 + y2) - beta_bar * (y2 - y1))

                # Calculation of the second child
                beta = 1 + (2 / (y2 - y1)) * min((y1 - lower_bound), (upper_bound - y2))
                alpha = 2 - pow(beta, -(crossover_constant + 1))
                if u <= (1/alpha):
                    beta_bar = pow(alpha * u, 1/(crossover_constant + 1))
                else:
                    beta_bar = pow(1/(2 - (alpha * u)), 1/(crossover_constant + 1))
                child2_genotype = 0.5 * ((y1 + y2) + beta_bar * (y2 - y1))

                child1_genome.append(child1_genotype)
                child2_genome.append(child2_genotype)

            # The paper is not very clear about this, but i assume, in the equation of beta (not beta_bar),
            # y2 and y1, since they could not have been calculated yet, refer to the parents
            # So, if both parents are equal at the specified variable, the divisor would be zero
            # In this case, the children should have the same value as the parents. 
            else:
                child1_genome.append(parent1.genome[j])
                child2_genome.append(parent2.genome[j])

        return child1_genome, child2_genome"""

    # Método que realiza mutação no genoma do indivíduo
    def mutation(self, genome, pontos_cluster):

        # Verifica se a mutação irá ocorrer
        if random.uniform(0, 1) > self.mutation_rate:

            # Se a mutação não for ocorrer, então o genoma é apenas retornado sem nenhuma modificação
            return genome

        # Verifica se será o primeiro ou o segundo gene a sofrer a mutação
        # Atualmente é utilizada uma mutação bem simples, onde apenas se soma +1 no gene selecionado
        if random.random() < 0.5:

            genome[0] += 1
        else:

            genome[1] += 1

        # Percorre os pontos de início dos cluster para aplicar mutação
        for i, ponto_inicio in enumerate(genome[2]):

            if random.random() < 0.5:

                genome[2][i] = random.choice(pontos_cluster[i])

        return genome

    # Utils
    def _show_fronts(self, fronts):
        """Show all fronts"""

        result = "FRONTS:\n"

        i = 0
        for front in fronts:
            i += 1
            result += "FRONT NUMBER " + str(i) + ":\n"

            j = 0
            for individual in front.individuals:
                j += 1
                result += (" [" + str(j) + "] " + str(individual) + "\n")

            result += "\n"

        print(result)

    def _show_population(self, population):
        """Show all fronts"""

        result = "# [FRONT INDEX] [NAME] [GENOME LIST] [SOLUTIONS LIST] [NONDOMINATED RANK] [CROWDING DISTANCE]\n"

        j = 0
        for individual in population.individuals:
            j += 1
            result += str(j) + " " + str(individual) + "\n"

        return result
