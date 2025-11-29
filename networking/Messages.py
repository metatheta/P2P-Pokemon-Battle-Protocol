from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import field

# this it the parent class that has the message_type
# and the toMessageFormat() method
@dataclass
class Message:
    message_type: str = field(init=False)

    def toMessageFormat(self) -> str:
        m = asdict(self)
        
        result = ""

        for k, v in m.items():
            result += f'{k}: {v}\n'

        return result

@dataclass
class Acknowledgement(Message):
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
class StatBoost():
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
    content_type: str = field(init=False)

    def __post_init__(self):
        self.message_type: str = "CHAT_MESSAGE"

@dataclass
class TextMessage(ChatMessage):
    message_text: str

    def __post_init__(self):
        self.content_type = "TEXT"

# TODO: CHANGE STICKER DATA TO PROPER TYPE
@dataclass
class StickerMessage(ChatMessage):
    sticker_data: any

    def __post_init__(self):
        self.content_type: str = "STICKER"