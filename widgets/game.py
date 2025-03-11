from dataclasses import dataclass

from textual.widgets import Label, Static
from textual.containers import Vertical, Horizontal
from textual import events, on
from textual.binding import Binding


@dataclass
class GameInfo:
    title: str
    description: str


class Game(Vertical, can_focus=True, can_focus_children=False):
    ALLOW_MAXIMIZE = True
    DEFAULT_CSS = """
    Game {
        width: 1fr;
        height: auto;
        padding: 0 1;
        border: tall transparent;
        box-sizing: border-box;
        &:focus {
            border: tall $text-primary;
            background: $primary 20%;
            &.link {
                color: red !important;
            }
        }
        #title { text-style: bold; width: 1fr; }
        .header { height: 1; }
        .description { color: $text-muted; }
        &.-hover { opacity: 1; }
    }
    """

    BINDINGS = [
        Binding(
            "enter",
            "open_game",
            "open game",
            tooltip="Open the game you have selected"
        )
    ]    

    def __init__(self, game_info: GameInfo):
        self.game_info = game_info
        super().__init__()

    def compose(self):
        info = self.game_info
        with Horizontal(classes="header"):
            yield Label(info.title, id="title")
        yield Static(info.description, classes="description")

    @on(events.Enter)
    @on(events.Leave)
    def on_enter(self, event):
        event.stop()
        self.set_class(self.is_mouse_over, "-hover")

    def action_open_game(self):
        self.app.notify("You openned the game!!!!!")