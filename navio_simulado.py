# Exemplo de script Python usando pymoos para publicar NODE_REPORT diretamente no MOOSDB.
# Certifique-se de ter o pymoos instalado (pip install pymoos) e um MOOSDB rodando.

import time
import pymoos

class MOOSShipMover:
    def __init__(self,
                 server_host="localhost",
                 server_port=9000,
                 name="ShipMover"):
        """
        Configurações de conexão com o MOOSDB.
        """
        self.server_host = server_host
        self.server_port = server_port
        self.name = name
        self.comms = pymoos.comms()
        self.comms.set_on_connect_callback(self.on_connect)
        self.connected = False

        # Configurações iniciais de posição e velocidade
        self.lat = -22.90879800  # Latitude inicial
        self.lon = -43.15812588  # Longitude inicial
        self.speed_knots = 5    # Velocidade do navio em nós
        self.heading = 0        # Rumo 000 (Norte)
        self.ship_length = 3.8  # Comprimento
        self.mode = "DRIVE"
        
        # Conversão de nós para metros/segundo
        self.knots_to_mps = 0.514444
        self.speed_mps = self.speed_knots * self.knots_to_mps

        # Aproximação para converter metros em graus de latitude
        self.meters_per_degree = 111111

        # Vamos guardar o tempo inicial do sistema ao conectar
        self.start_time = None

    def on_connect(self):
        """Callback chamado ao conectar com o MOOSDB."""
        self.connected = True
        # Armazena o tempo do sistema (ou tempo MOOS local) no momento da conexão
        self.start_time = pymoos.time()
        return True

    def publish_node_report(self):
        """Monta e envia o NODE_REPORT para o MOOSDB."""
        # Calcula tempo decorrido desde que conectou ao MOOSDB
        # (Não é exatamente o tempo do MOOS, mas sim relativo)
        # Se quiser o tempo absoluto do sistema, basta usar time.time().
        elapsed_time = pymoos.time() - self.start_time if self.start_time else 0.0

        node_report = (
            f"NAME=contato_teste,"   # nome do contato
            f"TYPE=SHIP,"            # tipo
            f"TIME={elapsed_time},"  # tempo em float (decorridos desde conexão)
            f"LAT={self.lat},"       # latitude
            f"LON={self.lon},"       # longitude
            f"SPD={self.speed_knots},"  # nós
            f"HDG={self.heading:03d},"   # heading
            f"LENGTH={self.ship_length},"
            f"MODE={self.mode}"
        )
        # Publica no MOOSDB
        self.comms.notify("NODE_REPORT", node_report)

    def update_position(self, dt=1):
        """Atualiza a latitude do navio com base na velocidade e no intervalo de tempo dt."""
        # Movimentando somente em latitude (rumo 000)
        delta_lat = (self.speed_mps * dt) / self.meters_per_degree
        self.lat += delta_lat  # movendo para o norte

    def run(self):
        """Inicia conexão com MOOSDB e loop de envio."""
        self.comms.run(self.server_host, self.server_port, self.name)

        print("Conectando ao MOOSDB...")
        while not self.connected:
            time.sleep(0.5)

        print("Conectado ao MOOSDB. Iniciando envio de NODE_REPORT...")

        while True:
            self.publish_node_report()
            self.update_position(dt=1)
            time.sleep(1)

if __name__ == "__main__":
    # Ajuste host/porta conforme necessário
    mover = MOOSShipMover()
    mover.run()
