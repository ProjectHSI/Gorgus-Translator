from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Label, LoadingIndicator
from textual.events import ScreenResume, ScreenSuspend
from textual import on

from client_server.network import Network


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
            game.border_subtitle = "Definition Race"
            with Vertical(id="loading"):
                yield Label("hi the game is loading", id="loading-text")
                yield LoadingIndicator()

    def action_quit_game(self):
        self.dismiss()

    @on(ScreenResume)
    def ready(self, event):
        # get the loading text
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        # use this time to start the client connection
        loading_label.update("Attempting to connect to server..")
        self.app.log("Attempting to connect to game server..")

        n = Network()
        player = n.get_player()

        self.app.log(f"Player: {player}")

        if isinstance(player, str):
            self.app.log("Failed to connect to server... :(")
            loading_label.update("Failed to connect! The server may be down. :(")
            loading_symbol.styles.visibility = "hidden"
            self.app.log(player)
            return
        
        loading_label.update("We have a connection! :D")
        

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
    