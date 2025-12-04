from Data import Data
from HostPeer import HostPeer
from ConnectorPeer import ConnectorPeer
from IO import IO

if __name__ == '__main__':
    # readying the dictionaries
    Data.populate_match_ups()
    Data.populate_pokemon_data()

    choice = IO.get_role()
    match choice:
        case 1:
            hostPeer = HostPeer()
        case 2:
            connectorPeer = ConnectorPeer()
            connectorPeer.main_loop()
    