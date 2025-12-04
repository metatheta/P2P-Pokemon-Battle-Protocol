from Connections import PeerConnection
from IO import IO 
from BattlerKit import BattlerKit
from Data import Data
from Pokemon import Pokemon
from SQ import SQ
from Messages import HandshakeRequest, HandshakeResponse, SpectatorRequest, BattleSetup, AttackAnnounce, DefenseAnnounce,CalculationReport, CalculationConfirm, ResolutionRequest, GameOver, ChatMessage, StatBoost, Continue, BattlerNotification
import random
random.seed(4)

class ConnectorPeer():
    battlerAvailable = True

    def __init__(self):
        self.connection = PeerConnection(random.randint(6000, 9999))
        self.connection.wait_for_broadcast()
        print('done waiting for broadcast')
        choice = IO.get_conncector_peer_role(ConnectorPeer.battlerAvailable)
        match choice:
            case 1:
                pass
                # insert code for spectator
            case 2:
                ConnectorPeer.battlerAvailable = False
                if not self.send_battler_notification():
                    self.terminate_battle()
                else: 
                    print('battler notification sent')
                self.bk = BattlerKit()
                print('done making battler kit')

    def main_loop(self):
        print("--- MAIN LOOP STARTED ---")
        loopDict = {}

        if not self.send_handshake_request():
            self.terminate_battle()
        else:
            print('Joiner sent Handsake Request')
        
        while True:
            print('--- ENTERED WHILE TRUE---')
            # get the message from receive and store it in out tempDict
            loopDict = self.connection.receive()

            print('--- DONE RECEIVING ---')
            # we call different methods depending on the result 
            # of the switch statement
            match loopDict['message_type']:

                # if we receive a handshake response,
                # we send a battle setup to the peer
                case 'HANDSHAKE_RESPONSE':
                    self.connection.send_ack(int(loopDict['sequence_number']))

                    # build pokemon before sending battle setup
                    pokemonChoice = IO.ask_pokemon()
                    tempPokemonData = Data.pokemonDataDictionary[pokemonChoice]
                    moveChoice = IO.ask_move()
                    self.bk.pokemon = Pokemon(tempPokemonData, Pokemon.make_move_tuple(moveChoice))
                    self.bk.health = self.bk.pokemon.pokemonData.hp

                    if not self.send_battle_setup():
                        self.terminate_battle()
                    else:
                        print('Joiner sent Battle Setup')

                # if we receive a battle setup we initialize the values
                # for the enemy pokemon, we check if the current peer
                # uses a HostTransport, if that is true then we make the user
                # choose a move then sends an attack announce
                case 'BATTLE_SETUP':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    self.bk.foe = Data.pokemonDataDictionary[loopDict['pokemon_name']]
                    self.foeHealth = self.bk.foe.hp
                           

                # if we receive an attack announce, we send the 
                # acknowledgement known as the defense announce
                case 'ATTACK_ANNOUNCE':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    self.bk.foeMove = Data.moveDictionary[loopDict['move_name'].lower()]
                    if not self.send_defense_announce():
                        self.terminate_battle()
                    else:
                        print('Joiner sent Attack Announce')

                # if we receive a defense announce, we send the 
                # acknowledgement known as the calculation report
                case 'DEFENSE_ANNOUNCE':
                    self.connection.send_ack()
                    if not self.send_calculation_report():
                        self.terminate_battle()
                    else:
                        print('Joiner sent Defense Announce')

                # if we receive a calculation report, we check
                # if the report matches our report, if it does
                # we apply the changes to our health, send a 
                # calculation confirm, and then have the previous 
                # defender make a move and send an attack announce
                # if it does not match we send our calculation 
                # through a resolution request
                case 'CALCULATION_REPORT':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    self.bk.foeDamage, multiplier = self.bk.pokemon.defender_calculation(self.bk.foeMove.name, self.bk.foe.name)
                    if self.bk.foeDamage == float(loopDict['damage_dealt']):
                        self.apply_own_hp_update()
                        if not self.send_calculation_confirm():
                            self.terminate_battle()
                        else:
                            print(loopDict['status_message'])

                    else:
                        if not self.send_resolution_request():
                            self.terminate_battle()
                        else: 
                            self.apply_own_hp_update()
                            print(loopDict['status_message'])

                # since this the end of the 4 way acknowledgement 
                # we just need to update the enemy hp
                case 'CALCULATION_CONFIRM':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    self.apply_enemy_hp_update()
                    if self.bk.foe.hp <= 0:
                        if not self.send_game_over():
                            self.terminate_battle()
                        else:
                            print(f'{self.bk.foe.name} is unable to battle')
                            print(f'The winner is {self.bk.pokemon.pokemonData.name}')
                            print('Program shutting down...')
                            self.connection.close()
                    else:
                        if not self.send_continue():
                            self.terminate_battle()

                # if we receive a resolution request, we need to
                # check if the recalculated damage matches the
                # received damage, if it does we send an ack and
                # update enemy health on our end, if it still doesnt
                # then we terminate the battle
                case 'RESOLUTION_REQUEST':
                    self.bk.damage, multiplier = self.bk.pokemon.attacker_calculation(self.bk.move.name, self.bk.foe.name)
                    if self.bk.damage == float(loopDict['damage_dealt']):
                        self.connection.send_ack(int(loopDict['sequence_number']))
                        self.apply_enemy_hp_update()
                        if self.bk.foe.hp <= 0:
                            if not self.send_game_over():
                                self.terminate_battle()
                            else:
                                print(f'{self.bk.foe.name} is unable to battle')
                                print(f'The winner is {self.bk.pokemon.pokemonData.name}')
                                print('Program shutting down...')
                                self.connection.close()
                        else:
                            if not self.send_continue():
                                self.terminate_battle()
                    else:
                        self.terminate_battle()
                
                # if we receive a game over message it means that
                # our pokemon fainted and the program shits down
                case 'GAME_OVER':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    print(f'{loopDict['loser']} is unable to battle.')
                    print(f'The winner of this match is {loopDict['winner']}')
                    print('Program shutting down...')
                    self.connection.close()
                    

                # we receive this when our pokemon can still fight
                # after receiving an attack
                case 'CONTINUE':
                    self.connection.send_ack(int(loopDict['sequence_number']))
                    moveIndex = IO.choose_attack(self.bk.pokemon.pokemonData.name, self.bk.pokemon.moveTuple)
                    self.bk.move = Data.moveDictionary[self.bk.pokemon.moveTuple[moveIndex].name.lower()]
                    if not self.send_attack_announce():
                        self.terminate_battle()
    """
    # if we receive a chat message, we first check if
    # its text or a sticker, idk what to do from there
    case 'CHAT_MESSAGE':
        self.connection.send_ack()
        match loopDict['content_type']:
            case 'TEXT':
            
            case 'STICKER':
    """
    def terminate_battle(self):
        print('Connection lost... battle over... shutting down...')
        self.connection.close()

    def send_handshake_request(self) -> bool:
        message = HandshakeRequest(self.connection.send_sequence_number).to_message_format()
        return self.connection.send(message)
    
    def send_handshake_response(self) -> bool:
        SQ.sequence_number += 1
        message = HandshakeResponse(sequence_number=SQ.sequence_number).to_message_format()
        return self.connection.send(message)

    def send_battle_setup(self) -> bool:
        sb = StatBoost(5,5)
        SQ.sequence_number += 1
        message = BattleSetup(sequence_number=SQ.sequence_number,
                            pokemon_name=self.bk.pokemon.pokemonData.name,
                            stat_boosts=sb
                            ).to_message_format()
        return self.connection.send(message)

    def send_attack_announce(self) -> bool:
        SQ.sequence_number += 1
        message = AttackAnnounce(sequence_number=SQ.sequence_number, move_name=self.bk.move.name).to_message_format()
        return self.connection.send(message)

    def send_defense_announce(self) -> bool:
        SQ.sequence_number += 1
        message = DefenseAnnounce(sequence_number=SQ.sequence_number).to_message_format()
        return self.connection.send(message)

    def send_calculation_report(self) -> bool:
        SQ.sequence_number += 1
        a = self.bk.pokemon.pokemonData.name
        b = self.bk.move.name
        self.bk.damage, multiplier = self.bk.pokemon.attacker_calculation(b, self.bk.foe.name)
        tempEnemyHP = self.bk.foe.hp - self.bk.damage
        tempMessage = f'{a} used {b}!'
        if multiplier >= 2:
            tempMessage += ' It was super effective!'
        elif multiplier <= 0.5:
            tempMessage += ' It was not very effective...'

        message = CalculationReport(sequence_number=SQ.sequence_number,
                                    attacker=a,
                                    move_used=b,
                                    remaining_health=self.bk.health,
                                    damage_dealt=self.bk.damage,
                                    defender_hp_remaining= tempEnemyHP,
                                    status_message=tempMessage
                                    ).to_message_format()
        return self.connection.send(message)

    def send_calculation_confirm(self):
        SQ.sequence_number += 1
        message = CalculationConfirm(sequence_number=SQ.sequence_number).to_message_format()
        return self.connection.send(message)

    def send_resolution_request(self):
        SQ.sequence_number += 1
        self.bk.foeDamage, multiplier = Pokemon.defender_calculation(self.bk.foeMove.name, self.bk.foe.name)
        tempHP = self.bk.health - self.bk.foeDamage
        message = ResolutionRequest(sequence_number=SQ.sequence_number,
                                    attacker=self.bk.foe.name,
                                    move_used=self.bk.foeMove.name,
                                    damage_dealt=self.bk.foeDamage,
                                    defender_hp_remaining=tempHP
                                    ).to_message_format()
        return self.connection.send(message)
    
    def send_game_over(self):
        SQ.sequence_number += 1
        message = GameOver(sequence_number=SQ.sequence_number,
                        winner=self.bk.pokemon.pokemonData.name,
                        loser=self.bk.foe.name
                        ).to_message_format()
        return self.connection.send(message)

    def send_continue(self):
        SQ.sequence_number += 1
        message = Continue(sequence_number=SQ.sequence_number).to_message_format()
        return self.connection.send(message)
    
    def send_battler_notification(self):
        SQ.sequence_number += 1
        message = BattlerNotification(sequence_number=SQ.sequence_number).to_message_format()
        return self.connection.send(message)

    def apply_enemy_hp_update(self):
        self.bk.foeHealth -= self.bk.damage

    def apply_own_hp_update(self):
        self.bk.health -= self.bk.foeDamage