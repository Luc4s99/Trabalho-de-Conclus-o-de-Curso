# Classe que define um ponto do mapa

import itertools


class Ponto:

    # Controla o valor assumido pelo label do ponto
    # O label é o que será printado na plotagem do grafo para identificar o ponto
    novo_label = itertools.count()

    def __init__(self, gera_label=True):

        # Identificador único do ponto no grafo da cidade
        self.id = -1

        # Latitude que localiza o ponto
        self.latitude = 0

        # Longitude que localiza o ponto
        self.longitude = 0

        # Lista dos pontos aos quais este ponto tem ligação
        self.pontos_vizinhos = []

        # Gera um label somente para os pontos que forem mapeados
        # Isso será usado depois para verificar quantos pontos foram mapeados
        if gera_label:
            # Label que identifica o ponto
            self.label = next(self.novo_label)

    def realiza_ligacao(self, ponto):
        self.pontos_vizinhos.append(ponto)

    def retorna_coordenadas(self):
        return tuple([float(self.latitude), float(self.longitude)])
