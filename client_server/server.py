import socket
from _thread import start_new_thread
import os

from rich.console import Console


console = Console()


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

        s.listen(2)
        self.log("Waiting for connections! Server is running.")

        while True:
            conn, addr = s.accept()
            self.log(f"New connection! Address: {addr}")

            start_new_thread(self.threaded_client, (conn))

    def threaded_client(self, conn: socket.socket):
        self.log("Started new thread for client.", level=1)

        reply = ""

        while True:
            try:
                data = conn.recv(2048)
                reply = data.decode("utf-8")

                if not data:
                    self.log(f"Disconnected.")
                    break
                else:
                    self.log(f"Received: {reply}")
                    self.log(f"Sending: {reply}")
                
                conn.sendall(str.encode(reply, "utf-8"))
            except socket.error as e:
                self.log(f"An error occured with a client and that client has been disconnected.\nError: {e}", 3)
                break
        
        self.log("Lost connection!")
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
    server = Server("192.168.56.1", 5555)