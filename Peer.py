from networking.Transport import HostTransport
from networking.Transport import JoinerTransport
from networking.Messages import *

class Peer:
    def __init__(self):
        self.transport = None
        self.name = None

    # a start method for the peer which gets the name
    # and the choice of the user that tells us if they want
    # to be a host or a joiner
    def start(self):
        self.name = input('What is your name: ')
        response = 10
        while response not in (0, 1):
            response = int(input("Enter '1' if you want to Host and '0' if you want to Join: "))

        # if they want to be a host we make transport a 
        # HostTransport object so they can broadcast 
        # an initiation for the game 
        if response == 1:
            self.transport = HostTransport(8168)
            self.transport.broadcast()
            self.mainLoop()

        # if they want to be a joiner we make transport a
        # JoinerTransport object so they can start waiting 
        # for a broadcast and immediately send the HandshakeRequest 
        # message to the broadcaster
        elif response == 0:
            self.transport = JoinerTransport(9279)
            self.transport.waitForBroadcast()
            self.transport.send(HandshakeRequest().toMessageFormat())
            self.mainLoop()

    # turns the string into a dictionary and returns
    # the dictionary
    def turnMessageIntoDict(self, message: str):
        tempDict = {}
        for line in message.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    tempDict[key.strip()] = value.strip()
        return tempDict
        
    # we place the peers in a constant state of receiving
    # which only breaks if the message_type is GAME_OVER
    # we then get the value of message_type to determine
    # switch statement well enter
    def mainLoop(self):
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
                    self.sendDefenseAnnounce()

                # if we receive a defense announce, we send the 
                # acknowledgement known as the calculation report
                case 'DEFENSE_ANNOUNCE':
                    # function call to send a calculation report

                # if we receive a calculation report, we check
                # if the report matches our report
                case 'CALCULATION_REPORT':
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
                    # print stuff idk

                # if we receive a resolution request, we need to
                # recalculate and resend the calculation report
                case 'RESOLUTION_REQUEST':
                    # function call to make calculations
                    # function call to send a calculation report
                
                # if we receive a chat message, we first check if
                # its text or a sticker, idk what to do from there
                case 'CHAT_MESSAGE':
                    match loopDict['content_type']:
                        case 'TEXT':
                        
                        case 'STICKER':




    def sendHandshakeResponse(self):
        message = HandshakeResponse().toMessageFormat()
        self.transport.sendToPeer(message)  

    def sendAttackAnnounce(self, movedUsed: str):
        sn = self.transport.updateAndGetSequenceNumber()
        message = AttackAnnounce(move_name=movedUsed, sequence_number=sn).toMessageFormat()
        self.transport.sendToPeer(message)

    def sendDefenseAnnounce(self):
        sn = self.transport.updateAndGetSequenceNumber()
        message = DefenseAnnounce(sequence_number=sn).toMessageFormat()
        self.transport.sendToPeer(message)

