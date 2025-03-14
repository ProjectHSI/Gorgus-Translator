from network import Network
from time import sleep


def main():
    run = True
    n = Network()
    player = n.get_player()

    try:
        while run:
            player2 = n.send(player)

            print(f"my name: {player.data['name']}")
            print(f"other player's name: {player2.data['name']}")

            sleep(1/10)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()