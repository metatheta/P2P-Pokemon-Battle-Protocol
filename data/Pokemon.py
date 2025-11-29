from Data import Data
from Templates import Move, PokemonData

class Pokemon:
    def __init__(self, pokemonData: PokemonData, moveTuple: tuple[Move]):
        self.pokemonData = pokemonData
        self.moveTuple = moveTuple

    def defender_calculation(self, moveName: str, opponentName: str) -> float:
        move = Data.moveDictionary[moveName.lower()]
        damage: float = 0.0
        opponentName = opponentName.lower()

        # if the move is of the special category
        if move.category == 'Special':
            # calculate the damage using the opponent pokemon's spatt and the spdef of the user's pokemon
            damage = (
                move.basePower * 
                Data.pokemonDataDictionary[opponentName].pokemondata.spatt *
                getattr(Data.matchUpDictionary[self.pokemonData.type1.lower()], move.moveType.lower()) / 
                self.pokemonData.spdef 
            )

        else:
            # calculate the damage using the opponent pokemon's attck and the defense of the user's pokemon
            damage = (
                move.basePower * 
                Data.pokemonDataDictionary[opponentName].pokemondata.attack *
                getattr(Data.matchUpDictionary[self.pokemonData.type1.lower()], move.moveType.lower()) / 
                self.pokemonData.defense 
            )
            
         # if the user's pokemon has a secondary type, multiply it by the corresponding match up multiplier
        if self.pokemonData.type2:
            damage *= getattr(Data.matchUpDictionary[self.pokemonData.type2.lower()], move.moveType.lower())

        return damage
            
    def attacker_calculation(self, moveName: str, opponentName: str) -> float:
        move = Data.moveDictionary[moveName.lower()]
        damage: float = 0.0
        opponentName = opponentName.lower()

        # if the move is of the special category
        if move.category == 'Special':
            # calculate the damage using the opponent pokemon's spdef and the spatt of the user's pokemon
            damage = (
                move.basePower * 
                self.pokemondata.spatt *
                getattr(Data.matchUpDictionary[Data.pokemonDictionary[opponentName].pokemonData.type1.lower()], move.moveType.lower()) / 
                Data.pokemonDataDictionary[opponentName].pokemonData.spdef 
            )

        else:
            # calculate the damage using the opponent pokemon's defense and the attack of the user's pokemon
            damage = (
                move.basePower * 
                self.pokemondata.attack *
                getattr(Data.matchUpDictionary[Data.pokemonDictionary[opponentName].pokemonData.type1.lower()], move.moveType.lower()) / 
                Data.pokemonDataDictionary[opponentName].pokemonData.defense 
            )
            
         # if the opponent's pokemon has a secondary type, multiply it by the corresponding match up multiplier
        if Data.pokemonDictionary[opponentName].pokemonData.type2:
            damage *= getattr(Data.matchUpDictionary[Data.pokemonDictionary[opponentName].pokemonData.type2.lower()], move.moveType.lower())

        return damage        
