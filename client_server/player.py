from typing import Any


class Player:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def update(self, new_data: dict[str, Any]):
        self.data = new_data