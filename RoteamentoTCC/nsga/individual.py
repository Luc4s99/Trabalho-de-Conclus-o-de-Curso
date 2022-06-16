"""
Este código possui partes desenvolvidas ou baseadas em código desenvolvido por Thales Otávio
Link do GitHub: https://github.com/thalesorp/NSGA-II

E também possui partes desenvolvidas e baseadas em código desenvolvido por Mateus Soares
Link do GitHub: https://github.com/MateusSoares/Wireless-Access-Point-Optimization
"""


class Individual:

    id = 1

    def __init__(self, genome):

        self.name = "i~" + str(Individual.id)
        Individual.id += 1

        # Lista de pontos(Objeto Ponto) que descrevem o genoma do indivíduo
        self.genome = genome

        # List of solutions
        self.solutions = list()

        # Lista de soluções ainda não normalizadas
        self.non_normalized_solutions = list()

        # Quantity of individuals which dominate this individual
        self.domination_count = 0

        # List of individuals that are dominated by this individual
        self.dominated_by = list()

        self.rank = None

        self.crowding_distance = None

    # Verifica se um indivíduo domina outro
    def dominates(self, individual):

        first_half = True
        second_half = False

        # Compara todas as soluções do indivíduo atual com as do indivíduo passado por parâmetro
        for i, solution in enumerate(self.solutions):

            first_half = first_half and bool(solution <= individual.solutions[i])
            second_half = second_half or bool(solution < individual.solutions[i])

            i += 1

        return first_half and second_half

    def __str__(self):

        return (self.name
                + " " + self.__str_genome__()
                + " " + self.__str_solutions__()
                + " " + str(self.rank)
                + " " + self.__str_crowding_distance__()
                )

    def __str_genome__(self):

        if not self.genome:
            return "[]"

        return str(self.genome)

    def __str_solutions__(self):

        if not self.solutions:
            return "[]"

        result = "["

        for i in range(len(self.solutions) - 1):

            result += '%.6f' % (self.solutions[i]) + ", "

        result += '%.6f' % (self.solutions[-1]) + "]"

        return result

    def __str_crowding_distance__(self):

        if self.crowding_distance is None:
            return "-"

        return '%.4f' % self.crowding_distance

    def __str_dominated_by__(self):

        if not self.dominated_by:
            return "[]"

        dominated_by_size = len(self.dominated_by)

        if dominated_by_size > 1:
            result = "["
            for i in range(dominated_by_size - 1):
                result += str(self.dominated_by[i].name) + ", "
            result += str(self.dominated_by[-1].name) + "]"
        else:
            result = "[" + str(self.dominated_by[0].name) + "]"

        return result
