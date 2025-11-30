from Messages import CalculationConfirm
from Messages import StatBoost
from Messages import Message
from _typeshed import Self
from networking.Transport import HostTransport
from networking.Transport import JoinerTransport
from networking.Messages import *
from ui.IO import IO
from data.Data import Data
from data.Pokemon import Pokemon
from data.Templates import PokemonData, Move, TypeMatchUps

class Peer(self):
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


    def start():
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
            moveName = self.ui.ask_move(i, localMoveDict).lower()
            tempMoveList.append(Data.moveDictionary[moveName])
            # remove a move that has already been picked
            del localMoveDict[moveName]

        # make the user's pokemon using the pokemon data and the moves received
        self.pokemon = Pokemon(tempPokemonData, tuple(tempMoveList))

        match roleChoice:
            case 1:
                self.transport = HostTransport(8168)
                self.transport.broadcast()
                self.main_loop()
            case 2:
                self.transport = JoinerTransport(9279)
                self.transport.wait_for_broadcast()
                self.main_loop()
            case _:
                print('No spectator yet')

    def main_loop(self):
        loopDict = {
                        'message_type': 'justToEnterLoop'
                   }

        while(not loopDict['message_type'] == 'GAME_OVER'):

            # get the message from receive and store it in out tempDict
            loopDict = self.transport.receive()

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
                    if self.enemyDamage == float(loopDict['damage_dealth']):
                        self.apply_own_hp_update()
                        if not self.send_calculation_confirm():
                            self.terminate_battle()
                        else:
                            moveIndex = self.io.choose_attack(self.pokemon.pokemonData.name, self.pokemon.moveTuple)
                            self.move = Data.moveDictionary[self.pokemon.moveTuple[moveIndex].name.lower()]
                            if not self.send_attack_announce():
                                self.terminate_battle()

                    else:
                        if not self.send_resolution_request():
                            self.terminate_battle()

                # since this the end of the 4 way acknowledgement 
                # we just need to update the enemy hp
                case 'CALCULATION_CONFIRM':
                    self.transport.send_ack()
                    self.apply_enemy_hp_update()
                    # print stuff idk

                # if we receive a resolution request, we need to
                # recalculate and resend the calculation report
                case 'RESOLUTION_REQUEST':
                    self.transport.send_ack()
                    # function call to make calculations
                    # function call to send a calculation report
                
                # if we receive a chat message, we first check if
                # its text or a sticker, idk what to do from there
                case 'CHAT_MESSAGE':
                    self.transport.send_ack()
                    match loopDict['content_type']:
                        case 'TEXT':
                        
                        case 'STICKER':

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
    

def apply_enemy_hp_update(self):
    self.enemyHealth -= self.damage

def apply_own_hp_update(self):
    self.health -= self.enemyDamage