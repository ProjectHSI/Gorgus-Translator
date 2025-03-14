from textual.screen import ModalScreen
from textual.binding import Binding


class TypingGame(ModalScreen):
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