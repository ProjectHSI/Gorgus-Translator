from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Label
from textual.containers import Vertical


class Hangman(ModalScreen):
    BINDINGS = [
        Binding(
            "escape",
            "quit_game",
            "quit game",
            tooltip="Quit the game"
        )
    ]

    def action_quit_game(self):
        self.dismiss()

    def compose(self):
        with Vertical() as game:
            yield Label("i haven't finished this be [bold bright_red]patient[/bold bright_red] >:(")

    CSS = """
    Vertical {
        margin: 5 25;
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
    }
    """