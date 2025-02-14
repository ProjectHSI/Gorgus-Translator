__VERSION__ = 1.7
print("Hello. I am loading stuff in the background, gimme a sec plz.")

import os, sys
import json
import importlib.util
import platform
import subprocess

GIT_AVAILABLE = True
try:
    import git
except ModuleNotFoundError:
    GIT_AVAILABLE = False

def install_module(module_name):
    if module_name == "gitpython":
        module_name = "git"

    if importlib.util.find_spec(module_name) is None:
        print(f"{module_name} not found. Installing...")
        
        # Determine correct pip command
        pip_cmd = "pip" if platform.system() == "Windows" else "pip3"
        
        try:
            subprocess.check_call([pip_cmd, "install", module_name])
            print(f"{module_name} installed successfully!")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to install {module_name}. Please install it manually.")
            sys.exit(1)
    else:
        print(f"{module_name} is already installed.")

with open("requirements.txt", "r") as f:
    for line in f.readlines():
        install_module(line.strip("\n"))

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, TabbedContent, TabPane, Select, Label, MarkdownViewer, DataTable, Input, Rule, Checkbox, Button
from textual.containers import Horizontal, Vertical
from textual import on, work, log
from textual.css.query import NoMatches
from textual.worker import WorkerState
from textual.binding import Binding

from translations import translation_dictionary, phrase_translations, dictionary_information
from translater import translate

