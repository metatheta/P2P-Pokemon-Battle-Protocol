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
    message_type = field(init=False, default='ACKNOWLEDGEMENT')
    ackNumber = int

@dataclass
class HandshakeRequest(Message):
    message_type = field(init=False, default='HANDSHAKE_REQUEST')

@dataclass
class HandshakeResponse(Message):
    message_type = field(init=False, default='HANDSHAKE_RESPONSE')

@dataclass
class SpectatorRequest(Message):
    message_type = field(init=False, default='SPECTATOR_REQUEST')

# TODO: CHANGE STAT BOOSTS WHEN SIR ELMAR REPLIES
@dataclass
class BattleSetup(Message):
    message_type = field(init=False, default='BATTLE_SETUP')
    communication_mode = field(init=False, default="P2P")
    pokemon_name: str
    stat_boosts = field(init=False, default={'special_attack_uses': 5, 'special_defense_uses': 5})
    pokemon: Pokemon
    
@dataclass
class AttackAnnounce(Message):
    message_type = field(init=False, default='ATTACK_ANNOUNCE')
    move_name: str
    sequence_number: int

@dataclass
class DefenseAnnounce(Message):
    message_type = field(init=False, default='DEFENSE_ANNOUNCE')
    sequence_number: int

@dataclass
class CalculationReport(Message):
    message_type = field(init=False, default='CALCULATION_REPORT')
    attacker: str
    move_used: str
    remaining_health: int
    damage_dealt: int
    defender_hp_remaining: int
    status_message: str
    sequence_number: int   

@dataclass
class CalculationConfirm(Message):
    message_type = field(init=False, default='CALCULATION_CONFIRM')
    sequence_number: int

@dataclass
class ResolutionRequest(Message):
    message_type = field(init=False, default='RESOLUTION_REQUEST')
    attacker: str
    move_used: str
    damage_dealt: int
    defender_hp_remaining: int
    sequence_number: int

@dataclass
class GameOver(Message):
    message_type = field(init=False, default='GAME_OVER')
    winner: str
    loser: str
    sequence_number: int

@dataclass
class TextMessage(Message):
    message_type = field(init=False, default='CHAT_MESSAGE')
    sender_name: str
    content_type = field(init=False, default='TEXT')
    message_text: str
    sequence_number: int

# TODO: CHANGE STICKER DATA TO PROPER TYPE
@dataclass
class StickerMessage(Message):
    message_type = field(init=False, default='CHAT_MESSAGE')
    sender_name: str
    content_type = field(init=False, default='STICKER')
    sticker_data: any
    sequence_number: int