from dataclasses import dataclass

# made a data class to represent a pokemon
@dataclass(frozen=True)
class Pokemon:
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
