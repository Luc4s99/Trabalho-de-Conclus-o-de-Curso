# Classe que define uma rua do mapa

class Rua:

    def __init__(self):

        # Identificador único da rua
        self.id = 0

        # Latitude que localiza a rua
        self.latitude = 0

        # Longitude que localiza a rua
        self.longitude = 0

        # Quantidade de lixo que aquela rua possui
        self.quilosLixo = 0

        # Lista que indica os pontos que formam a rua
        self.pontos = []

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id
