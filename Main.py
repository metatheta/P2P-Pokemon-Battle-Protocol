from Connections import PeerConnection
from Data import Data
from HostPeer import HostPeer
from JoinerPeer import JoinerPeer
from SpectatorPeer import SpectatorPeer
from IO import IO

if __name__ == '__main__':
    # readying the dictionaries
    Data.populate_match_ups()
    Data.populate_pokemon_data()

    choice = IO.get_role()
    match choice:
        case 1:
            hostPeer = HostPeer()
            print('End of the game, thank you for playing')
        case 2:
            connection = PeerConnection(0)
            print("Waiting for host broadcast...")
            if connection.wait_for_broadcast():
                choice = IO.get_connector_role()
                match choice:
                    case 1:
                        print("Starting as Spectator...")
                        spectator = SpectatorPeer(connection)
                    case 2:
                        print("Starting as Battler...")
                        joiner = JoinerPeer(connection)
