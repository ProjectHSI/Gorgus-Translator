from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Label, Button


class MessageBox(ModalScreen[bool]):
    DEFAULT_CSS ="""
    MessageBox {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 80;
        height: 15;
        border: thick $background 80%;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    #ok {
        width: 100%;
    }
    """
    

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label("The Gorgus Translator is migrating away from SpaCy and to NLTK, while we're doing this, translations (specifically ones that have different verb tenses) will not fully translate correctly.", id="question")
            yield Button("OK", variant="success", id="ok")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()