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
    self.damage: float = None


    def start():
        # get the role of the user
        roleChoice = self.io.get_role()

        # get the pokemon of the user
        pokemonName = self.io.ask_pokemon().lower()
        tempPokemonData = Data.pokemonDataDictionary[pokemonName]

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
                    self.sendHandshakeResponse()

                # if we receive a handshake response,
                # we send a battle setup to the peer
                case 'HANDSHAKE_RESPONSE':
                    self.transport.send_ack()
                    self.sendBattleSetup(self.pokemon.pokemonData.name)

                # if we receive a battle setup we initialize the value
                # for the enemy pokemon, we check if the current peer
                # uses a HostTransport, if that is true then we make the user
                # choose a move then sends an attack announce
                case 'BATTLE_SETUP':
                    self.transport.send_ack()
                    self.enemyPokemon = Data.pokemonDataDictionary[loopDict[pokemon_name]]

                    if isinstance(self.transport, HostTransport):
                        self.sendBattleSetup(self.pokemon.pokemonData.name)
                        while True:
                            try:
                                tempDict = self.transport.receive()
                                if tempDict['message_type'] == "ACKNOWLEDGEMENT":
                                    moveIndex = self.io.choose_attack(self.pokemon.pokemonData.name, self.pokemon.moveTuple)
                                    self.sendAttackAnnounce(moveIndex)
                            except Exception as e:
                                print(f"Exception: {e}")

                # if we receive an attack announce, we send the 
                # acknowledgement known as the defense announce
                case 'ATTACK_ANNOUNCE':
                    self.transport.send_ack()
                    self.sendDefenseAnnounce()

                # if we receive a defense announce, we send the 
                # acknowledgement known as the calculation report
                case 'DEFENSE_ANNOUNCE':
                    self.transport.send_ack()
                    # function call to send a calculation report

                # if we receive a calculation report, we check
                # if the report matches our report
                case 'CALCULATION_REPORT':
                    self.transport.send_ack()
                    if # function call that compares contents of calculation report
                        # function call to make calculations
                        # function call to send a calculation confirm
                        # function call to have the user make a move
                        # function call to send an attack announce

                    else:
                        # function call to send resolution request

                # since this the end of the 4 way acknowledgement 
                # we dont have to do anything anymore
                case 'CALCULATION_CONFIRM':
                    self.transport.send_ack()
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

def sendHandshakeResponse(self):
    self.transport.sequenceNumber += 1
    message = HandshakeResponse(sequence_number=self.transport.sequenceNumber).to_message_format()
    self.transport.send_to_peer(message)

def sendBattleSetup(self, pokemonName: str):
    sb = StatBoost(5,5)
    self.transport.sequenceNumber += 1
    message = BattleSetup(sequence_number=self.transport.sequenceNumber,
                            pokemon_name=pokemonName, stat_boosts=sb).to_message_format()
    self.transport.send_to_peer(message)

def sendAttackAnnounce(self, moveIndex: int):
    self.transport.sequenceNumber += 1
    message = AttackAnnounce(sequence_number=self.transport.sequenceNumber, move_name=self.pokemon.moveTuple[moveIndex].name)
    self.transport.send_to_peer(message)

def sendCalculation(self):
    self.transport.sequenceNumber += 1
    message = CalculationReport(sequence_number=self.transport.sequenceNumber, 
                                what here)
    self.transport.send_to_peer(message)