class GorgusTranslator(App):
    TITLE = "Gorgus Translator"
    #SUB_TITLE = "Made with ❤️ by @spookydervish"

    CSS_PATH = "resources/style.tcss"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True)
    ]

    def get_settings(self):
        if not os.path.isfile("settings.json"):
            initial_data = {
                "check_updates_on_start": True,
                "theme": "nord",
                "theme_index": 0,
                "clock_enabled": True
            }
            with open("settings.json", "w") as file:
                json.dump(initial_data, file, indent=4)
            return initial_data
        else:
            with open("settings.json", "r") as file:
                return json.load(file)
            
    def modify_json(self, file_path, key, value):
        # Open the file and load its current data
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Modify or add the key-value pair
        data[key] = value

        # Write the updated data back to the JSON file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @work(thread=True, group="updates", name="check-updates", exit_on_error=False)
    def check_for_updates(self):
        """This function will return `True` when updates are available, otherwise it will return `False`.
        """

        # disable the check for updates button
        self.query_one("#check-update-button").disabled = True

        log("Checking for updates..")

        self.app.notify("Checking for updates...")

        if not GIT_AVAILABLE:
            log("Can't check for updates, [bold]gitpython[/bold] is not installed.")
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
        #commits_behind = len(list(repo.iter_commits(f'{remote_ref}..{current_branch}')))

        # how many commits the main branch is ahead of us
        commits_ahead = len(list(repo.iter_commits(f'{current_branch}..{remote_ref}')))

        # re enable the check for updates button
        self.query_one("#check-update-button").disabled = False

        return commits_ahead > 0

    @work(thread=True, group="updates", name="check-updates")
    def update(self):
        log("Downloading updates from git repo..")
        self.query_one("#update-button").disabled = True

        self.notify("Applying updates...")
        repo = git.Repo(os.getcwd())
        repo.remotes.origin.fetch()

        #current_branch = repo.active_branch

        try:
            repo.remotes.origin.pull()
        except git.GitCommandError as e:
            self.notify(f"Updates failed to apply:\n{e}", title="Woops!", severity="error")
            self.query_one("#update-button").disabled = False
            return
        self.notify("Done! Restart for changes to be finished.", title="Updates Complete")

    @work(thread=True, group="dictionary", exclusive=True)
    def update_dictionary_table(self, table, search):
        search = search.strip().lower()
        
        num_words = 0
        for gorgus, english in translation_dictionary.items():
            if gorgus.startswith("<") and gorgus.endswith(">"):
                continue
            
            def search_in_string_or_list(search_query, data):
                if isinstance(data, list):
                    for string in data:
                        if search_query in string:
                            return True
                    return False
                elif isinstance(data, str):
                    return search_query in data
                else:
                    raise TypeError("Data must be a string or a list of strings")
                
            if not search_in_string_or_list(search, gorgus) and not search_in_string_or_list(search, english):
                continue

            info = []
            if gorgus in dictionary_information.get("informal_words"):
                info.append("[red]informal[/red]")
            extra_info = dictionary_information.get("extra_info").get(gorgus)
            if extra_info:
                info.append(extra_info)
            info = ', '.join(info)

            if type(english) == str:
                table.add_row(f"[blue]{gorgus}[/blue]", f"[green]{english}[/green]", info)
            elif type(english) == list:
                table.add_row(f"[blue]{gorgus}[/blue]", f"[green]{', '.join(english)}[/green]", info)
            num_words += 1

        if num_words == 0:
            table.add_row("[blue]Hmm..[/blue]", "[green]No search results found, sorry.[/green]", "[red]:([/red]")

    @on(Checkbox.Changed)
    def checkbox_changed(self, event):
        if "setting" in event.checkbox.classes:
            if event.checkbox.id == "clock_enabled":
                self.notify("You need to restart for this change to take effect.", title="Setting Changed")

            self.modify_json("settings.json", event.checkbox.id, event.checkbox.value)

    @on(Button.Pressed)
    def button_pressed(self, event):
        if event.button.id == "update-button":
            self.update()
        elif event.button.id == "check-update-button":
            self.check_for_updates()

    @on(TextArea.Changed)
    def text_changed(self, event):
        if event.text_area.id != "translate-input": return
        self.update_translation(event.text_area.text)
    
    @on(Input.Changed)
    def search_dictionary(self, event):
        if event.input.id == "search-input":
            try:
                table: DataTable = self.query_one("#dict-table")
            except NoMatches:
                return
            
            table.clear()
            self.update_dictionary_table(table, event.input.value)

    @on(Select.Changed)
    def select_changed(self, event):
        if event.select.id == "to-select": # change translation mode
            try:
                input_area = self.query_one("#translate-input")
                output_area = self.query_one("#output")
            except NoMatches:
                return

            input_area.text = output_area.text

            self.update_translation(input_area.text)
        elif event.select.id == "theme-select": # changing translator theme in settings

            chosen_theme = event.select._options[event.value][0]

            self.modify_json("settings.json", "theme", chosen_theme)
            self.modify_json("settings.json", "theme_index", event.value)
            self.theme = chosen_theme
            

    @work(group="translate")
    async def update_translation(self, text):
        output_text_area: TextArea = self.app.query_one("#output")
        translate_to_selection: Select = self.query_one("#to-select")

        selection = translate_to_selection.value
        #self.app.notify(selection)
        
        if selection == 1:
            output_text_area.text = translate(text, "gorgus")
        elif selection == 2:
            output_text_area.text = translate(text, "english")

    def compose(self) -> ComposeResult:
        settings = self.get_settings()
        try:
            settings["theme_index"]
            settings["clock_enabled"]
        except KeyError: # support older settings.json formats
            self.modify_json("settings.json", "clock_enabled", True)
            self.modify_json("settings.json", "theme_index", 0)
            self.modify_json("settings.json", "theme", "textual-dark")
            settings = self.get_settings()

        yield Header(show_clock=settings["clock_enabled"], id="header")

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
                    Horizontal(
                        Label("Check for updates when openned:"),
                        Checkbox(button_first=False, value=True, id="check_updates_on_start", classes="setting"),
                        classes="setting"
                    ),

                    Horizontal(
                        Label("Show time in the top right:"),
                        Checkbox(button_first=False, value=settings["clock_enabled"], id="clock_enabled", classes="setting"),
                        classes="setting"
                    ),

                    Horizontal(
                        Label("Theme:"),
                        Select([(theme,i) for i, theme in enumerate(self._registered_themes.keys())], allow_blank=False, id="theme-select", value=self.get_settings()["theme_index"]),
                        classes="setting"
                    ),
                    
                    Button("Update", variant="success", disabled=True, id="update-button", classes="side-button", tooltip="Apply updates"),
                    Button("Check for updates", id="check-update-button", classes="side-button", tooltip="Check for updates"),
                    id="settings-panel"
                )
                settings_panel.border_title = "Settings"
                yield settings_panel

        yield Footer()

    def on_worker_state_changed(self, event):
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
                self.notify("Failed to check for updates. :(", severity="error", timeout=10)

    def on_ready(self):
        self.update_dictionary_table(self.query_one("#dict-table"), "")
        self.app.notify(
            message="Please be mindful, not a lot of English words exist in Gorgus, and the translator is not perfect yet.",
            title="Welcome!",
            severity="information",
            timeout=10
        )

        # get the user's settings
        settings = self.get_settings()

        try:
            self.query_one("#check_updates_on_start").value = settings["check_updates_on_start"]
            if settings["check_updates_on_start"]:
                self.check_for_updates()
        except KeyError:
            log("Settings failed to load due to KeyError! Maybe an update broke their settings.json?")
            self.notify(
                "Your settings may be out of date. Please delete the [bold]settings.json[/bold] in the translator's directory and restart the translator.",
                title="Settings Failed to Load",
                severity="error",
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
