"""

Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Thales Otávio
Link do GitHub: https://github.com/thalesorp/NSGA-II

E também possui partes desenvolvidas e baseadas em código desenvolvido por Mateus Soares
Link do GitHub: https://github.com/MateusSoares/Wireless-Access-Point-Optimization

Este projeto também utiliza dados obtidos pelo projeto Open Street Map
Link: https://www.openstreetmap.org/about
"""

import sys
import random

from .individual import Individual


class Population:

    def __init__(self, max_caminhoes, min_clusters, max_clusters):

        # Semente para geração de valores aleatórios
        random.seed()

        self.size = 0

        self.individuals = list()

        self.fronts = list()

        self.max_caminhoes = max_caminhoes

        self.min_clusters = min_clusters

        self.max_clusters = max_clusters

    # Método que gera os indivíduos da população
    def initiate(self, n_individuals):

        # Itera sobre o número de indivíduos que precisa ser gerado
        for _ in range(n_individuals):

            # Lista que representa o genoma do indivíduo
            # Cada posição da lista define o número de caminhões a ser utilizado e a quantidade de cluster
            genome = list()

            # Gera a quantidade de caminhões que serão utilizados para realizar a coleta
            genome.append(random.randint(1, self.max_caminhoes))

            # Gera a quantidade de cluster que serão gerados para a cidade
            genome.append(random.randint(self.min_clusters, self.max_clusters))

            # Inicia a lista com os pontos de início de cada cluster
            genome.append(list())

            self.new_individual(genome)

    # Calcula a quantidade de lixo de um determinado indivíduo carrega
    def calcula_quantidade_lixo(self, genoma):

        quantidade_lixo = 0

        # Verifica se o genoma está vazio, se estiver a quantidade de lixo é 0
        if len(genoma) != 0:

            # Percorre todos os genes no indivíduo, cada gene é composto por uma tupla com dois pontos
            for gene in genoma:

                quantidade_lixo += gene[0].quantidade_lixo + gene[1].quantidade_lixo

        return quantidade_lixo

    # Cria um novo indivíduo e insere na população
    def new_individual(self, genome):

        self.insert(Individual(genome))

    # Insere um indivíduo na população
    def insert(self, individual):

        self.individuals.append(individual)
        self.size += 1

    def delete_individual(self, individual):
        """Delete "individual" from population"""

        self.individuals.remove(individual)
        self.size -= 1

    # Realiza a união entre uma população e outra
    def union(self, population):

        for individual in population.individuals:
            self.insert(individual)

    # Reseta dados sobre as fronteiras e também das informações do domination sort dos indivíduos
    def reset_fronts(self):

        for individual in self.individuals:

            individual.domination_count = 0
            individual.dominated_by = list()

        self.fronts = list()

    def new_front(self):

        self.fronts.append([])

    # Retorna um indivíduo aleatório da população
    def get_random_individual(self):

        index = random.randint(0, self.size-1)

        return self.individuals[index]

    def add_to_front(self, index, individual):

        self.fronts[index].append(individual)

    def get_last_front_index(self):
        """Retun the index of last front"""

        return len(self.fronts)-1

    def add_to_last_front(self, individual):

        self.fronts[self.get_last_front_index()].append(individual)

    def get_last_front(self):

        return self.fronts[len(self.fronts)-1]

    def delete_individual_from_last_front(self, individual):
        """Deletes the individual from front AND from individuals list"""

        # Deleting from last front the individual with index = "index"
        last_front = self.get_last_front()
        index = last_front.index(individual)
        del last_front[index]

        self.delete_individual(individual)

    def delete_last_front(self):

        last_front = self.get_last_front()

        for individual in last_front:

            self.delete_individual(individual)

        self.fronts.remove(last_front)

    # Crowding Distance utils
    def get_neighbour(self, individual_genome, front_index, genome_index):
        """Return the left and right neighbour values of "individual_genome\""""

        genome_list = list()

        for individual in self.fronts[front_index]:
            genome_list.append(individual.genome[genome_index])

        genome_list.sort()

        individual_genome_index = genome_list.index(individual_genome)

        # Usually, the value is as described bellow
        left_neighbour_index = individual_genome_index - 1
        right_neighbour_index = individual_genome_index + 1

        # But when isn't, then it's checked the cases when there's no neighbour on one side
        if individual_genome_index == 0:
            # When it happens, the closest neighbour it's himself
            left_neighbour_index = 0
        if individual_genome_index == (len(genome_list)-1):
            right_neighbour_index = (len(genome_list)-1)

        return genome_list[left_neighbour_index], genome_list[right_neighbour_index]

    # Retorna o maior e menor valor da solução de vizinhos
    def get_extreme_neighbours(self, solution_index):

        genome_list = list()

        for individual in self.individuals:
            genome_list.append(individual.solutions[solution_index])

        return min(genome_list), max(genome_list)

    # Utils
    def _show_individuals(self):
        """Show the values of each individual of population"""

        result = "INDIVIDUALS:\n"
        i = 1
        for individual in self.individuals:
            result += (" [" + str(i) + "] " + str(individual) + "\n")
            i += 1

        print(result)

    def _show_front(self, front_index):
        """Show only front with "front_index\""""

        result = "FRONT:\n"
        j = 0
        for individual in self.fronts[front_index]:
            j += 1
            result += (" [" + str(j) + "] " + str(individual) + "\n")

        result += "\n"

        print(result)

    def _show_fronts_simple(self):
        """Show all fronts"""

        result = "FRONTS:\n"

        i = 0
        for front in self.fronts:
            i += 1
            result += "FRONT NUMBER " + str(i) + ":\n"

            j = 0
            for individual in front:
                j += 1
                result += (" [" + str(j) + "] " + individual.__str_genome__() + "\n")

            result += "\n"

        print(result)

    def _show_general_domination_info(self):
        """Show all data of population"""

        for individual in self.individuals:
            sys.stdout.write("  Individual: " + str(individual)
                             + "\tdomination count: " + str(individual.domination_count)
                             + "\tdominated by this: ")
            for dominated_individual in individual.dominated_by:
                sys.stdout.write(str(dominated_individual.name) + ", ")
            print("")
        print("")

    def _show_fronts_with_crowding_distance(self):
        """Show all fronts"""

        i = 1
        for front in self.fronts:
            sys.stdout.write("Front " + str(i) + ": ")
            i += 1
            for individual in front:
                sys.stdout.write(str(individual)+ ".CD: "
                                 + str(individual.crowding_distance) + ", ")
            print("")
