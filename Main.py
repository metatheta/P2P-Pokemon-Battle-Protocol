from Peer import Peer
from Data import Data

if __name__ == '__main__':
    # readying the dictionaries
    Data.populate_match_ups()
    Data.populate_pokemon_data()

    Peer().start()
    print('Thank you for playing')
"""
    menu_text = "[1] Host\n[2] Join\n[3] Spectate\n[4] Exit Program"
    while True:
        print(menu_text)
        match input().strip():
            case "1":
                pass
            case "2":
                pass
            case "3":
                pass
            case "4":
                break
            case _:
                print("Please pick one of the choices.")
"""