from Data import Data
from Templates import Move

class IO:
    def get_role(self) -> int:
        print('Dear Trainer, welcome to the wonderful world of Pokemon')
        print('In this P2P game you will need to choose a role')
        self.print_role_list()
        choice = -1 
        while choice not in range(1, 4):
            try:
                choice = int(input('Please choose the number of the role you want: '))
            except ValueError:
                print("Invalid input. Please enter a number (1, 2, or 3).")
                choice = -1
        return choice
        
    def print_role_list(self):
        print('The choices are:')
        print('1] Host - sends a battle request')
        print('2] Joiner - waits for a host to send a battle request')
        print('3] Spectator - watches the battle but does not participate')

    def ask_pokemon(self) -> str:
        print('What Pokemon would you like to battle with?')
        pokemon = None
        while pokemon is None:
            pokemonName = input('Please enter the name: ').lower()
            pokemon = Data.pokemonDataDictionary.get(pokemonName)
        return pokemonName

    def ask_move(self, whichMoveNumber: int, moveDict: dict[Move]) -> str:
        print(f'What do you want move {whichMoveNumber} of your pokemon to be?')
        print('Choose from the list below:')
        self.print_moves(moveDict)
        move = None
        while move is None:
            moveName = input('Please enter the name of the move: ').lower()
            move = Data.moveDictionary.get(moveName)
        return moveName

    def print_moves(self, moveDict: dict[Move]):
        number = 1
        for key, move in moveDict.item():
            print(f'{number}] {move.name}')
            number += 1

    def choose_attack(self, pokemonName: str, moveTuple: tuple[Move]) -> int:
        print('You are attacking now!')
        print(f'Please choose an attack for {pokemonName} to use from the list below:')
        print(f"{pokemonName}'s moves:")
        count = 1
        for move in moveTuple:
            print(f'{count}] {move.name} is a {move.category} {move.moveType} move')
            count += 1
        choice = 0
        while choice not in range(1, 5):
            try:
                choice = int(input('Please choose the number of the role you want: '))
            except ValueError:
                print("Invalid input. Please enter a number (1, 2, 3, or 4).")
                choice = -1
        return choice - 1






    