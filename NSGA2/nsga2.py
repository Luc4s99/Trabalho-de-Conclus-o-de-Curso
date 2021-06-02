# Implementação baseada no algoritmo de Thales Pinto e no artigo de Kalyanmoy Deb

import random
from .util import Util


# Classe que descreve o algoritmo do NSGA-II
class Nsga2:

    # Construtor da classe
    def __init__(self, num_geracoes, tam_populacao):

        self.num_geracoes = num_geracoes

        self.tam_populacao = tam_populacao

        self.populacao = Util.inicia_populacao()

    # Método que inicia o NSGA-II
    def run(self):

        pass
