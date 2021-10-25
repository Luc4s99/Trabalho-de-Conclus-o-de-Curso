# Classe que define uma rua do mapa

class Rua:

    def __init__(self):

        # Identificador único da rua
        self.id = 0

        # Latitude que localiza a rua
        self.latitude = 0

        # Longitude que localiza a rua
        self.longitude = 0

        # Quantidade de lixo em quilos que aquela rua possui
        self.quantidade_lixo = 0

        # Lista que indica os pontos que formam a rua
        self.pontos = []

        # Nome da rua
        self.nome = ""

    # Insere um ponto na lista de pontos que formam a rua
    def insere_ponto(self, ponto):
        self.pontos.append(ponto)
