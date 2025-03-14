import socket
from _thread import start_new_thread
import pickle, sys, os

sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))

from rich.console import Console
from client_server.player import Player

from enum import Enum
from dataclasses import dataclass
from typing import Any


console = Console()


class PacketType(Enum):
    GET = 1
    MESSAGE = 2

@dataclass
class Packet:
    packet_type: PacketType
    data: Any

class Game:
    def __init__(self, id):
        self.ready = False
        self.id = id

    def connected(self):
        return self.ready

class Server:
    def __init__(self, HOST, PORT, log_level: int = 2):
        self.log_level = log_level

        self.log("Creating socket..", 1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.log("Attempting to bind socket..", level=1)
        try:
            s.bind((HOST, PORT))
        except socket.error as e:
            self.log(f"Failed to bind socket! {e}", level=4)

        self.log("Setting up game data..", 1)
        self.connected = set()
        self.games = {}
        self.id_count = 0

        s.listen(2)
        self.log("Waiting for connections! Server is running.")

        while True:
            conn, addr = s.accept()
            self.log(f"New connection! Address: {addr}")

            self.id_count += 1
            p = 0
            game_id = (self.id_count - 1) // 2

            if self.id_count % 2 == 1: # create a new game
                self.log(f"Creating new game for player.. [dim]{addr}[/dim]")
                self.games[game_id] = Game(game_id)
            else:
                self.log(f"Player has joined a game! [dim]{addr}[/dim]")
                self.games[game_id].ready = True
                p = 1

            start_new_thread(self.threaded_client, (conn, p, game_id))

    def threaded_client(self, conn: socket.socket, player, game_id):
        self.log("Started new thread for client.", level=1)

        conn.send(pickle.dumps(player))

        reply = ""

        while True:
            try:
                data = pickle.loads(conn.recv(2048))

                if game_id in self.games:
                    game = self.games[game_id]

                    if not data:
                        self.log(f"Client did not respond, disconnecting!", 1)
                        break
                    else:
                        reply = game
                        conn.sendall(pickle.dumps(reply))
                else:
                    break
            except (socket.error, EOFError) as e:
                self.log(f"An error occured with a client and that client has been disconnected.\nError: {e}", 3)
                break
        
        self.log(f"Lost connection! [dim][bold]game_id:[/bold] {game_id}[/dim]")

        try:
            del self.games[game_id]
            self.log(f"Closing game.. [dim][bold]game_id:[/bold] {game_id}[/dim]")
        except:
            pass
        
        self.id_count -= 1
        conn.close()

    def log(self, message: str, level: int = 2):
        """
        Show a message to the console.

        # Levels:
            - 1: Debug, not useful to the average user.
            - 2: Info, use when you just want to show some information to the user that they might need.
            - 3: Warning, slightly important info
            - 4: Error, an error occured and the server can't continue running
        """
        if level < self.log_level:
            return
        
        final_message = ""

        if level == 1:
            final_message = f"[bold][[blue_violet]DEBUG[/blue_violet]][/bold]     {message}"
        elif level == 2:
            final_message = f"[bold][[spring_green2]INFO[/spring_green2]][/bold]      {message}"
        elif level == 3:
            final_message = f"[bold][[light_goldenrod1]WARNING[/light_goldenrod1]][/bold]   {message}"
        elif level == 4:
            final_message = f"[bold][[bright_red]ERROR[/bright_red]][/bold]     {message}"

        console.print(final_message)


if __name__ == "__main__":
    server = Server("192.168.56.1", 5555, 1)