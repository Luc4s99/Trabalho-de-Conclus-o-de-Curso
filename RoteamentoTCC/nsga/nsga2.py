"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Thales Otávio
Link do GitHub: https://github.com/thalesorp/NSGA-II

E também possui partes desenvolvidas e baseadas em código desenvolvido por Mateus Soares
Link do GitHub: https://github.com/MateusSoares/Wireless-Access-Point-Optimization
"""

from sys import maxsize
import random
import RoteamentoTCC.util as util
import numpy as np

# Importando métodos úteis da classe população
from RoteamentoTCC.nsga.population import Population


# Classe que define o algoritmo NSGA-II
class NSGA2:

    # PARÂMETROS
    # generations: Número de gerações que o algortimo genético irá executar
    # population_size: Quantidade de indivíduos por população
    # genome_values: Lista de valores que o genoma de um indivíduo pode ter
    # mutation_rate: Probabilidade de ocorrer uma mutação em um indivíduo
    # crossover_rate: Probabilidade de ocorrer crossover
    # truck_capacity: Capacidade em KG de carga do caminhão
    # pontos do grafo que será analisado
    def __init__(self, generations, population_size, genome_values, mutation_rate,
                 crossover_rate, truck_capacity, graph_points):

        self.generations = generations

        self.population_size = population_size

        self.genome_values = genome_values

        self.crossover_rate = crossover_rate

        self.mutation_rate = mutation_rate

        self.truck_capacity = truck_capacity

        self.graph_points = graph_points

        self.front = []

        # Depende da forma que será feita a mutação
        # self.genotype_mutation_probability = 0.5

        # Inicializacao da população
        self.population = Population(genome_values, truck_capacity)

        # Indica qual geração o algoritmo está executando
        self.geracao = 1

    # Método principal que executa o NSGA-II
    def run(self):

        # Criando a população inicial Pt
        self.population.initiate(self.population_size // 2)

        # Avalia os indivíduos gerados na população
        self.evaluate(self.population)

        # Armazena as fronteiras selecionadas pela ordenação de dominância
        fronts = self.fast_non_dominated_sort()

        # População originada do cruzamento dos indivíduos da primeira metade da população
        offspring_population = self.usual_crossover()

        self.evaluate(offspring_population)

        # Variável que irá armazenar a melhor fronteira
        best_front = None

        # Passa pelo número de gerações definido
        for i in range(self.generations):

            # "Rt" population: union between "Pt" and "Qt", now with size of "2N"
            self.population.union(offspring_population)

            # "F" on NSGA-II paper
            fronts = self.fast_non_dominated_sort()

            best_front = fronts[0]

            self.crowding_distance_assignment(fronts)

            # "Pt+1" population
            next_population = self.new_population()

            i = 0
            while (next_population.size + fronts[i].size) <= self.population_size:
                next_population.union(fronts[i])
                i += 1

            # Sort(Fi, <n)
            self.sort_by_crowded_comparison(fronts[i])

            # "Pt+1" = "Pt+1" union fronts[i][1 : "N" - sizeof("Pt+1")]
            amount_to_insert = self.population_size - len(next_population.individuals)
            fronts[i].individuals = fronts[i].individuals[:amount_to_insert]
            next_population.union(fronts[i])

            self.population = next_population

            # Make new offspring population. "Qt+1" on NSGA-II paper
            offspring_population = self.crossover()
            self.evaluate(offspring_population)

        return best_front

    # Função que avalia um indivíduo de acordo com as métricas propostas
    def evaluate_individual(self, individual):

        # Nesta função serão verificadas 3 métricas do indivíduo
        # 1ª: Distância total do indivíduo, 2ª: Número de ruas, 3ª: Número de ruas conectadas
        # Será retornada uma lista com os três valores em ordem
        return util.calcula_metricas(individual)

    # Função que avalia os indivíduos gerados na população
    def evaluate(self, population):

        # Iterando sobre todos os indivíduos gerados na população
        for individual in population.individuals:

            # Verifica se o indivíduo já foi avaliado antes
            if not individual.solutions:

                # Avalia e retorna as soluções não normalizadas
                individual.non_normalized_solutions = self.evaluate_individual(individual)

        # Normalização de dados MIN MAX
        # Obtem os maiores valores dos indivíduos durante suas avaliações
        distancia_max = np.max([i.non_normalized_solutions[0] for i in population.individuals])
        ruas_max = np.max([i.non_normalized_solutions[1] for i in population.individuals])
        ruas_conectadas_max = np.max([i.non_normalized_solutions[2] for i in population.individuals])

        # Obtem os menores valores dos indivíduos durante suas avaliações
        distancia_min = np.min([i.non_normalized_solutions[0] for i in population.individuals])
        ruas_min = np.min([i.non_normalized_solutions[1] for i in population.individuals])
        ruas_conectadas_min = np.min([i.non_normalized_solutions[2] for i in population.individuals])

        # Realiza a normalização das soluções para que seus valores não sejam tão discrepantes
        # O método de normalização utilizada foi o Min-Max, que retorna valores entre [0-1]
        for individual in population.individuals:

            # x' = (xi - xmin) / (xmax - xmin)
            individual.solutions.append(
                (individual.non_normalized_solutions[0] - distancia_min) / (distancia_max - distancia_min))

            individual.solutions.append(
                (individual.non_normalized_solutions[1] - ruas_min) / (ruas_max - ruas_min))

            individual.solutions.append(
                (individual.non_normalized_solutions[2] - ruas_conectadas_min) /
                (ruas_conectadas_max - ruas_conectadas_min))

        # Usado para calibrar, depois descomentar e plotar os gráficos do hypervolume
        # self.add_population_to_file(population)

        self.geracao += 1

    # Retorna uma nova população vazia
    def new_population(self):

        return Population(self.genome_values, self.truck_capacity)

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

        while len(fronts[i].individuals) > 0:
            fronts.append(self.new_population())
            for individual in fronts[i].individuals:
                for dominated_individual in individual.dominated_by:
                    dominated_individual.domination_count -= 1

                    # Now if this dominated individual aren't dominated by anyone, insert into next front
                    if dominated_individual.domination_count == 0:

                        # "+1" becasue "i" is index value, and rank starts from 1 and not 0
                        # "+1" because the rank it's for the next front
                        dominated_individual.rank = i+2
                        fronts[len(fronts)-1].insert(dominated_individual)
            i += 1

        # Deleting empty last front created in previously loops
        del fronts[len(fronts)-1]

        return fronts

    def crowding_distance_assignment(self, fronts):

        for population in fronts:

            last_individual_index = len(population.individuals)-1

            # Reseting this value because it's a new generation
            for individual in population.individuals:
                individual.crowding_distance = 0

            genome_index = 0
            for genome_index in range(self.genotype_quantity):

                # Sorting current population (front) according to the current objective (genome)
                population.individuals.sort(key=lambda x: x.genome[genome_index])

                # The first and last individuals of current population (front) receive "infinite"
                population.individuals[0].crowding_distance = maxsize
                population.individuals[last_individual_index].crowding_distance = maxsize

                min_value, max_value = population.get_extreme_neighbours(genome_index)

                # Calculating the crowding distance of each objective (genome) of all individuals
                for i in range(1, last_individual_index):
                    right_neighbour_value = population.individuals[i+1].genome[genome_index]
                    left_neighbour_value = population.individuals[i-1].genome[genome_index]

                    # population.individuals[i].crowding_distance += ((right_neighbour_value - left_neighbour_value) / (max_value - min_value))
                    if (max_value - min_value) == 0:
                        # TODO: warning: IN CROWDING DISTANCE: division by zero!
                        #print("IN CROWDING DISTANCE: division by zero!")
                        population.individuals[i].crowding_distance += ((right_neighbour_value - left_neighbour_value) / 1)
                    else:
                        population.individuals[i].crowding_distance += ((right_neighbour_value - left_neighbour_value) / (max_value - min_value))

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

        for i in range(len(population.individuals)-2):

            worst = population.individuals[i]

            for j in range(1, len(population.individuals)-i):

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
        # Primeiro verifica qual dos dois possui a menor distância
        if primeiro_candidato.solutions[0] < segundo_candidato.solutions[0]:

            pontuacao_primeiro_candidato += 1
        elif primeiro_candidato.solutions[0] > segundo_candidato.solutions[0]:

            pontuacao_segundo_candidato += 1

        # Depois verifica qual possui o maior número de ruas utilizadas
        if primeiro_candidato.solutions[0] > segundo_candidato.solutions[0]:

            pontuacao_primeiro_candidato += 1
        elif primeiro_candidato.solutions[0] < segundo_candidato.solutions[0]:

            pontuacao_segundo_candidato += 1

        # Por último verifica qual possui o maior número de ruas conectadas
        if primeiro_candidato.solutions[0] > segundo_candidato.solutions[0]:

            pontuacao_primeiro_candidato += 1
        elif primeiro_candidato.solutions[0] < segundo_candidato.solutions[0]:

            pontuacao_segundo_candidato += 1

        if pontuacao_primeiro_candidato > pontuacao_segundo_candidato:

            return primeiro_candidato

        return segundo_candidato

    def crossover(self):
        """Create a offspring population using the simulated binary crossover (SBX)
        and the binary tournament selection according to the crowded comparison operator"""

        genomes_list = list()

        # Getting the quantity of individuals that are needed to create
        # TODO: This value MUST BE even
        amount_to_create = self.population_size

        # "step = 2" because each iteration generates two children
        for i in range(0, amount_to_create, 2):

            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()

            # Checking if crossover will or not be made
            if random.random() > self.crossover_rate:
                # When crossover isn't made, the children will be a clone of the parents
                child1_genome = parent1.genome
                child2_genome = parent2.genome
            else:
                child1_genome, child2_genome = self.simulated_binary_crossover(parent1, parent2)

            genomes_list.append(child1_genome)
            genomes_list.append(child2_genome)

        # Creating the offspring population
        offspring_population = self.new_population()

        # Adding the new children on that population
        for child_genome in genomes_list:
            offspring_population.new_individual(self.mutation(child_genome))

        return offspring_population

    # Seleciona os pais para a realização do crossover e geração dos filhos
    def usual_crossover(self):

        genomes_list = list()

        # O loop conta de 2 em 2 pois cada iteração gera 2 indivíduos
        for _ in range(0, self.population_size, 2):

            # Seleciona dois pais bons para realizarem o crossover
            parent1 = self.usual_tournament_selection()
            parent2 = self.usual_tournament_selection()

            child1_genome, child2_genome = self.simulated_binary_crossover(parent1, parent2)

            genomes_list.append(child1_genome)
            genomes_list.append(child2_genome)

        # Creating the offspring population
        offspring_population = self.new_population()

        # Adding the new children on that
        for child_genome in genomes_list:
            offspring_population.new_individual(self.mutation(child_genome))

        return offspring_population

    def simulated_binary_crossover(self, parent1, parent2):
        """Simulated binary crossover (SBX)"""

        # Distribution index. "nc" in NSGA-II paper
        crossover_constant = self.crossover_constant

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

        return child1_genome, child2_genome

    def mutation(self, genome):
        """Mutation method"""

        random.seed()

        value = random.random()
        value = random.uniform(0, 1)
        # Checking if mutation will or not occur
        if value > self.mutation_rate:
            # When mutation doesn't occur, nothing happens
            return genome

        for i in range(len(genome)):
            # Mutate that genotype
            if random.random() < self.genotype_mutation_probability:

                value = self.disturb_percent * genome[i]

                # Will it add or decrease?
                if random.random() < 0.5:
                    value = -value

                genome[i] = genome[i] + value

                # Making sure that it doesn't escape the bounds
                if genome[i] > self.genome_max_value:
                    genome[i] = self.genome_max_value
                elif genome[i] < self.genome_min_value:
                    genome[i] = self.genome_min_value

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
