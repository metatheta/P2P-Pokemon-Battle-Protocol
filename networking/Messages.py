from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import field
from data.Templates import Pokemon

# this it the parent class that has the message_type
# and the toMessageFormat() method
@dataclass
class Message:
    message_type: str

    def toMessageFormat(self) -> str:
        m = asdict(self)
        result = ""

        for k, v in m.items():
            result += f'{k}: {v}\n'

        return result

@dataclass
class Acknowledgement(Message):
    ackNumber: int
    message_type: str = "ACKNOWLEDGEMENT"

@dataclass
class HandshakeRequest(Message):
    message_type: str = "HANDSHAKE_REQUEST"

@dataclass
class HandshakeResponse(Message):
    message_type: str = "HANDSHAKE_RESPONSE"

@dataclass
class SpectatorRequest(Message):
    message_type: str = "SPECTATOR_REQUEST"


@dataclass
class StatBoost():
    special_attack_uses: int
    special_defense_uses: int

# TODO: CHANGE STAT BOOSTS WHEN SIR ELMAR REPLIES
@dataclass
class BattleSetup(Message):
    pokemon_name: str
    stat_boosts: StatBoost
    message_type: str = "BATTLE_SETUP"
    communication_mode: str = "P2P"
    
@dataclass
class AttackAnnounce(Message):
    move_name: str
    sequence_number: int
    message_type: str = "ATTACK_ANNOUNCE"

@dataclass
class DefenseAnnounce(Message):
    sequence_number: int
    message_type: str = "DEFENSE_ANNOUNCE"

@dataclass
class CalculationReport(Message):
    attacker: str
    move_used: str
    remaining_health: int
    damage_dealt: int
    defender_hp_remaining: int
    status_message: str
    sequence_number: int
    message_type: str = "CALCULATION_REPORT"

@dataclass
class CalculationConfirm(Message):
    sequence_number: int
    message_type: str = "CALCULATION_CONFIRM"

@dataclass
class ResolutionRequest(Message):
    attacker: str
    move_used: str
    damage_dealt: int
    defender_hp_remaining: int
    sequence_number: int
    message_type: str = "RESOLUTION_REQUEST"

@dataclass
class GameOver(Message):
    winner: str
    loser: str
    sequence_number: int
    message_type: str = "GAME_OVER"

@dataclass
class TextMessage(Message):
    sender_name: str
    message_text: str
    sequence_number: int
    message_type = "CHAT_MESSAGE"
    content_type = "TEXT"

# TODO: CHANGE STICKER DATA TO PROPER TYPE
@dataclass
class StickerMessage(Message):
    sender_name: str
    sticker_data: any
    sequence_number: int
    message_type: str = "CHAT MESSAGE"
    content_type: str = "STICKER"