from data.Data import Data
from data.Templates import Move

class IO:
    def getRole(self) -> int:
        print('Dear Trainer, welcome to the wonderful world of Pokemon')
        print('In this P2P game you will need to choose a role')
        self.printRoleList()
        choice = -1 
        while choice not in range(1, 4):
            try:
                choice = int(input('Please choose the number of the role you want: '))
            except ValueError:
                print("Invalid input. Please enter a number (1, 2, or 3).")
                choice = -1
        return choice
        
    def printRoleList(self):
        print('The choices are:')
        print('1] Host - sends a battle request')
        print('2] Joiner - waits for a host to send a battle request')
        print('3] Spectator - watches the battle but does not participate')

    def askPokemon(self) -> str:
        print('What Pokemon would you like to battle with?')
        pokemon = None
        while pokemon is None:
            pokemonName = input('Please enter the name: ').lower()
            pokemon = Data.pokemonDataDictionary.get(pokemonName)
        return pokemonName

    def askMove(self, whichMoveNumber: int) -> str:
        print(f'What do you want move {whichMoveNumber} of your pokemon to be?')
        print('Choose from the list below:')
        self.printMoves()
        move = None
        while move is None:
            moveName = input('Please enter the name of the move: ').lower()
            move = Data.moveDictionary.get(moveName)
        return moveName

    def printMoves(self):
        number = 1
        for key, move in Data.moveDictionary:
            print(f'{number}] {move.name}')
            number += 1

    def chooseAttack(self, pokemonName: str, moveTuple: tuple[Move]) -> int:
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
        return choice






    