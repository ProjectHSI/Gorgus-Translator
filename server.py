import socket
from threading import Thread
import os

from rich.console import Console


console = Console()


class Server:
    def __init__(self, HOST, PORT, log_level: int = 2):
        # Create a new socket. AF_INET is the address family for IPv4
        # SOCK_STREAM is the socket type for TCP.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))

        # Enable a server to accept connections.
        self.socket.listen()
        console.print()

    def log(self, message: str, level: int = 2):
        """
        Show a message to the console.

        Levels:
            - 1: Debug, not useful to the average user.
            - 2: Info, use when you just want to show some information to the user that they might need.
            - 3: Warning, slightly important info
            - 4: Error, an error occured and the server can't continue running
        """