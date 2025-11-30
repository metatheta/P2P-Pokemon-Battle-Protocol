from Messages import CalculationConfirm
from Messages import StatBoost
from Messages import Message
from Transport import HostTransport
from Transport import JoinerTransport
from Messages import *
from IO import IO
from Data import Data
from Pokemon import Pokemon
from Templates import PokemonData, Move

class Peer():
    def __init__(self):
        self.transport = None
        self.pokemon: Pokemon = None
        self.enemyPokemon: PokemonData = None
        self.io: IO = IO()
        self.health: float = None
        self.enemyHealth: float = None
        self.move: Move = None
        self.enemyMove: Move = None
        self.damage: float = None
        self.enemyDamage: float = None


    def start(self):
        try:
            # get the role of the user
            roleChoice = self.io.get_role()

            # get the pokemon of the user
            pokemonName = self.io.ask_pokemon().lower()
            tempPokemonData = Data.pokemonDataDictionary[pokemonName]
            self.health = tempPokemonData.hp

            # ask the user for 4 moves
            localMoveDict = Data.moveDictionary
            tempMoveList = []

            for i in range(1,5):
                moveName = self.io.ask_move(i, localMoveDict).lower()
                tempMoveList.append(Data.moveDictionary[moveName])
                # remove a move that has already been picked
                del localMoveDict[moveName]

            print('stopped getting moves')
            # make the user's pokemon using the pokemon data and the moves received
            self.pokemon = Pokemon(tempPokemonData, tuple(tempMoveList))

            match roleChoice:
                case 1:
                    print('entered case')
                    self.transport = HostTransport(8168)
                    print('finished making transport object')
                    self.transport.broadcast()
                    print('Finished broadcasting')
                    self.main_loop()
                    print('entered main loop')
                case 2:
                    print('entered case')
                    self.transport = JoinerTransport(9279)
                    print('finished making transport object')
                    self.transport.wait_for_broadcast()
                    print('done receving broadcast')
                    self.main_loop()
                    print('entered main loop')
                case _:
                    print('No spectator yet')
        except Exception as e:
                print(f"Exception: {e}")

    def main_loop(self):
        print("--- MAIN LOOP STARTED ---")
        loopDict = {
                        'message_type': 'justToEnterLoop'
                   }

        
        while True:
            print('--- ENTERED WHILE TRUE---')
            # get the message from receive and store it in out tempDict
            loopDict = self.transport.receive()

            print('--- DONE RECEIVING ---')
            # we call different methods depending on the result 
            # of the switch statement
            match loopDict['message_type']:

                # if we receive a handshake request, then we send a 
                # handshake response
                case 'HANDSHAKE_REQUEST':
                    self.transport.send_ack()
                    if not self.send_handshake_response():
                        self.terminate_battle()

                # if we receive a handshake response,
                # we send a battle setup to the peer
                case 'HANDSHAKE_RESPONSE':
                    self.transport.send_ack()
                    if not self.send_battle_setup():
                        self.terminate_battle()

                # if we receive a battle setup we initialize the values
                # for the enemy pokemon, we check if the current peer
                # uses a HostTransport, if that is true then we make the user
                # choose a move then sends an attack announce
                case 'BATTLE_SETUP':
                    self.transport.send_ack()
                    self.enemyPokemon = Data.pokemonDataDictionary[loopDict[pokemon_name]]
                    self.enemyHealth = self.enemyPokemon.hp

                    if isinstance(self.transport, HostTransport):
                        if not self.send_battle_setup():
                            self.terminate_battle()
                        else:
                            moveIndex = self.io.choose_attack(self.pokemon.pokemonData.name, self.pokemon.moveTuple)
                            self.move = Data.moveDictionary[self.pokemon.moveTuple[moveIndex].name.lower()]
                            if not self.send_attack_announce():
                                self.terminate_battle()
                           

                # if we receive an attack announce, we send the 
                # acknowledgement known as the defense announce
                case 'ATTACK_ANNOUNCE':
                    self.transport.send_ack()
                    self.enemyMove = Data.moveDictionary[loopDict['move_name'].lower()]
                    if not self.send_defense_announce():
                        self.terminate_battle()

                # if we receive a defense announce, we send the 
                # acknowledgement known as the calculation report
                case 'DEFENSE_ANNOUNCE':
                    self.transport.send_ack()
                    if not self.send_calculation_report():
                        self.terminate_battle()

                # if we receive a calculation report, we check
                # if the report matches our report, if it does
                # we apply the changes to our health, send a 
                # calculation confirm, and then have the previous 
                # defender make a move and send an attack announce
                # if it does not match we send our calculation 
                # through a resolution request
                case 'CALCULATION_REPORT':
                    self.transport.send_ack()
                    self.enemyDamage, multiplier = self.pokemon.defender_calculation(self.enemyMove.name, self.enemyPokemon.name)
                    if self.enemyDamage == float(loopDict['damage_dealt']):
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
                    self.transport.send_ack()
                    self.apply_enemy_hp_update()
                    if self.enemyHealth <= 0:
                        if not self.send_game_over():
                            self.terminate_battle()
                        else:
                            print(f'{self.enemyPokemon.name} is unable to battle')
                            print(f'The winner is {self.pokemon.pokemonData.name}')
                            print('Program shutting down...')
                            self.transport.close()
                    else:
                        if not self.send_continue():
                            self.terminate_battle()

                # if we receive a resolution request, we need to
                # check if the recalculated damage matches the
                # received damage, if it does we send an ack and
                # update enemy health on our end, if it still doesnt
                # then we terminate the battle
                case 'RESOLUTION_REQUEST':
                    self.damage, multiplier = self.pokemon.attacker_calculation(self.move.name, self.enemyPokemon.name)
                    if self.damage == float(loopDict['damage_dealt']):
                        self.transport.send_ack()
                        self.apply_enemy_hp_update()
                        if self.enemyHealth <= 0:
                            if not self.send_game_over():
                                self.terminate_battle()
                            else:
                                print(f'{self.enemyPokemon.name} is unable to battle')
                                print(f'The winner is {self.pokemon.pokemonData.name}')
                                print('Program shutting down...')
                                self.transport.close()
                        else:
                            if not self.send_continue():
                                self.terminate_battle()
                    else:
                        self.terminate_battle()
                
                # if we receive a game over message it means that
                # our pokemon fainted and the program shits down
                case 'GAME_OVER':
                    self.transport.send_ack()
                    print(f'{loopDict['loser']} is unable to battle.')
                    print(f'The winner of this match is {loopDict['loser']}')
                    print('Program shutting down...')
                    self.transport.close()
                    

                # we receive this when our pokemon can still fight
                # after receiving an attack
                case 'CONTINUE':
                    moveIndex = self.io.choose_attack(self.pokemon.pokemonData.name, self.pokemon.moveTuple)
                    self.move = Data.moveDictionary[self.pokemon.moveTuple[moveIndex].name.lower()]
                    if not self.send_attack_announce():
                        self.terminate_battle()
