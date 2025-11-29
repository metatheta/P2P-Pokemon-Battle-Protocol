import Peer
from data.Data import Data

if __name__ == '__main__':
    # readying the dictionaries
    Data.populate_match_ups()
    Data.populate_pokemon_data()

    p = Peer()
    p.start()