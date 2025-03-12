from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Label, Footer, Input
from textual.containers import Vertical
from textual import on
from textual.validation import Validator

from translations import translation_dictionary
from random import choice


class InputValidator(Validator):
    def validate(self, value):
        if value.lower() in "abcdefghijklmnopqrstuvexyz":
            return self.success()
        else:
            return self.failure("You must enter a letter.")

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

    @on(Input.Submitted)
    def user_pressed_enter(self, event):
        input = event.input
        letter = input.value

        input.value = ""

        if self.user_word.find(letter) != -1: # user has already typed this letter before
            self.notify("You've already guessed that letter.", title="Hangman", severity="error")
            return

    def action_quit_game(self):
        self.dismiss()

    def compose(self):
        with Vertical() as game:
            game.border_title = "Bingbonk Norack (Hangman)"

            yield Label("[bold]" + self.HANGMANPICS[self.guesses_left] + "[/bold]", id="hangman-picture")
            yield Input(placeholder="Enter a letter.", max_length=1, id="user-input", valid_empty=False, tooltip="Guess a letter!", validators=[InputValidator])
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