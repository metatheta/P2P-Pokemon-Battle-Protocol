from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import field
import uuid

# this it the parent class that has the message_type
# and the toMessageFormat() method
@dataclass
class Message:
    message_type: str = field(init=False)

    def to_message_format(self) -> str:
        m = asdict(self)

        result = ""

        for k, v in m.items():
            result += f"{k}: {v}\n"

        return result

    @staticmethod
    def from_message_format(message: str) -> dict:
        tempDict = {}
        for line in message.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                tempDict[key.strip()] = value.strip()
        return tempDict


@dataclass
class DiscoveryBroadcast(Message):
    host_port: int

    def __post_init__(self):
        self.message_type: str = "BROADCAST"


@dataclass
class Acknowledgement(Message):
    ack_number: int

    def __post_init__(self):
        self.message_type: str = "ACKNOWLEDGEMENT"


@dataclass
class MainMessage(Message):
    sequence_number: int


@dataclass
class HandshakeRequest(MainMessage):
    def __post_init__(self):
        self.message_type: str = "HANDSHAKE_REQUEST"


@dataclass
class HandshakeResponse(MainMessage):
    def __post_init__(self):
        self.message_type: str = "HANDSHAKE_RESPONSE"


@dataclass
class SpectatorRequest(MainMessage):
    def __post_init__(self):
        self.message_type: str = "SPECTATOR_REQUEST"


@dataclass
class StatBoost:
    special_attack_uses: int
    special_defense_uses: int


# TODO: CHANGE STAT BOOSTS WHEN SIR ELMAR REPLIES
@dataclass
class BattleSetup(MainMessage):
    pokemon_name: str
    stat_boosts: StatBoost
    communication_mode: str = "P2P"

    def __post_init__(self):
        self.message_type: str = "BATTLE_SETUP"


@dataclass
class AttackAnnounce(MainMessage):
    move_name: str

    def __post_init__(self):
        self.message_type: str = "ATTACK_ANNOUNCE"


@dataclass
class DefenseAnnounce(MainMessage):
    def __post_init__(self):
        self.message_type: str = "DEFENSE_ANNOUNCE"


@dataclass
class CalculationReport(MainMessage):
    attacker: str
    move_used: str
    remaining_health: int
    damage_dealt: int
    defender_hp_remaining: int
    status_message: str

    def __post_init__(self):
        self.message_type: str = "CALCULATION_REPORT"


@dataclass
class CalculationConfirm(MainMessage):
    def __post_init__(self):
        self.message_type: str = "CALCULATION_CONFIRM"


@dataclass
class ResolutionRequest(MainMessage):
    attacker: str
    move_used: str
    damage_dealt: int
    defender_hp_remaining: int

    def __post_init__(self):
        self.message_type: str = "RESOLUTION_REQUEST"


@dataclass
class GameOver(MainMessage):
    winner: str
    loser: str

    def __post_init__(self):
        self.message_type: str = "GAME_OVER"


@dataclass
class ChatMessage(MainMessage):
    sender_name: str

    def __post_init__(self):
        self.message_type: str = "CHAT_MESSAGE"


@dataclass
class Continue(MainMessage):
    def __post_init__(self):
        self.message_type: str = "CONTINUE"


@dataclass
class TextMessage(ChatMessage):
    message_text: str
    content_type: str = field(default="TEXT", init=False)

    def __post_init__(self):
        self.message_type: str = "CHAT_MESSAGE"

    @staticmethod
    def format(message: dict) -> str:
        return f"[{message.get('sender_name')}]: {message.get('message_text')}"


@dataclass
class StickerMessage(ChatMessage):
    chunk_number: int
    sticker_data: str
    content_type: str = field(default="STICKER", init=False)
    # Base64 encoded string for the sticker image

    def __post_init__(self):
        self.message_type: str = "CHAT_MESSAGE"

@dataclass
class StickerFragment(MainMessage):
    sticker_id: str
    sender_name: str
    chunk_index: int
    total_chunks: int
    fragment_data: str

    def __post_init__(self):
        self.message_type: str = "STICKER_FRAGMENT"

# To minimize the effects of IP-layer fragmentation, we'll do the fragmenting ourselves
# We could technically just leave the fragmenting up to the IP layer, but by doing so
# the system becomes fragile and redundant because even the tiniest missing IP fragment
# invalidates the entire sticker datagram. That's why it's better to fragment it ourselves 
# instead of relying solely on the IP layer to handle it.