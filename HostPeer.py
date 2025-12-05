from Connections import HostConnection
from BattlerKit import BattlerKit
from IO import IO
from Data import Data
from Pokemon import Pokemon
from Messages import (
    HandshakeResponse,
    SpectatorRequest,
    BattleSetup,
    AttackAnnounce,
    DefenseAnnounce,
    CalculationReport,
    CalculationConfirm,
    ResolutionRequest,
    GameOver,
    ChatMessage,
    StatBoost,
    Continue,
    HostReady,
    Message,
)
import random

random.seed(1)

# Debug simulation flag
simulate_damage_mismatch = False


# wrapper class for a host connection and battler
# kit
class HostPeer:
    def __init__(self):
        self.connection = HostConnection(8493, verbose_flag=True)
        # Binding to 0 makes the system select an available port
        print("Broadcasting and wating for connections...")
        self.connection.discovery_broadcast()
        self.bk = BattlerKit()
        self.main_loop()

    def main_loop(self):
        loopDict = {}

        while True:
            # get the message from receive and store it in out tempDict
            loopDict = self.connection.receive()

            # we call different methods depending on the result
            # of the switch statement
            match loopDict["message_type"]:
                case "BATTLER_NOTIFICATION":
                    self.battlerAddress = loopDict.get("sender_addr")
                    print(f"Battler located: {self.battlerAddress}")
                    self.echo_to_spectators(Message.dict_to_message(loopDict))
                    if not self.send_host_ready():
                        self.terminate_battle()
                    else:
                        print("Host sent Host Ready")

                # if we receive a handshake request, then we send a
                # handshake response
                case "HANDSHAKE_REQUEST":
                    if not self.send_handshake_response():
                        self.terminate_battle()
                    else:
                        print("Host sent Handshake Response")

                case "SPECTATOR_REQUEST":
                    if not self.send_spectator_response(loopDict["sender_addr"]):
                        self.terminate_battle()
                    else:
                        print("Host sent Spectator Handshake Response")

                # if we receive a battle setup we initialize the values
                # for the enemy pokemon, we check if the current peer
                # uses a HostTransport, if that is true then we make the user
                # choose a move then sends an attack announce
                case "BATTLE_SETUP":
                    self.bk.foe = Data.pokemonDataDictionary[
                        loopDict["pokemon_name"].lower()
                    ]
                    self.bk.foeHealth = self.bk.foe.hp

                    # build pokemon before sending battle setup
                    pokemonChoice = IO.ask_pokemon()
                    tempPokemonData = Data.pokemonDataDictionary[pokemonChoice]
                    moveChoice = IO.ask_move()
                    self.bk.pokemon = Pokemon(
                        tempPokemonData, Pokemon.make_move_tuple(moveChoice)
                    )
                    self.bk.health = self.bk.pokemon.pokemonData.hp

                    self.echo_to_spectators(Message.dict_to_message(loopDict))

                    if not self.send_battle_setup():
                        self.terminate_battle()
                    else:
                        print("Host sent Battle Setup")
                        # Initial UI Update
                        IO.update_battle_status(
                            self.bk.pokemon.pokemonData.name,
                            self.bk.health,
                            self.bk.pokemon.pokemonData.hp,
                            self.bk.foe.name,
                            self.bk.foeHealth,
                            self.bk.foe.hp,
                        )
                        moveIndex = IO.choose_attack(
                            self.bk.pokemon.pokemonData.name, self.bk.pokemon.moveTuple
                        )
                        self.bk.move = Data.moveDictionary[
                            self.bk.pokemon.moveTuple[moveIndex].name.lower()
                        ]
                        if not self.send_attack_announce():
                            self.terminate_battle()
                        else:
                            print("Host sent Attack Announce")

                # if we receive an attack announce, we send the
                # acknowledgement known as the defense announce
                case "ATTACK_ANNOUNCE":
                    self.bk.foeMove = Data.moveDictionary[loopDict["move_name"].lower()]
                    self.echo_to_spectators(Message.dict_to_message(loopDict))
                    if not self.send_defense_announce():
                        self.terminate_battle()
                    else:
                        print("Host sent Defense Announce")

                # if we receive a defense announce, we send the
                # acknowledgement known as the calculation report
                case "DEFENSE_ANNOUNCE":
                    if not self.send_calculation_report():
                        self.terminate_battle()
                    else:
                        print("Host sent Calculation Report")

                # if we receive a calculation report, we check
                # if the report matches our report, if it does
                # we apply the changes to our health, send a
                # calculation confirm, and then have the previous
                # defender make a move and send an attack announce
                # if it does not match we send our calculation
                # through a resolution request
                case "CALCULATION_REPORT":
                    self.bk.foeDamage, multiplier = (
                        self.bk.pokemon.defender_calculation(
                            self.bk.foeMove.name, self.bk.foe.name
                        )
                    )
                    if self.bk.foeDamage == float(loopDict["damage_dealt"]):
                        print("Damage Calculations confirmed equal!")
                        print(f"Self damage computation {self.bk.foeDamage}")
                        print(
                            f"Enemy damage computation {float(loopDict['damage_dealt'])}"
                        )
                        self.apply_own_hp_update()
                        if not self.send_calculation_confirm():
                            self.terminate_battle()
                        else:
                            print(loopDict["status_message"])

                    else:
                        print("Damage Calculations confirmed equal!")
                        print(f"Self damage computation {self.bk.foeDamage}")
                        print(
                            f"Enemy damage computation {float(loopDict['damage_dealt'])}"
                        )
                        if not self.send_resolution_request():
                            self.terminate_battle()
                        else:
                            print("host sent resolution request")

                # since this the end of the 4 way acknowledgement
                # we just need to update the enemy hp
                case "CALCULATION_CONFIRM":
                    self.echo_to_spectators(Message.dict_to_message(loopDict))
                    self.apply_enemy_hp_update()
                    if self.bk.foeHealth <= 0:
                        if not self.send_game_over():
                            self.terminate_battle()
                        else:
                            print(f"{self.bk.foe.name} is unable to battle")
                            print(f"The winner is {self.bk.pokemon.pokemonData.name}")
                            print("Program shutting down...")
                            self.connection.close()
                            break
                    else:
                        if not self.send_continue():
                            self.terminate_battle()

                # if we receive a resolution request, we need to
                # check if the recalculated damage matches the
                # received damage, if it does we send an ack and
                # update enemy health on our end, if it still doesnt
                # then we termine the battle
                case "RESOLUTION_REQUEST":
                    self.bk.damage, multiplier = self.bk.pokemon.attacker_calculation(
                        self.bk.move.name, self.bk.foe.name
                    )
                    if self.bk.damage == float(loopDict["damage_dealt"]):
                        print("Damage Calculations confirmed equal!")
                        print(f"Self damage computation {self.bk.foeDamage}")
                        print(
                            f"Enemy damage computation {float(loopDict['damage_dealt'])}"
                        )
                        self.apply_enemy_hp_update()
                        if self.bk.foeHealth <= 0:
                            if not self.send_game_over():
                                self.terminate_battle()
                            else:
                                print(f"{self.bk.foe.name} is unable to battle!")
                                print(
                                    f"The winner is {self.bk.pokemon.pokemonData.name}"
                                )
                                print("Program shutting down...")
                                self.connection.close()
                                break
                        else:
                            if not self.send_continue():
                                self.terminate_battle()
                    else:
                        print("Damage Calculations confirmed equal!")
                        print(f"Self damage computation {self.bk.foeDamage}")
                        print(
                            f"Enemy damage computation {float(loopDict['damage_dealt'])}"
                        )
                        self.terminate_battle()
                        break

                # if we receive a game over message it means that
                # our pokemon fainted and the program shits down
                case "GAME_OVER":
                    self.echo_to_spectators(Message.dict_to_message(loopDict))
                    print(f"{loopDict['loser']} is unable to battle.")
                    print(f"The winner of this match is {loopDict['winner']}")
                    print("Program shutting down...")
                    self.connection.close()
                    break

                # we receive this when our pokemon can still fight
                # after receiving an attack
                case "CONTINUE":
                    moveIndex = IO.choose_attack(
                        self.bk.pokemon.pokemonData.name, self.bk.pokemon.moveTuple
                    )
                    self.bk.move = Data.moveDictionary[
                        self.bk.pokemon.moveTuple[moveIndex].name.lower()
                    ]
                    if not self.send_attack_announce():
                        self.terminate_battle()

    def terminate_battle(self):
        print("Connection lost... battle over... shutting down...")
        self.connection.close()

    def send_handshake_response(self) -> bool:
        message = HandshakeResponse(0).to_message_format()
        return self.connection.send(message, self.battlerAddress)

    def send_spectator_response(self, addr) -> bool:
        message = HandshakeResponse(0).to_message_format()
        return self.connection.send(message, addr)

    def send_battle_setup(self) -> bool:
        sb = StatBoost(5, 5)

        message = BattleSetup(
            0, pokemon_name=self.bk.pokemon.pokemonData.name, stat_boosts=sb
        ).to_message_format()
        self.echo_to_spectators(message)
        return self.connection.send(message, self.battlerAddress)

    def send_attack_announce(self) -> bool:
        message = AttackAnnounce(0, move_name=self.bk.move.name).to_message_format()
        self.echo_to_spectators(message)
        return self.connection.send(message, self.battlerAddress)

    def send_defense_announce(self) -> bool:
        message = DefenseAnnounce(0).to_message_format()
        return self.connection.send(message, self.battlerAddress)

    def send_calculation_report(self) -> bool:
        a = self.bk.pokemon.pokemonData.name
        b = self.bk.move.name
        self.bk.damage, multiplier = self.bk.pokemon.attacker_calculation(
            b, self.bk.foe.name
        )

        # Damage mismatch simulation
        reported_damage = self.bk.damage
        if simulate_damage_mismatch:
            reported_damage = self.bk.damage + 10
            print(
                f"SIMULATION: Reporting incorrect damage {reported_damage} instead of {self.bk.damage}"
            )

        tempEnemyHP = self.bk.foeHealth - reported_damage
        tempMessage = f"{a} used {b}!"
        if multiplier >= 2:
            tempMessage += " It was super effective!"
        elif multiplier <= 0.5:
            tempMessage += " It was not very effective..."

        message = CalculationReport(
            0,
            attacker=a,
            move_used=b,
            remaining_health=self.bk.health,
            damage_dealt=reported_damage,
            defender_hp_remaining=tempEnemyHP,
            status_message=tempMessage,
        ).to_message_format()
        self.echo_to_spectators(message)
        return self.connection.send(message, self.battlerAddress)

    def send_calculation_confirm(self):
        message = CalculationConfirm(0).to_message_format()
        self.echo_to_spectators(message)
        return self.connection.send(message, self.battlerAddress)

    def send_resolution_request(self):
        self.bk.foeDamage, multiplier = self.bk.pokemon.defender_calculation(
            self.bk.foeMove.name, self.bk.foe.name
        )
        tempHP = self.bk.health - self.bk.foeDamage
        message = ResolutionRequest(
            0,
            attacker=self.bk.foe.name,
            move_used=self.bk.foeMove.name,
            damage_dealt=self.bk.foeDamage,
            defender_hp_remaining=tempHP,
        ).to_message_format()
        return self.connection.send(message, self.battlerAddress)

    def send_game_over(self):
        message = GameOver(
            0, winner=self.bk.pokemon.pokemonData.name, loser=self.bk.foe.name
        ).to_message_format()
        self.echo_to_spectators(message)
        return self.connection.send(message, self.battlerAddress)

    def send_continue(self):
        message = Continue(0).to_message_format()
        return self.connection.send(message, self.battlerAddress)

    def send_host_ready(self):
        message = HostReady(0).to_message_format()
        return self.connection.send(message, self.battlerAddress)

    def apply_enemy_hp_update(self):
        self.bk.foeHealth -= self.bk.damage
        print(
            f"Enemy {self.bk.foe.name} took {self.bk.damage}! {max(self.bk.foeHealth, 0)} health remaining!"
        )
        IO.update_battle_status(
            self.bk.pokemon.pokemonData.name,
            self.bk.health,
            self.bk.pokemon.pokemonData.hp,
            self.bk.foe.name,
            self.bk.foeHealth,
            self.bk.foe.hp,
        )

    def apply_own_hp_update(self):
        self.bk.health -= self.bk.foeDamage
        print(
            f"Your {self.bk.pokemon.pokemonData.name} took {self.bk.foeDamage}! {max(self.bk.health, 0)} health remaining!"
        )
        IO.update_battle_status(
            self.bk.pokemon.pokemonData.name,
            self.bk.health,
            self.bk.pokemon.pokemonData.hp,
            self.bk.foe.name,
            self.bk.foeHealth,
            self.bk.foe.hp,
        )

    def echo_to_spectators(self, message: str):
        for addr in self.connection.connected_peers.keys():
            if addr != self.battlerAddress:
                self.connection.send(message, addr)
