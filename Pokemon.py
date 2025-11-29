from Data import Data
from Templates import Move, PokemonData

class Pokemon:
    def __init__(self, pokemonData: PokemonData, moveTuple: tuple[Move]):
        self.pokemonData = pokemonData
        self.moveTuple = moveTuple

    def defender_calculation(self, moveName: str, opponentName: str) -> float:
        move = Data.moveDictionary[moveName.lower()]
        damage: float = 1.0
        opponent = Data.pokemonDataDictionary[opponentName.lower()]
        damageMultiplier = 1.0

        # if the move is of the special category
        if move.category == 'Special':
            # calculate the damage using the opponent pokemon's spatt and the spdef of the user's pokemon
            damage = (
                move.basePower * 
                opponent.spatt *
                Data.get_match_up_multiplier(move.moveType.lower(), self.pokemonData.type1.lower()) /
                self.pokemonData.spdef 
            )

        else:
            # calculate the damage using the opponent pokemon's attck and the defense of the user's pokemon
            damage = (
                move.basePower * 
                opponent.attack *
                Data.get_match_up_multiplier(move.moveType.lower(), self.pokemonData.type1.lower()) /
                self.pokemonData.defense 
            )
            
        damageMultiplier *= Data.get_match_up_multiplier(move.moveType.lower(), self.pokemonData.type1.lower())

         # if the user's pokemon has a secondary type, multiply it by the corresponding match up multiplier
        if self.pokemonData.type2:
            damage *= Data.get_match_up_multiplier(move.moveType.lower(), self.pokemonData.type2.lower())
            damageMultiplier *= Data.get_match_up_multiplier(move.moveType.lower(), self.pokemonData.type2.lower())

        return round(damage, 2), damageMultiplier
            
    def attacker_calculation(self, moveName: str, opponentName: str) -> float:
        move = Data.moveDictionary[moveName.lower()]
        damage: float = 1.0
        opponentName = opponentName.lower()
        opponent = Data.pokemonDataDictionary[opponentName.lower()]
        damageMultiplier = 1.0


        # if the move is of the special category
        if move.category == 'Special':
            # calculate the damage using the opponent pokemon's spdef and the spatt of the user's pokemon
            damage = (
                move.basePower * 
                self.pokemondata.spatt *
                Data.get_match_up_multiplier(move.moveType.lower(), opponent.type1.lower()) /
                opponent.spdef 
            )

        else:
            # calculate the damage using the opponent pokemon's defense and the attack of the user's pokemon
            damage = (
                move.basePower * 
                self.pokemondata.attack *
                Data.get_match_up_multiplier(move.moveType.lower(), opponent.type1.lower()) /
                opponent.defense 
            )
            
        damageMultiplier *= Data.get_match_up_multiplier(move.moveType.lower(), opponent.type1.lower())

         # if the opponent's pokemon has a secondary type, multiply it by the corresponding match up multiplier
        if opponent.type2:
            damage *= Data.get_match_up_multiplier(move.moveType.lower(), opponent.type2.lower())
            damageMultiplier *= Data.get_match_up_multiplier(move.moveType.lower(), opponent.type2.lower())

        return round(damage, 2), damageMultiplier
