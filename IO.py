from Data import Data
from Templates import Move
import re

class IO:
    @staticmethod
    def get_role() -> int:
        print('Dear Trainer, welcome to the wonderful world of Pokemon')
        print('In this P2P game you will need to choose a role')
        IO.print_role_list()
        choice = -1 
        while choice not in range(1, 3):
            try:
                choice = int(input('Please choose the number of the role you want: '))
            except ValueError:
                print("Invalid input. Please enter a number (1 or 2)")
                choice = -1
        return choice
        
    @staticmethod
    def print_role_list():
        print('The choices are:')
        print('1] Host - sends a battle request')
        print('2] Connector - waits for a host to send a battle request')

    @staticmethod
    def get_connector_role() -> int:
        print('Choose a role as a non-host:')
        print('1] Spectator')
        print('2] Battler')

        answer = int(input('Please enter the number of your choice: '))
        while answer not in range(1, 3):
            try:
                answer = int(input('Please enter the number of your choice: '))
            except ValueError:
                print("Invalid input. Please enter a number (1 or 2)")
                answer = -1
        return answer

    @staticmethod
    def ask_pokemon() -> str:
        print('What Pokemon would you like to battle with?')
        pokemon = None
        while pokemon is None:
            pokemonName = input('Please enter the name: ').lower()
            pokemon = Data.pokemonDataDictionary.get(pokemonName)
        return pokemonName

    @staticmethod
    def ask_move() -> str:
        print('What moves do you want your pokemon to have?')
        print('Choose from the list below:')
        IO.print_moves()
        while True:
            answer = input('Enter 4 appropriate numbers separated by commas: ')
            try:
                nums = [int(x) for x in answer.split(',')]
            except ValueError:
                continue
            check = lambda x: 0 < x <= 36
            if len(nums) != 4 or len(nums) != len(set(nums)):
                continue
            if not all(check(x) for x in nums):
                continue
            break
        return answer

    @staticmethod
    def print_moves():
        moveDict = Data.moveDictionary
        number = 1
        row = ""

        for key, move in moveDict.items():
            row += f"{number}] {move.name:<25}"

            if number % 3 == 0:
                print(row)
                row = ""

            number += 1

    @staticmethod
    def choose_attack(pokemonName: str, moveTuple: tuple[Move]) -> int:
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
                choice = int(input('Please choose the number of the move you want: '))
            except ValueError:
                print("Invalid input. Please enter a number (1, 2, 3, or 4).")
                choice = -1
        return choice - 1






    