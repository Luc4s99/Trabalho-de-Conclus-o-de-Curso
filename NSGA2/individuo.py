class Individuo:

    def __init__(self):

        # Cromossomo que define a solução do individuo
        self.cromossomo = list()

        # Quantidade de individuos que domina este individuo
        self.cont_dominacao = 0

        # Lista que contem os individuos dominados por esse individuo
        self.dominados = list()

        # Rank para classificacao do individuo
        self.rank = None

        self.crowding_distance = None
