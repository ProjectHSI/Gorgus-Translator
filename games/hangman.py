from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Label, Footer, Input
from textual.containers import Vertical

from translations import translation_dictionary
from random import choice


class Hangman(ModalScreen):
    BINDINGS = [
        Binding(
            "escape",
            "quit_game",
            "quit game",
            tooltip="Quit the game"
        )
    ]

    HANGMANPICS = ['''
    +---+
    |   |
        |
        |
        |
        |
    =========''', '''
    +---+
    |   |
    O   |
        |
        |
        |
    =========''', '''
    +---+
    |   |
    O   |
    |   |
        |
        |
    =========''', '''
    +---+
    |   |
    O   |
   /|   |
        |
        |
    =========''', '''
    +---+
    |   |
    O   |
   /|\  |
        |
        |
    =========''', '''
    +---+
    |   |
    O   |
   /|\  |
   /    |
        |
    =========''', '''
    +---+
    |   |
    O   |
   /|\  |
   / \  |
        |
    ========='''
    ]

    def __init__(self):
        possible_words = list(translation_dictionary.keys())
        self.target_word = choice(possible_words)

        self.guesses_left = 6
        self.user_word = "_" * len(self.target_word)

        super().__init__()

    def action_quit_game(self):
        self.dismiss()

    def compose(self):
        with Vertical() as game:
            game.border_title = "Bingbonk Norack (Hangman)"

            yield Label("this doesn't work yet, lmao", variant="error")

            yield Label(self.HANGMANPICS[self.guesses_left], id="hangman-picture")
            yield Input(placeholder="Enter a letter.", max_length=1, id="user-input")
            yield Label(f"Your Guess: [bold]{self.user_word}[/bold]", id="user-word")

        yield Footer(show_command_palette=False)

    CSS = """
    Hangman {
        align: center middle;
    }

    Vertical {
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
        width: 50%;
        height: 50%;
    }

    #user-input {
        margin-bottom: 1;
        dock: bottom;
    }

    #hangman-picture {
        text-align: center;
        min-width: 100%;
    }

    #user-word {
        dock: bottom;
        margin-bottom: 6;
    }
    """