__VERSION__ = 1.6
print("Hello. I am loading stuff in the background, gimme a sec plz.")


import os

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, TabbedContent, TabPane, Select, Label, MarkdownViewer, DataTable, Input, Rule
from textual.containers import Horizontal, Vertical
from textual import on, work
from textual.css.query import NoMatches
from translations import translation_dictionary, phrase_translations, dictionary_information
from translater import translate

class GorgusTranslator(App):
    TITLE = "Gorgus Translator"
    #SUB_TITLE = "Made with ❤️ by @spookydervish"

    CSS_PATH = "resources/style.tcss"

    #ENABLE_COMMAND_PALETTE = False
    #theme = "flexoki"

    @work(thread=True, group="dictionary", exclusive=True)
    def update_dictionary_table(self, table: DataTable, search: str = None):
        if search:
            search = search.strip()
            if search == "":
                search = None
        
        num_words = 0
        for gorgus, english in translation_dictionary.items():
            if gorgus.startswith("<") and gorgus.endswith(">"):
                continue
            
            if search:
                english_find = False # this is true if it was found in the english column of the dictionary
                if type(english) == str:
                    if english_find == False:
                        english_find = (english.lower().find(search) != -1)
                elif type(english) == list:
                    for thing in english:
                        if thing.lower().find(search) != -1:
                            english_find = True
                            break

                if gorgus.lower().find(search) == -1 and not english_find:
                    continue

            info = []
            if gorgus in dictionary_information.get("informal_words"):
                info.append("[red]informal[/red]")
            info = ', '.join(info)

            if type(english) == str:
                table.add_row(f"[blue]{gorgus}[/blue]", f"[green]{english}[/green]", info)
            elif type(english) == list:
                table.add_row(f"[blue]{gorgus}[/blue]", f"[green]{', '.join(english)}[/green]", info)
            num_words += 1

        if num_words == 0:
            table.add_row("[blue]Hmm..[/blue]", "[green]No search results found, sorry.[/green]", "[red]:([/red]")

    @on(TextArea.Changed)
    def text_changed(self, event: TextArea.Changed):
        if event.text_area.id != "translate-input": return
        self.update_translation(event.text_area.text)
    
    @on(Input.Changed)
    def search_dictionary(self, event: Input.Changed):
        if event.input.id == "search-input":
            try:
                table: DataTable = self.query_one("#dict-table")
            except NoMatches:
                return
            
            table.clear()
            self.update_dictionary_table(table, event.input.value)

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed):
        if event.select.id == "to-select": # change translation mode
            try:
                input_area = self.query_one("#translate-input")
                output_area = self.query_one("#output")
            except NoMatches:
                return

            input_area.text = output_area.text

            self.update_translation(input_area.text)
            

    @work(thread=True, group="translate", exclusive=True)
    def update_translation(self, text: str):
        output_text_area: TextArea = self.app.query_one("#output")
        translate_to_selection: Select = self.query_one("#to-select")

        selection = translate_to_selection.value
        #self.app.notify(selection)
        
        if selection == 1:
            output_text_area.text = translate(text, "gorgus")
        elif selection == 2:
            output_text_area.text = translate(text, "english")

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            with TabPane("Translator", id="translator"): 
                yield Label("Input")
                yield TextArea(text="", tooltip="Type here!", classes="text-box", id="translate-input")
                yield Select([("to Gorgus",1), ("to English",2)], id="to-select", allow_blank=False,prompt="Translate...", value=1)
                yield Label("Translated")
                yield TextArea(text="Hello, how are you?", read_only=True, classes="text-box", tooltip="This is where your translated text will appear.", id="output")
            with TabPane("Dictionary",id="dict-pane"):
                yield Rule(line_style="dashed")
                with Horizontal(id="dictionary-top"):
                    with Vertical(id="lang-stats"):
                        yield Label(" [bold yellow]Language Stats[/bold yellow]")
                        yield Label(f"    - [bold]Words:[/bold] [blue]{len(translation_dictionary)}[/blue]")
                        yield Label(f"    - [bold]Phrases:[/bold] [blue]{len(phrase_translations)}[/blue]")
                    yield Input(placeholder="Search words...", id="search-input", value="")
                yield Rule(line_style="dashed")

                table = DataTable(id="dict-table")
                table.add_columns("Gorgus", "English", "Information")

                

                yield table
            with TabPane("Changelog"):
                try:
                    changelog_file = open("resources/CHANGELOG.md", "r")
                    changelog = changelog_file.read()
                    changelog_file.close()
                except Exception as e:
                    changelog = f"""# Woops!  
  
We failed to load the changelog, try giving **@spookydervish** on **Discord** this error message:  
{e}
                    """
                yield MarkdownViewer(changelog,open_links=False)
            with TabPane("Credits"):
                yield MarkdownViewer("""# Hello!
These are the people that make this possible! *(all of these are Discord usernames)*  
  
- **@pynecoen:** Came up with the idea to make a language and made a majority of the words
- **@spookydervish:** Made the translator, made grammar rules and made words
- **@plenorf:** Contributed many words""", show_table_of_contents=False)

        yield Footer()

    def on_ready(self):
        self.update_dictionary_table(self.query_one("#dict-table"), "")
        self.app.notify(
            message="Please be mindful, not a lot of English words exist in Gorgus, and the translator is not perfect yet.",
            title="Welcome!",
            severity="information",
            timeout=10
        )


if __name__ == "__main__":
    # clear the screen
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    # start the app
    app = GorgusTranslator()
    app.run()