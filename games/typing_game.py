from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical, Container, Horizontal
from textual.widgets import Label, LoadingIndicator, Input, ProgressBar, Button
from textual.events import ScreenResume, ScreenSuspend
from textual import on, work
from time import sleep

import socket

from client_server.network import Network
from client_server.packet import Packet, PacketType


class TypingGame(ModalScreen):
    BINDINGS = [
        Binding(
            "escape",
            "quit_game",
            "quit game",
            tooltip="Quit the game"
        )
    ]

    def compose(self):
        with Vertical(id="game") as loading:
            loading.border_title = "Definition Race (Connecting to server..)"
            yield Label("Loading..", id="loading-text")
            yield LoadingIndicator()
        with Container(id="game-window") as game:
            game.styles.display = "none"
            game.border_title = "Definition Race"
            
            yield Label(f"Word: [bold]Loading...[/bold]", id="target-word")
            yield Input(placeholder="Write the English equivelant!", id="user-input", max_length=20)

            with Horizontal(id="player1-progress", classes="progress"):
                yield Label("Player1:", id="p1-label")
                yield ProgressBar(10, show_eta=False, id="p1")
            with Horizontal(id="player2-progress", classes="progress"):
                yield Label("Player2:", id="p2-label")
                yield ProgressBar(10, show_eta=False, id="p2")
        with Container(id="end-screen") as end:
            end.styles.display = "none"
            end.border_title = "Game Over!"

            yield Label("Uhh...", variant="warning", id="win-loss-msg")
            yield Label("[dim]If you're seeing this, it means that something went wrong lol.[/dim]", id="extra-msg")

            # TODO: make a rematch system 😭
            #yield Button("Rematch?", variant="default")
            #yield Label("0 / 2 Players")

    @on(Input.Submitted)
    def word_answered(self, event):
        input_box = event.input
        value = input_box.value.lower()

        input_box.value = ""

        if input_box.id == "user-input":
            response = self.n.send(Packet(
                PacketType.ANSWER,
                value
            ))

            if response.packet_type == PacketType.MESSAGE:
                self.app.notify(str(response.data))
            elif response.packet_type == PacketType.WIN:
                input_box.disabled = True

                if response.data == self.player:
                    self.app.notify("You win! Good job. :)")

    def action_quit_game(self):
        self.dismiss()

    @work(thread=True)
    def connect_to_server(self):
        self.run = True

        #self.query_one("#game-window").styles.visibility = "hidden"

        # get the loading text
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        # use this time to start the client connection
        loading_label.update("Attempting to connect to server..")
        self.app.log("Attempting to connect to game server..")

        self.n = Network("169.254.245.236")
        self.player = self.n.get_player()

        self.app.log(f"Player: {self.player}")

        if isinstance(self.player, str):
            self.app.log.error(f"Failed to connect to server... :(\n{self.player}")
            loading_label.update(f"Failed to connect! The server may be down. :(")
            loading_symbol.styles.visibility = "hidden"
            return
        
        if self.player == 0:
            self.query_one("#p1-label").update("Player1 (You):")
            self.query_one("#p2-label").update("Player2      :")
        elif self.player == 1:
            self.query_one("#p2-label").update("Player2 (You):")
            self.query_one("#p1-label").update("Player1      :")

        self.app.log("Attempting to connect to game server..")

        self.main_loop()

    @work(thread=True)
    def main_loop(self):
        loading_label = self.query_one("#loading-text")
        loading_symbol = self.query_one(LoadingIndicator)

        target_word_label = self.query_one("#target-word")

        progress1 = self.query_one("#p1")
        progress2 = self.query_one("#p2")

        game_started = False

        while self.run:
            try:
                packet = self.n.send(Packet(
                    PacketType.GET,
                    0
                ))
                self.app.log(f"Packet: {packet}")

                if isinstance(packet, str):
                    self.notify("You have been disconnected from the server because the game closed.\n\nThis can be caused by another player leaving, or the server closing.")
                    self.app.log.error(packet)
                    self.run = False
                    self.dismiss()
                    break

                self.app.log(packet.data.winner)

                if packet.data.ready:
                    target_word_label.update(f"Translate this word to English: [bold]{packet.data.current_words[self.player]}[/bold]")
                    if packet.data.winner:
                        self.query_one("#game-window").styles.display = "none"
                        self.query_one("#end-screen").styles.display = "block"

                        win_loss_msg = self.query_one("#win-loss-msg")
                        extra_msg = self.query_one("#extra-msg")

                        if packet.data.winner == self.player:
                            win_loss_msg.update("Win!")

                            win_loss_msg.set_class(False, "warning")
                            win_loss_msg.set_class(True, "success")

                            extra_msg.update("[dim]But can you do it faster?[/dim]")
                        else:
                            win_loss_msg.update("Loss... :(")

                            win_loss_msg.set_class(False, "warning")
                            win_loss_msg.set_class(True, "error")

                            extra_msg.update("[dim]They aren't hacking, they just have a good gaming chair.[/dim]")

                    if not game_started:
                        self.app.log("Game started!")
                        game_started = True
                        self.query_one("#game").styles.display = "none"
                        self.query_one("#game-window").styles.display = "block"
                    
                    progress1.update(progress=packet.data.points[0])
                    progress2.update(progress=packet.data.points[1])
                
                else:
                    loading_label.update(f"Connected! Waiting for players..")
                    loading_symbol.styles.display = "none"

                sleep(1) # wait 1 second after every packet sent
            except Exception as e:
                self.notify("An error occured, you have been disconnected.", severity="error")
                self.app.log.error(str(e))
                self.run = False
                self.dismiss()
                break
        self.n.send(None)

    @on(ScreenSuspend)
    def stop(self, _):
        self.run = False

    @on(ScreenResume)
    def ready(self, _):
        self.connect_to_server()
        

    CSS = """
    TypingGame {
        align: center middle;
    }

    #game, #game-window, #end-screen {
        padding: 1;
        background: $boost;
        border: round $primary;
        border-title-align: center;
        width: 75%;
        height: 85%;
        min-height: 20;
        align: center middle;
    }

    #loading-text {
        text-align: center;
        width: 100%;
    }

    LoadingIndicator {
        max-height: 1;
    }

    #target-word {
        margin-bottom: 1;
    }

    #user-input {
        max-width: 50%
    }

    .progress {
        dock: bottom;
        max-height: 1;
    }

    .progress Label {
        margin-right: 1;
    }

    #player1-progress {
        margin-bottom: 1;
    }

    #win-loss-msg {
        text-align: center;
        margin-bottom: 1;
    }

    #extra-msg {
        width: 50%;
        text-align: center;
    }

    #end-screen {
        content-align: center middle;
    }
    """
    