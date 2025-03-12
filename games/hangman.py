from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Label, Footer, Input
from textual.containers import Vertical
from textual import on
from textual.validation import Validator

from translations import translation_dictionary
from translater import translate, remove_all_except
from random import choice


class InputValidator(Validator):
    def validate(self, value):
        if value.lower() in "abcdefghijklmnopqrstuvwxyz":
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
        possible_words = [remove_all_except(key) for key in translation_dictionary.keys() if key.find("-") == -1]
        self.target_word = choice(possible_words)

        self.guesses_left = 6
        self.user_word = "_" * len(self.target_word)

        self.guessed_letters = []

        super().__init__()

    @on(Input.Submitted)
    def user_pressed_enter(self, event):
        input = event.input
        
        if not input.is_valid:
            self.app.bell()
            return

        letter = input.value.lower()
        if letter.strip() == "":
            self.app.bell()
            return

        input.value = ""

        if letter in self.guessed_letters or letter in self.user_word: # user has already typed this letter before
            self.notify("You've already guessed that letter.", title="Hangman", severity="error")
            self.app.bell()
            return
        
        if not letter in self.target_word: # the user guessed incorrectly
            self.guessed_letters.append(letter)
            self.query_one("#letters-guessed").update(f"[dim]Letters already guessed: {' '.join(self.guessed_letters)}[/dim]")
            self.guesses_left -= 1

            self.query_one("#hangman-picture").update(f"[bold]{self.HANGMANPICS[self.guesses_left]}[/bold]")

            if self.guesses_left <= 0:
                self.query_one("#user-input").disabled = True
                self.notify(f"You ran out of guesses!!!!!! :(\n\nThe word was \"{self.target_word}\", which means \"{translate(self.target_word, 'english')}\".", title="Hangman", severity="error", timeout=7.5)
                return

            self.notify(f"Oops, wrong guess! You have {self.guesses_left} guesses left.", title="Hangman", severity="warning")

            return

        for i, word_letter in enumerate(self.target_word):
            if word_letter == letter:
                new_word = list(self.user_word)
                new_word[i] = letter
                self.user_word = ''.join(new_word)
        self.query_one("#user-word").update(f"Your Guess: [bold]{self.user_word}[/bold]")

        if self.target_word.lower() == self.user_word.lower():
            self.notify(f"You got the word!\n\nThe word meant \"{translate(self.target_word, 'english')}\".", title="Hangman", timeout=7.5)
            self.query_one("#user-input").disabled = True
        else:
            self.notify("You guessed correct! Keep going. ;)", title="Hangman")

    def action_quit_game(self):
        self.dismiss()

    def compose(self):
        with Vertical() as game:
            game.border_title = "Bingbonk Norack (Hangman)"

            yield Label(f"[bold]{self.HANGMANPICS[self.guesses_left]}[/bold]", id="hangman-picture")
            yield Input(placeholder="Enter a letter.", max_length=1, id="user-input", valid_empty=False, tooltip="Guess a letter!", validators=[InputValidator()])
            yield Label(f"Your Guess: [bold]{self.user_word}[/bold]", id="user-word")
            yield Label("[dim]Letters already guessed:[/dim]", id="letters-guessed")

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
        min-height: 20;
    }

    #user-input {
        dock: bottom;
    }

    #hangman-picture {
        text-align: center;
        min-width: 100%;
        padding-bottom: 1;
    }

    #user-word {
        dock: bottom;
        margin-bottom: 5;
    }
    """