"""
# if we receive a chat message, we first check if
# its text or a sticker, idk what to do from there
case 'CHAT_MESSAGE':
    self.transport.send_ack()
    match loopDict['content_type']:
        case 'TEXT':
        
        case 'STICKER':
"""
def terminate_battle(self):
    print('Connection lost... battle over... shutting down...')
    self.transport.close()

def send_handshake_response(self) -> bool:
    self.transport.sequenceNumber += 1
    message = HandshakeResponse(sequence_number=self.transport.sequenceNumber).to_message_format()
    return self.transport.send_to_peer(message)

def send_battle_setup(self) -> bool:
    sb = StatBoost(5,5)
    self.transport.sequenceNumber += 1
    message = BattleSetup(sequence_number=self.transport.sequenceNumber,
                          pokemon_name=self.pokemon.pokemonData.name, 
                          stat_boosts=sb
                        ).to_message_format()
    return self.transport.send_to_peer(message)

def send_attack_announce(self) -> bool:
    self.transport.sequenceNumber += 1
    message = AttackAnnounce(sequence_number=self.transport.sequenceNumber, move_name=self.move.name).to_message_format()
    return self.transport.send_to_peer(message)

def send_defense_announce(self) -> bool:
    self.transport.sequenceNumber += 1
    message = DefenseAnnounce(sequence_number=self.transport.sequenceNumber).to_message_format()
    return self.transport.send_to_peer(message)

def send_calculation_report(self) -> bool:
    self.transport.sequenceNumber += 1
    a = self.pokemon.pokemonData.name
    b = self.move.name
    self.damage, multiplier = self.pokemon.attacker_calculation(b, self.enemyPokemon.name)
    tempEnemyHP = self.enemyHealth - self.damage
    tempMessage = f'{a} used {b}!'
    if multiplier >= 2:
        tempMessage += ' It was super effective!'
    elif multiplier <= 0.5:
        tempMessage += ' It was not very effective...'

    message = CalculationReport(sequence_number=self.transport.sequenceNumber, 
                                attacker=a,
                                move_used=b,
                                remaining_health=self.pokemon.pokemonData.hp,
                                damage_dealt=self.damage,
                                defender_hp_remaining= tempEnemyHP,
                                status_message=tempMessage
                                ).to_message_format()
    return self.transport.send_to_peer(message)

def send_calculation_confirm(self):
    self.transport.sequenceNumber += 1
    message = CalculationConfirm(sequence_number=self.transport.sequenceNumber).to_message_format()
    return self.transport.send_to_peer(message)

def send_resolution_request(self):
    self.transport.sequenceNumber += 1
    self.enemyDamage, multiplier = self.pokemon.defender_calculation(self.enemyMove.name, self.enemyPokemon.name)
    tempHP = self.health - self.enemyDamage
    message = ResolutionRequest(sequence_number=self.transport.sequenceNumber,
                                attacker=self.enemyPokemon.name,
                                move_used=self.enemyMove.name,
                                damage_dealt=self.enemyDamage,
                                defender_hp_remaining=tempHP                         
                               ).to_message_format()
    return self.transport.send_to_peer(message)

def send_game_over(self):
    self.transport.sequenceNumber += 1
    message = GameOver( sequence_number=self.transport.sequenceNumber,
                        winner=self.pokemon.pokemonData.name,
                        loser=self.enemyPokemon.name
                        ).to_message_format()
    return self.transport.send_to_peer(message)

def send_continue(self):
    self.transport.sequenceNumber += 1
    message = Continue(sequence_number=self.transport.sequenceNumber).to_message_format()
    return self.transport.send_to_peer(message)

def apply_enemy_hp_update(self):
    self.enemyHealth -= self.damage

def apply_own_hp_update(self):
    self.health -= self.enemyDamage