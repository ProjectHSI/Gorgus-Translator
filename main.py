__VERSION__ = 1.6
print("Hello. I am loading stuff in the background, gimme a sec plz.")


import os
import subprocess

GIT_AVAILABLE = True
try:
    import git
except ModuleNotFoundError:
    GIT_AVAILABLE = False

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, TabbedContent, TabPane, Select, Label, MarkdownViewer, DataTable, Input, Rule, Checkbox, Button
from textual.containers import Horizontal, Vertical
from textual import on, work, log
from textual.css.query import NoMatches
from textual.worker import Worker, WorkerState

from translations import translation_dictionary, phrase_translations, dictionary_information
from translater import translate

class GorgusTranslator(App):
    TITLE = "Gorgus Translator"
    #SUB_TITLE = "Made with ❤️ by @spookydervish"

    CSS_PATH = "resources/style.tcss"

    #ENABLE_COMMAND_PALETTE = False
    #theme = "flexoki"

    @work(thread=True, group="updates", name="check-updates")
    def check_for_updates(self):
        """This function will return `True` when updates are available, otherwise it will return `False`.
        """

        if not GIT_AVAILABLE:
            self.notify("You can't update because [bold]gitpython[/bold] is not installed. Use pip to install it.", title="Can't Update", severity="warning", timeout=6)
            return

        # Initialize the repository object
        repo = git.Repo(os.getcwd())

        # Fetch the latest changes from the remote (to ensure you have the latest state)
        repo.remotes.origin.fetch()

        # Get the current branch and its corresponding remote tracking branch
        current_branch = repo.active_branch
        remote_ref = f'origin/{current_branch.name}'

        # Compare the current branch with the remote tracking branch
        commits_behind = len(list(repo.iter_commits(f'{remote_ref}..{current_branch}')))
        #commits_ahead = len(list(repo.iter_commits(f'{current_branch}..{remote_ref}')))

        return commits_behind > 0

    @work(thread=True, group="updates", name="check-updates")
    def update(self):
        self.query_one("#update-button").disabled = True

        self.notify("Applying updates...")
        repo = git.Repo(os.getcwd())
        repo.remotes.origin.fetch()

        #current_branch = repo.active_branch

        repo.remotes.origin.pull()
        self.notify("Done! Restart for changes to be finished.", title="Updates Complete")

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

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed):
        if event.button.id == "update-button":
            self.update()

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
            with TabPane("Settings"):
                settings_panel = Vertical(
                    Checkbox("Check for updates when openned.", button_first=False, value=True),
                    Button("Update", variant="success", disabled=True, id="update-button", tooltip="Apply updates"),
                    id="settings-panel"
                )
                settings_panel.border_title = "Settings"
                yield settings_panel

        yield Footer()

    def on_worker_state_changed(self, event: Worker.StateChanged):
        worker = event.worker
        if worker.name == "check-updates":
            if worker.state == WorkerState.SUCCESS:
                log(f"Updates available: {worker.result}")
                self.query_one("#update-button").disabled = not worker.result
                if worker.result == True: # There are updates available!
                    self.notify("Updates available on Github! Go to settings to apply them.", title="Updates Available")
                elif worker.result == False: # Up to date
                    self.notify("No updates available, you're up to date!", title="No Updates Available")
            elif worker.state == WorkerState.ERROR:
                self.notify("Failed to check for updates. :(", severity="error")

    def on_ready(self):
        self.update_dictionary_table(self.query_one("#dict-table"), "")
        self.app.notify(
            message="Please be mindful, not a lot of English words exist in Gorgus, and the translator is not perfect yet.",
            title="Welcome!",
            severity="information",
            timeout=10
        )

        self.app.notify("Checking for updates...")
        self.check_for_updates()


if __name__ == "__main__":
    # clear the screen
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    # start the app
    app = GorgusTranslator()
    app.run()