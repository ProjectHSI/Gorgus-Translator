from dataclasses import dataclass
from typing import Any
from enum import Enum


class PacketType(Enum):
    GET = 1
    MESSAGE = 2
    ANSWER = 3
    SEND = 4
    CLOSE = 5
    WIN = 6

@dataclass
class Packet:
    packet_type: PacketType
    data: Any