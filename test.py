import IO
import Pokemon
import Data

Data.Data.populate_pokemon_data()
Data.Data.populate_match_ups()


io = IO.IO()

# get pokemon and moves for player 1
chosenPokemon = io.ask_pokemon()
chosenMoves = io.ask_move()

# make pokemon for player 1
p1 = Pokemon.Pokemon(Data.Data.pokemonDataDictionary[chosenPokemon], Pokemon.Pokemon.make_move_tuple(chosenMoves))

# get pokemon and moves for player 2
chosenPokemon = io.ask_pokemon()
chosenMoves = io.ask_move()

# make pokemon for player 2
p2 = Pokemon.Pokemon(Data.Data.pokemonDataDictionary[chosenPokemon], Pokemon.Pokemon.make_move_tuple(chosenMoves))

p1Turn = True
attackChoice: int
attackName: str
damage: float
enemyName: str

while p1.health > 0 and p2.health > 0:

    if p1Turn:
        print('Player 1:')
        attackChoice = io.choose_attack(p1.pokemonData.name, p1.moveTuple)
        attackName = p1.moveTuple[attackChoice].name
        enemyName = p2.pokemonData.name
        print(f'{p1.pokemonData.name} used {attackName} on {enemyName}')
        damage, multiplier = p1.attacker_calculation(attackName, enemyName)
        p2.health -= damage
        print(f'{enemyName} only has {p2.health} left')
    else:
        print('Player 2:')
        attackChoice = io.choose_attack(p2.pokemonData.name, p2.moveTuple)
        attackName = p2.moveTuple[attackChoice].name
        enemyName = p1.pokemonData.name
        print(f'{p2.pokemonData.name} used {attackName} on {enemyName}')
        damage, multiplier = p2.attacker_calculation(attackName, enemyName)
        p1.health -= damage
        print(f'{enemyName} only has {p1.health} left')

    p1Turn = not p1Turn