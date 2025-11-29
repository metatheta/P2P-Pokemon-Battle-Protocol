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

    def turn_message_into_dict(self, message: str) -> dict:
        tempDict = {}
        for line in message.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    tempDict[key.strip()] = value.strip()
        return tempDict

    def start():
        # get the role of the user
        roleChoice = self.io.get_role()

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
            message = self.transport.receive()
            loopDict = self.turnMessageIntoDict(message)

            # we call different methods depending on the result 
            # of the switch statement
            match loopDict['message_type']:

                # if we receive a handshake request, then we send a 
                # handshake response and start building a pokemon
                # to use for the battle, when the pokemon is done
                # we send a battle setup to the peer
                case 'HANDSHAKE_REQUEST':
                    self.sendHandshakeResponse()
                    # function call to build the pokemon
                    # function call to send a battle setup message the peer

                # if we receive a handshake response, then we start
                # building a pokemon to use for the battle, when the pokemon
                # is done we send a battle setup to the peer
                case 'HANDSHAKE_RESPONSE':
                    # function call to build the pokemon
                    # function call to send a battle setup message the peer

                # if we receive a battle setup, we check if the current peer
                # uses a HostTransport, if that is true then the peer makes
                # a move then sends an attack announce
                case 'BATTLE_SETUP':
                    if isinstance(self.transport, HostTransport):
                        # function call to have the user make a move
                        # function call to send an attack announce

                # if we receive an attack announce, we send the 
                # acknowledgement known as the defense announce
                case 'ATTACK_ANNOUNCE':
                    self.sendAcknowledgement(loopDict['sequence_number'])
                    self.sendDefenseAnnounce()

                # if we receive a defense announce, we send the 
                # acknowledgement known as the calculation report
                case 'DEFENSE_ANNOUNCE':
                    self.sendAcknowledgement(loopDict['sequence_number'])
                    # function call to send a calculation report

                # if we receive a calculation report, we check
                # if the report matches our report
                case 'CALCULATION_REPORT':
                    self.sendAcknowledgement(loopDict['sequence_number'])
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
                    self.sendAcknowledgement(loopDict['sequence_number'])
                    # print stuff idk

                # if we receive a resolution request, we need to
                # recalculate and resend the calculation report
                case 'RESOLUTION_REQUEST':
                    self.sendAcknowledgement(loopDict['sequence_number'])
                    # function call to make calculations
                    # function call to send a calculation report
                
                # if we receive a chat message, we first check if
                # its text or a sticker, idk what to do from there
                case 'CHAT_MESSAGE':
                    self.sendAcknowledgement(loopDict['sequence_number'])
                    match loopDict['content_type']:
                        case 'TEXT':
                        
                        case 'STICKER':
