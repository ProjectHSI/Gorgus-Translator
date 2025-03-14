import socket


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.56.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        print(self.id)

    def connect(self):
        """When we connect to something we want to send back a piece of information to the thing that connected to us.
        """

        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass


if __name__ == "__main__":
    n = Network()