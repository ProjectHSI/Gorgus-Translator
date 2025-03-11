from textual.screen import ModalScreen
from textual.widgets import Footer, Static
from textual.containers import Vertical
from textual.binding import Binding
from textual import work
from time import sleep

import datetime
import random

from translations import translation_dictionary
from translater import remove_all_except

from util import get_settings, modify_json


class WordleGame(ModalScreen):
    BINDINGS = [
        Binding(
            "escape",
            "quit_game",
            "quit game",
            tooltip="Quit the game"
        )
    ]

    def __init__(self):
        self.guesses_left = 6 # how many guesses the user has left
        self.current_guess = "_____" # the user's current word guess
        self.current_letter_index = 0 # the index of the letter the user is typing

        self.letter_index = self.current_letter_index

        self.guessed_correct = False

        self.can_type = True

        today = datetime.date.today()
        seed = today.year * 10000 + today.month * 100 + today.day
        random.seed(seed)

        filtered_keys = [remove_all_except(key) for key in translation_dictionary if '>' not in key and '<' not in key and len(remove_all_except(key)) == 5]
        self.target_word = random.choice(filtered_keys)
        
        super().__init__()

    def action_quit_game(self):
        self.dismiss()

    def compose(self):
        settings = get_settings()

        if settings.get("completed_gordle", False):
            self.notify("You've already completed the Gordle for today! Come back tomorrow. >:(", title="Gordle", severity="error")
            self.dismiss()
            return

        self.notify("This is basically just Wordle, except the words are in Gorgus lol.", title="Welcome to Gordle!", timeout=7.5)

        with Vertical() as game:
            game.border_title = "Gordle"

            for i in range(30):
                yield Static(" ", disabled=True, id=f"letter{i}", classes="letter no-guess")

        yield Footer(show_command_palette=True)
    
    @work(thread=True)
    def play_animation(self):
        self.can_type = False

        first_letter_index = self.letter_index - 4
        for i in range(first_letter_index, self.letter_index+1):
            letter: Static = self.query_one(f"#letter{i}")

            current_letter = letter._content.lower()
            word_index = i - first_letter_index

            chosen_class = ""
            
            if self.target_word[word_index] == current_letter:
                chosen_class = "correct"
            elif current_letter in self.target_word:
                chosen_class = "elsewhere"
            else:
                chosen_class = "incorrect"

            letter.set_class(True, chosen_class)
            letter.set_class(False, "no-guess")
            sleep(0.2)

        if self.current_guess.lower() == self.target_word:
            self.guessed_correct = True


        # notifications
        if not self.guessed_correct:
            if self.guesses_left > 0:
                self.app.notify(f"{self.guesses_left} guesses left!", title="Gordle")
                self.can_type = True
            else:
                self.app.notify(f"You didn't guess the word... :( Better luck next time!\n\nThe word was \"{self.target_word}\".", title="Gordle", severity="error")
                modify_json("settings.json", "completed_gordle", True)
        else:
            self.app.notify(f"You guessed the word in {6-self.guesses_left} attempt(s)! Congrats!\n\nCome back tomorrow for your next word. ;)", title="Gordle")
            modify_json("settings.json", "completed_gordle", True)

    async def on_key(self, event):
        if not self.can_type:
            return
        
        key = event.key.upper()

        if key == "BACKSPACE":
            if self.current_letter_index <= 0:
                self.app.bell()
                return

            modified_guess = list(self.current_guess)
            modified_guess[self.current_letter_index] = "_"
            self.current_guess = ''.join(modified_guess)

            current_guess = 6 - self.guesses_left
            self.letter_index = self.current_letter_index + 5*current_guess - 1
            current_letter = self.query_one(f"#letter{self.letter_index}")

            current_letter.update(" ")
            
            self.current_letter_index -= 1
            return

        if not key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.app.bell()
            return

        modified_guess = list(self.current_guess)
        modified_guess[self.current_letter_index] = key
        self.current_guess = ''.join(modified_guess)

        current_guess = 6 - self.guesses_left
        self.letter_index = self.current_letter_index + 5*current_guess

        current_letter = self.query_one(f"#letter{self.letter_index}")

        current_letter.update(key)

        self.current_letter_index += 1
        if self.current_letter_index >= 5:
            self.current_letter_index = 0
            self.guesses_left -= 1

            self.play_animation()

    CSS = """
    Vertical {
        margin: 5 25;
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
        layout: grid;
        grid-size: 5 6;
        align: center middle;
        grid-gutter: 1;
        grid-columns: 8;
        grid-rows: 3;
    }

    .letter {
        width: 8;
        height: 3;

        text-align: center;

        &.no-guess {
           border: tall $boost;
        }

        &.correct {
            background: $success;
            border: tall $success-lighten-2;
        }

        &.incorrect {
            background: transparent;
            border: tall $panel;
        }

        &.elsewhere {
            background: $warning;
            border: tall $warning-lighten-2;
        }
    }
    """