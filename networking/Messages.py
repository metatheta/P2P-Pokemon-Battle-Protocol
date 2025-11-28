from dataclasses import dataclass
from dataclasses import asdict

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
    message_type: str = "ACKNOWLEDGEMENT"

@dataclass
class MainMessage(Message):
    sequence_number: int

@dataclass
class HandshakeRequest(MainMessage):
    message_type: str = "HANDSHAKE_REQUEST"

@dataclass
class HandshakeResponse(MainMessage):
    message_type: str = "HANDSHAKE_RESPONSE"

@dataclass
class SpectatorRequest(MainMessage):
    message_type: str = "SPECTATOR_REQUEST"


@dataclass
class StatBoost():
    special_attack_uses: int
    special_defense_uses: int

# TODO: CHANGE STAT BOOSTS WHEN SIR ELMAR REPLIES
@dataclass
class BattleSetup(MainMessage):
    pokemon_name: str
    stat_boosts: StatBoost
    message_type: str = "BATTLE_SETUP"
    communication_mode: str = "P2P"
    
@dataclass
class AttackAnnounce(MainMessage):
    move_name: str
    message_type: str = "ATTACK_ANNOUNCE"

@dataclass
class DefenseAnnounce(MainMessage):
    message_type: str = "DEFENSE_ANNOUNCE"

@dataclass
class CalculationReport(MainMessage):
    attacker: str
    move_used: str
    remaining_health: int
    damage_dealt: int
    defender_hp_remaining: int
    status_message: str
    message_type: str = "CALCULATION_REPORT"

@dataclass
class CalculationConfirm(MainMessage):
    message_type: str = "CALCULATION_CONFIRM"

@dataclass
class ResolutionRequest(MainMessage):
    attacker: str
    move_used: str
    damage_dealt: int
    defender_hp_remaining: int
    message_type: str = "RESOLUTION_REQUEST"

@dataclass
class GameOver(MainMessage):
    winner: str
    loser: str
    message_type: str = "GAME_OVER"

@dataclass
class TextMessage(MainMessage):
    sender_name: str
    message_text: str
    message_type = "CHAT_MESSAGE"
    content_type = "TEXT"

# TODO: CHANGE STICKER DATA TO PROPER TYPE
@dataclass
class StickerMessage(MainMessage):
    sender_name: str
    sticker_data: any
    message_type: str = "CHAT MESSAGE"
    content_type: str = "STICKER"