from Pokemon import Pokemon
from Data import PokemonData
from Data import Move

# just a wrapper class to contain all the
# essential data stored when battling
# because Host and the first Connector are
# the ones battling, only they have this object
class BattlerKit():
    def __init__(self):
        self.move: Move = None
        self.foeMove: Move = None
        self.damage: float = None
        self.foeDamage: float = None
        self.pokemon: Pokemon = None
        self.foe: PokemonData = None
        self.health: float = None
        self.foeHealth:float = None