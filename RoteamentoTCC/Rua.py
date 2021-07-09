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

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_latitude(self, latitude):
        self.latitude = latitude

    def get_latitude(self):
        return self.latitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def get_longitude(self):
        return self.longitude

    def set_quantidade_lixo(self, quantidade_lixo):
        self.quantidade_lixo = quantidade_lixo

    def get_quantidade_lixo(self):
        return self.quantidade_lixo

    def set_pontos(self, pontos):
        self.pontos = pontos

    def get_pontos(self):
        return self.pontos

    # Insere um ponto na lista de pontos que formam a rua
    def insere_ponto(self, ponto):
        self.pontos.append(ponto)
