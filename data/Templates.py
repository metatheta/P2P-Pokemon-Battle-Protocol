from dataclasses import dataclass
import Data

# made a data class to represent a pokemon
@dataclass
class PokemonData:
    name: str 
    hp: int 
    attack: int 
    defense: int
    spatt: int
    spdef: int
    type1: str
    type2: str

# made a data class to represent the type match ups
# if in a specific instance we choose .bug then we get how well the current instance does against bug
@dataclass(frozen=True)
class TypeMatchUps:
    type: str
    bug: float
    dark: float
    dragon: float
    electric: float
    fairy: float
    fighting: float
    fire: float 
    flying: float
    ghost: float
    grass: float
    ground: float
    ice: float
    normal: float
    poison: float
    psychic: float
    rock: float
    steel: float
    water: float

@dataclass(frozen=True)
class Move:
    category: str
    moveType: str
    name: str
    basePower: int
    
class Pokemon:
    def __init__(self, pokemonData, moves):
        self.pokemonData = pokemonData
        self.moves = moves

    def defenderCalculation(self, moveName: str, opponentName: str) -> float:
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
            
    def attackerCalculation(self, moveName: str, opponentName: str) -> float:
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


