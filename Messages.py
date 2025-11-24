from dataclasses import dataclass
from csvStuff.Templates import Pokemon

@dataclass
class HandshakeRequest:
    message_type = "HANDSHAKE_REQUEST"

@dataclass
class HandshakeResponse:
    message_type = "HANDSHAKE_RESPONSE"
    seed: int

@dataclass
class SpectatorRequest:
    message_type = "SPECTATOR_REQUEST"

# TODO: CHANGE STAT BOOSTS WHEN SIR ELMAR REPLIES
@dataclass
class BattleSetup:
    message_type = "BATTLE_SETUP"
    communication_mode = "P2P"
    pokemon_name: str
    stat_boosts = {"special_attack_uses": 5, "special_defense_uses": 5}
    pokemon: Pokemon
    
@dataclass
class AttackAnnounce:
    message_type = "ATTACK_ANNOUNCE"
    move_name: str
    sequence_number: int

@dataclass
class DefenseAnnounce:
    message_type = "DEFENSE_ANNOUNCE"
    sequence_number: int

@dataclass
class CalculationReport:
    message_type = "CALCULATION_REPORT"
    attacker: str
    move_used: str
    remaining_health: int
    damage_dealt: int
    defender_hp_remaining: int
    status_message: str
    sequence_number: int   

@dataclass
class CalculationConfirm:
    message_type = "CALCULATION_CONFIRM"
    sequence_number: int

@dataclass
class ResolutionRequest:
    message_type = "RESOLUTION_REQUEST"
    attacker: str
    move_used: str
    damage_dealt: int
    defender_hp_remaining: int
    sequence_number: int

@dataclass
class GameOver:
    message_over = "GAME_OVER"
    winner: str
    loser: str
    sequence_number: int

@dataclass
class TextMessage:
    message_type = "CHAT_MESSAGE"
    sender_name: str
    content_type = "TEXT"
    message_text: str
    sequence_number: int

# TODO: CHANGE STICKER DATA TO PROPER TYPE
@dataclass
class StickerMessage:
    message_type = "CHAT_MESSAGE"
    sender_name: str
    content_type = "STICKER"
    sticker_data: any
    sequence_number: int