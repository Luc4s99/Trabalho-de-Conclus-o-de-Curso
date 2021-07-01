# Classe que define um ponto do mapa

class Ponto:

    def __init__(self):

        # Identificador único do ponto
        self.id = 0

        # Latitude que localiza o ponto
        self.latitude = 0

        # Longitude que localiza o ponto
        self.longitude = 0

        # Demanda que aquele ponto oferece, neste caso a quantidade de lixo
        self.demanda = 0
