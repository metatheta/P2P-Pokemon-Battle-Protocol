from networking.Transport import HostTransport
from networking.Transport import JoinerTransport
from networking.Messages import *
from ui.IO import IO
from data.Data import Data
from data.Pokemon import Pokemon
from data.Templates import PokemonData, Move, TypeMatchUps

class Peer(self):
    self.transport = None
    self.pokemon: Pokemon = None
    self.enemyPokemon: PokemonData = None
    self.io: IO = IO()
