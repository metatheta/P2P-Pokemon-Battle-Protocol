from Connections import PeerConnection
from IO import IO
from BattlerKit import BattlerKit
from Data import Data
from Pokemon import Pokemon
from Messages import (
    HandshakeRequest,
    HandshakeResponse,
    SpectatorRequest,
    BattleSetup,
    AttackAnnounce,
    DefenseAnnounce,
    CalculationReport,
    CalculationConfirm,
    ResolutionRequest,
    GameOver,
    StatBoost,
    Continue,
    BattlerNotification,
)
import random


class SpectatorPeer:
    def __init__(self, connection: PeerConnection):
        self.connection = connection
        self.bk = BattlerKit()
        self.spectator_loop()

    def spectator_loop(self):
        loopDict = {}
        while True:
            loopDict = self.connection.receive()
            match loopDict["message_type"]:
                case "BATTLE_SETUP":
                    if loopDict["sender_addr"] == self.connection.host_addr:
                        self.bk.pokemon = Data.pokemonDataDictionary[
                            loopDict["pokemon_name"].lower()
                        ]
                    else:
                        self.bk.foe = Data.pokemonDataDictionary[
                            loopDict["pokemon_name"].lower()
                        ]
                        self.bk.foeHealth = self.bk.foe.hp
                case "ATTACK_ANNOUNCE":
                    if loopDict["sender_addr"] == self.connection.host_addr:
                        self.bk.move = Data.moveDictionary[
                            loopDict["move_name"].lower()
                        ]
                    else:
                        self.bk.foeMove = Data.moveDictionary[
                            loopDict["move_name"].lower()
                        ]
                case "CALCULATION_REPORT":
                    if loopDict["sender_addr"] == self.connection.host_addr:
                        self.bk.damage = float(loopDict["damage_dealt"])
                    else:
                        self.bk.foeDamage = float(loopDict["damage_dealt"])
                case "CALCULATION_CONFIRM":
                    if loopDict["sender_addr"] == self.connection.host_addr:
                        self.apply_own_hp_update()
                    else:
                        self.apply_enemy_hp_update()
                case "GAME_OVER":
                    print(f"{loopDict['loser']} is unable to battle.")
                    print(f"The winner of this match is {loopDict['winner']}")
                    print("Program shutting down...")
                    self.connection.close()
                    break

    def apply_enemy_hp_update(self):
        self.bk.foeHealth -= self.bk.damage
        print(
            f"Joiner {self.bk.foe.name} took {self.bk.damage}! {max(self.bk.foeHealth, 0)} health remaining!"
        )

    def apply_own_hp_update(self):
        self.bk.health -= self.bk.foeDamage
        print(
            f"Host {self.bk.pokemon.pokemonData.name} took {self.bk.foeDamage}! {max(self.bk.health, 0)} health "
            f"remaining!"
        )
