# Classe que define uma rua do mapa

class Rota:

    def __init__(self):

        # Rota de ida até a coleta do cluster
        self.ida = []

        # Rota de volta do cluster
        self.volta = []

        # Rotas quando o caminhão encher e precisar voltar para o depósito
        self.descarregamentos = []

        # Rota dentro do cluster
        self.rota = []

    def formata_rota_ida(self):

        if self.ida:

            rota_detalhada_formatada = []

            for i in range(len(self.ida)):

                if i + 1 < len(self.ida):

                    rota_detalhada_formatada.append((self.ida[i], self.ida[i + 1]))

            self.ida = rota_detalhada_formatada

    def formata_rota_volta(self):

        if self.volta:

            rota_detalhada_formatada = []

            for i in range(len(self.volta)):

                if i + 1 < len(self.volta):

                    rota_detalhada_formatada.append((self.volta[i], self.volta[i + 1]))

            self.volta = rota_detalhada_formatada
