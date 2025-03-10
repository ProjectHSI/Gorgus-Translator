from dataclasses import dataclass

from textual.widgets import Label, Static
from textual.containers import Vertical, Horizontal


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
    

    def __init__(self, game_info: GameInfo):
        self.game_info = game_info
        super().__init__()

    def compose(self):
        info = self.game_info
        with Horizontal(classes="header"):
            yield Label(info.title, id="title")
        yield Static(info.description, classes="description")