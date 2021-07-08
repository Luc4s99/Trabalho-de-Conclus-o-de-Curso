# Classe que define um ponto do mapa

class Ponto:

    def __init__(self):

        # Identificador único do ponto
        self.id = 0

        # Latitude que localiza o ponto
        self.latitude = 0

        # Longitude que localiza o ponto
        self.longitude = 0

    # Métodos getters e setters
    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_latitude(self):
        return self.latitude

    def set_latitude(self, latitude):
        self.latitude = latitude

    def get_longitude(self):
        return self.longitude

    def set_longitude(self, longitude):
        self.longitude = longitude
