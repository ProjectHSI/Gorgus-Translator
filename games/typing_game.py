from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Label, LoadingIndicator
from textual.events import ScreenResume, ScreenSuspend
from textual import on, work
from time import sleep

import pickle

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
        with Vertical(id="game") as game:
            game.border_title = "Definition Race"
            with Vertical(id="loading"):
                yield Label("Loading..", id="loading-text")
                yield LoadingIndicator()
            with Vertical(id="game-window") as window:
                window.styles.visibility = "hidden"
                yield Label("this is what the game looks like when you get in a match :)")

    def action_quit_game(self):
        self.dismiss()

    @work(thread=True)
    def connect_to_server(self):
        self.run = True

        # get the loading text
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        # use this time to start the client connection
        loading_label.update("Attempting to connect to server..")
        self.app.log("Attempting to connect to game server..")

        self.n = Network()
        self.player = self.n.get_player()

        self.app.log(f"Player: {self.player}")

        if isinstance(self.player, str):
            self.app.log.error(f"Failed to connect to server... :(\n{self.player}")
            loading_label.update(f"Failed to connect! The server may be down. :(")
            loading_symbol.styles.visibility = "hidden"
            return

        self.app.log("Attempting to connect to game server..")

        self.main_loop()

    @work(thread=True)
    def main_loop(self):
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        while self.run:
            try:
                packet = self.n.send(Packet(
                    PacketType.GET,
                    0
                ))
                self.app.log(f"Packet: {packet}")

                if packet.data.ready:
                    self.query_one("#loading").styles.visibility = "hidden"
                    self.query_one("#game-window").styles.visibility = "visible"
                else:
                    loading_label.update(f"Connected! Waiting for players..")
                    loading_symbol.styles.visibility = "hidden"

                sleep(1 / 10)
            except Exception as e:
                self.notify("An error occured, you have been disconnected.", severity="error")
                self.app.log.error(str(e))
                self.run = False
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

    #game {
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
        width: 65%;
        height: 65%;
        min-height: 20;
        align: center middle;
    }

    #loading {
        align: center middle;
        height: 100%;
    }

    #loading-text {
        text-align: center;
        width: 100%;
    }

    LoadingIndicator {
        max-height: 1;
    }
    """
    