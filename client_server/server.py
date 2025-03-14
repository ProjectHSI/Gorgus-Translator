import socket
from _thread import start_new_thread
import pickle, sys, os

sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))

from rich.console import Console
from client_server.player import Player
from client_server.packet import Packet, PacketType

from translations import translation_dictionary
from translater import remove_all_except
from random import choice

from argparse import ArgumentParser


normalized_translation_dict = {remove_all_except(k): ([v] if isinstance(v, str) else v) for k, v in translation_dictionary.items()}
possible_words = [key for key in normalized_translation_dict.keys() if key.find("-") == -1 and key.find("'") == -1 and key.find("<") == -1]

console = Console()


class Game:
    def __init__(self, id):
        self.ready = False
        self.id = id

        self.winner = None
        self.get_target_words()

        self.current_words = [self.__target_words[0], self.__target_words[0]]

        self.points = [0, 0] # both players start with zero points

    def get_target_words(self):
        self.__target_words = []
        self.__answers = []

        for i in range(10):
            word = choice(possible_words)

            self.__target_words.append(word)
            self.__answers.append(normalized_translation_dict.get(word))

    def reset(self):
        self.winner = None

    def play(self, player, answer):
        if self.winner:
            return
        
        self.winner = 1

        if answer.lower() in self.__answers[self.points[player]]:
            self.points[player] += 1

            if self.points[player] == 10:
                self.winner = player
                return True

            self.current_words[player] = self.__target_words[self.points[player]]
            return True
        return False

    def is_winner(self, player):
        return self.winner == player

    def connected(self):
        return self.ready

class Server:
    def __init__(self, HOST, PORT, log_level: int = 2):
        self.log_level = log_level
        self.BLOCKED_IPS = ["172.31.128.41"]

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
        self.log(f"Give this ip to your friends to connect: [bold green]{s.getsockname()[0]}[/bold green]")

        while True:
            conn, addr = s.accept()

            if addr[0] in self.BLOCKED_IPS:
                self.log(f"Ignored connection from blocked ip: {addr}")
                continue

            self.log(f"New connection! Address: {addr}")

            self.id_count += 1
            p = 0
            game_id = (self.id_count - 1) // 2

            if self.id_count % 2 == 1: # create a new game
                self.log(f"Creating new game for player.. [dim]{addr}[/dim]")
                self.games[game_id] = Game(game_id)
                self.log(f"Created game!", 1)
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
                data = pickle.loads(conn.recv(4096))

                if game_id in self.games:
                    game: Game = self.games[game_id]

                    if not data:
                        self.log(f"Client did not respond, disconnecting!", 1)
                        break

                    self.log(f"Received: {data}", 1)

                    if data.packet_type == PacketType.GET:
                        reply = Packet(PacketType.SEND, game)
                    elif data.packet_type == PacketType.ANSWER:
                        if not isinstance(data.data, str):
                            reply = Packet(PacketType.MESSAGE, "Invalid data!")
                        else:
                            was_correct = game.play(player, data.data)

                            if game.is_winner(player):
                                reply = Packet(PacketType.WIN, player)
                            else:
                                reply = Packet(PacketType.MESSAGE, was_correct and "Correct!" or "Incorrect... :(")

                    self.log(f"Reply: {pickle.dumps(reply)}", 1)
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
        
        message = str(message)
        
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
    parser = ArgumentParser(
        prog="Gorgus Server",
        description="Used to host games for the Gorgus translator. This isn't completely secure, so I don't recommend port forwarding this..."
    )

    parser.add_argument("-H", "--host", type=str, default=socket.gethostbyname(socket.gethostname()), required=False, help="The IP to host the server on. Defaults to the private IP of your machine.")
    parser.add_argument("-p", "--port",  type=int, required=False, default=5000, help="The port to host the server on, defaults to 5555.")
    parser.add_argument("-l", "--log-level", type=int, required=False, default=2)

    args = parser.parse_args()

    server = Server(args.host, args.port, args.log_level)