from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical, Container, Horizontal
from textual.widgets import Label, LoadingIndicator, Input, ProgressBar
from textual.events import ScreenResume, ScreenSuspend
from textual import on, work
from time import sleep

import socket

from client_server.network import Network
from client_server.packet import Packet, PacketType


class TypingGame(ModalScreen):
    BINDINGS = [
        Binding(
            "escape",
            "quit_game",
            "quit game",
            tooltip="Quit the game"
        )
    ]

    def compose(self):
        with Vertical(id="game") as loading:
            loading.border_title = "Definition Race (Connecting to server..)"
            yield Label("Loading..", id="loading-text")
            yield LoadingIndicator()
        with Container(id="game-window") as game:
            game.styles.display = "none"
            game.border_title = "Definition Race"
            
            yield Label(f"Word: [bold]Loading...[/bold]", id="target-word")
            yield Input(placeholder="Write the English equivelant!", id="user-input", max_length=20)

            with Horizontal(id="player1-progress", classes="progress"):
                yield Label("Player1:", id="p1-label")
                yield ProgressBar(10, show_eta=False)
            with Horizontal(id="player2-progress", classes="progress"):
                yield Label("Player2:", id="p2-label")
                yield ProgressBar(10, show_eta=False)

    @on(Input.Submitted)
    def word_answered(self, event):
        input_box = event.input
        value = input_box.value.lower()

        input_box.value = ""

        if input_box.id == "user-input":
            response = self.n.send(Packet(
                PacketType.ANSWER,
                value
            ))

            self.app.notify(str(response.data))

    def action_quit_game(self):
        self.dismiss()

    @work(thread=True)
    def connect_to_server(self):
        self.run = True

        #self.query_one("#game-window").styles.visibility = "hidden"

        # get the loading text
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        # use this time to start the client connection
        loading_label.update("Attempting to connect to server..")
        self.app.log("Attempting to connect to game server..")

        self.n = Network("192.168.56.1")
        self.player = self.n.get_player()

        self.app.log(f"Player: {self.player}")

        if isinstance(self.player, str):
            self.app.log.error(f"Failed to connect to server... :(\n{self.player}")
            loading_label.update(f"Failed to connect! The server may be down. :(")
            loading_symbol.styles.visibility = "hidden"
            return
        
        if self.player == 0:
            self.query_one("#p1-label").update("Player1 (You):")
            self.query_one("#p2-label").update("Player2      :")
        elif self.player == 1:
            self.query_one("#p2-label").update("Player2 (You):")
            self.query_one("#p1-label").update("Player1      :")

        self.app.log("Attempting to connect to game server..")

        self.main_loop()

    @work(thread=True)
    def main_loop(self):
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        target_word_label = self.query_one("#target-word")

        game_started = False

        while self.run:
            try:
                packet = self.n.send(Packet(
                    PacketType.GET,
                    0
                ))
                self.app.log(f"Packet: {packet}")

                if isinstance(packet, str):
                    self.notify("You have been disconnected from the server because the other player disconnected.")
                    self.app.log.error(packet)
                    self.run = False
                    self.dismiss()
                    break
                
                self.app.log(packet.data.ready)
                target_word_label.update(f"Translate this word to English: [bold]{packet.data.current_words[self.player]}[/bold]")

                if packet.data.ready:
                    if not game_started:
                        self.app.log("Game started!")
                        game_started = True
                        self.query_one("#game").styles.display = "none"
                        self.query_one("#game-window").styles.display = "block"
                        
                    self.n.send(Packet(
                        PacketType.ANSWER,
                        "test"
                    ))

                    
                else:
                    loading_label.update(f"Connected! Waiting for players..")
                    loading_symbol.styles.display = "none"

                sleep(1)
            except Exception as e:
                self.notify("An error occured, you have been disconnected.", severity="error")
                self.app.log.error(str(e))
                self.run = False
                self.dismiss()
                break
        self.n.send(None)

    @on(ScreenSuspend)
    def stop(self, _):
        self.run = False

    @on(ScreenResume)
    def ready(self, _):
        self.connect_to_server()
        

    CSS = """
    TypingGame {
        align: center middle;
    }

    #game, #game-window {
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
        width: 75%;
        height: 85%;
        min-height: 20;
        align: center middle;
    }

    #loading-text {
        text-align: center;
        width: 100%;
    }

    LoadingIndicator {
        max-height: 1;
    }

    #target-word {
        margin-bottom: 1;
    }

    #user-input {
        max-width: 50%
    }

    .progress {
        dock: bottom;
        max-height: 1;
    }

    .progress Label {
        margin-right: 1;
    }

    #player1-progress {
        margin-bottom: 1;
    }
    """
    