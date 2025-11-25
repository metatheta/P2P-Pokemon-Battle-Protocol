import csv
from Templates import PokemonData
from Templates import TypeMatchUps
from Templates import Move
import random

# a class the Host and Joiner Peers can use
# the host calls populatePokemon() and populateMatchUps() once
# now every peer (except spectator) can access the pokemon and matchUps
class Data:
    # static dictionaries for everyones use
    pokemonDataDictionary = {}
    matchUpDictionary = {}
    moveDictionary = {
                        "special fire" : Move("Special", "Fire", "Flamethrower", random.randint(80, 100)),
                        "special water": Move("Special", "Water", "Hydro Pump", random.randint(80, 100)),
                        "special grass": Move("Special", "Grass", "Frenzy Plant", random.randint(80, 100)),
                        "special electric": Move("Special", "Electric", "Thunderbolt", random.randint(80, 100)),
                        "special ice": Move("Special", "Ice", "Aurora Beam", random.randint(80, 100)),
                        "special dark": Move("Special", "Dark", "Dark Pulse", random.randint(80, 100)),
                        "special psychic": Move("Special", "Psychic", "Future Sight", random.randint(80, 100)),
                        "special fairy": Move("Special", "Fairy", "Dazzling Gleam", random.randint(80, 100)),
                        "special flying": Move("Special", "Flying", "Hurricane", random.randint(80, 100)),
                        "special bug": Move("Special", "Bug", "Pollen Puff", random.randint(80, 100)),
                        "special dragon": Move("Special", "Dragon", "Draco Meteor", random.randint(80, 100)),
                        "special fighting": Move("Special", "Fighting", "Aura Sphere", random.randint(80, 100)),
                        "special ghost": Move("Special", "Ghost", "Hex", random.randint(80, 100)),
                        "special ground": Move("Special", "Ground", "Mud Shot", random.randint(80, 100)),
                        "special normal": Move("Special", "Normal", "Uproar", random.randint(80, 100)),
                        "special poison": Move("Special", "Poison", "Venoshock", random.randint(80, 100)),
                        "special rock": Move("Special", "Rock", "Power Gem", random.randint(80, 100)),
                        "special steel": Move("Special", "Steel", "Flash Cannon", random.randint(80, 100)),
                        "physical fire": Move("Physical", "Fire", "Flame Charge", random.randint(80, 100)),
                        "physical water": Move("Physical", "Water", "Aqua Jet", random.randint(80, 100)),
                        "physical grass": Move("Physical", "Grass", "Leaf Blade", random.randint(80, 100)),
                        "physical electric": Move("Physical", "Electric", "Volt Tackle", random.randint(80, 100)),
                        "physical ice": Move("Physical", "Ice", "Glacial Lance", random.randint(80, 100)),
                        "physical dark": Move("Physical", "Dark", "Night Slash", random.randint(80, 100)),
                        "physical psychic": Move("Physical", "Psychic", "Psyblade", random.randint(80, 100)),
                        "physical fairy": Move("Physical", "Fairy", "Play Rough", random.randint(80, 100)),
                        "physical flying": Move("Physical", "Flying", "Drill Peck", random.randint(80, 100)),
                        "physical bug": Move("Physical", "Bug", "Fell Stinger", random.randint(80, 100)),
                        "physical dragon": Move("Physical", "Dragon", "Dragon Rush", random.randint(80, 100)),
                        "physical fighting": Move("Physical", "Fighting", "Hammer Arm", random.randint(80, 100)),
                        "physical ghost": Move("Physical", "Ghost", "Poltergeist", random.randint(80, 100)),
                        "physical ground": Move("Physical", "Ground", "Earthquake", random.randint(80, 100)),
                        "physical normal": Move("Physical", "Normal", "Giga Impact", random.randint(80, 100)),
                        "physical poison": Move("Physical", "Poison", "Cross Poison", random.randint(80, 100)),
                        "physical rock": Move("Physical", "Rock", "Stone Edge", random.randint(80, 100)),
                        "physical steel": Move("Physical", "Steel", "Iron Head", random.randint(80, 100))
                     }
    # method to get the matchUp multiplicity given the 
    # attacker's type and the defender's type
    @staticmethod
    def matchUpMultiplier(attackerType: str, defenderType: str):
        defender_matchups = Data.matchUpDictionary[defenderType.lower()]
        return getattr(defender_matchups, attackerType.lower())
    
    # method that reads all the pokemon from the csv file
    def populatePokemonData(self):
        with open('pokemon.csv', 'r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:

                name = row["name"]
                hp = float(row["hp"])
                attack = float(row["attack"])
                defense = float(row["defense"])
                spatt = float(row["sp_attack"])
                spdef = float(row["sp_defense"])
                type1 = row["type1"]
                type2 = row["type2"]

                p = PokemonData(name, hp, attack, defense, spatt, spdef, type1, type2)

                Data.pokemonDataDictionary[name.lower()] = p
    
    # methods that reads the first 18 monotype pokemon
    # from the csv and records the type match up
    def populateMatchUps(self):
        with open('pokemon.csv', 'r') as file:
            reader = csv.DictReader(file)

            typesToComplete = ["bug", "dark", "dragon", "electric", "fairy", "fighting", "fire", "flying",
                                "ghost", "grass", "ground", "ice", "normal", "poison", "psychic", "rock", "steel", "water"]
            
            for row in reader:

                firstType = row["type1"]

                if firstType in typesToComplete and not row["type2"]:
                
                    bug = float(row["against_bug"])
                    dark = float(row["against_dark"])
                    dragon = float(row["against_dragon"])
                    electric = float(row["against_electric"])
                    fairy = float(row["against_fairy"])
                    fighting = float(row["against_fight"])
                    fire = float(row["against_fire"])
                    flying = float(row["against_flying"])
                    ghost = float(row["against_ghost"])
                    grass = float(row["against_grass"])
                    ground = float(row["against_ground"])
                    ice = float(row["against_ice"])
                    normal = float(row["against_normal"])
                    poison = float(row["against_poison"])
                    psychic = float(row["against_psychic"])
                    rock = float(row["against_rock"])
                    steel = float(row["against_steel"])
                    water = float(row["against_water"])

                    t = TypeMatchUps(firstType, bug, dark, dragon, electric, fairy, fighting, fire, flying,
                                        ghost, grass, ground, ice, normal, poison, psychic, rock, steel, water)
                    
                    Data.matchUpDictionary[firstType.lower()] = t

                    typesToComplete.remove(firstType)

                    # exit loop if no types left to complete
                    if len(typesToComplete) == 0:
                        break