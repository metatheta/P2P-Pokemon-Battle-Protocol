import csv
from Templates import PokemonData, TypeMatchUps, Move 
import random

# a class the Host and Joiner Peers can use
# the host calls populatePokemon() and populateMatchUps() once
# now every peer (except spectator) can access the pokemon and matchUps
class Data:
    # static dictionaries for everyones use
    pokemonDataDictionary = {}
    matchUpDictionary = {}
    moveDictionary = {
                        "flamethrower" : Move("Special", "Fire", "Flamethrower", random.randint(80, 100)),
                        "hydro pump": Move("Special", "Water", "Hydro Pump", random.randint(80, 100)),
                        "frenzy plant": Move("Special", "Grass", "Frenzy Plant", random.randint(80, 100)),
                        "thunderbolt": Move("Special", "Electric", "Thunderbolt", random.randint(80, 100)),
                        "aurora beam": Move("Special", "Ice", "Aurora Beam", random.randint(80, 100)),
                        "dark pulse": Move("Special", "Dark", "Dark Pulse", random.randint(80, 100)),
                        "future sight": Move("Special", "Psychic", "Future Sight", random.randint(80, 100)),
                        "dazzling gleam": Move("Special", "Fairy", "Dazzling Gleam", random.randint(80, 100)),
                        "hurricane": Move("Special", "Flying", "Hurricane", random.randint(80, 100)),
                        "pollen puff": Move("Special", "Bug", "Pollen Puff", random.randint(80, 100)),
                        "draco meteor": Move("Special", "Dragon", "Draco Meteor", random.randint(80, 100)),
                        "aura sphere": Move("Special", "Fighting", "Aura Sphere", random.randint(80, 100)),
                        "hex": Move("Special", "Ghost", "Hex", random.randint(80, 100)),
                        "mud shot": Move("Special", "Ground", "Mud Shot", random.randint(80, 100)),
                        "uproar": Move("Special", "Normal", "Uproar", random.randint(80, 100)),
                        "venoshock": Move("Special", "Poison", "Venoshock", random.randint(80, 100)),
                        "power gem": Move("Special", "Rock", "Power Gem", random.randint(80, 100)),
                        "flash cannon": Move("Special", "Steel", "Flash Cannon", random.randint(80, 100)),
                        "flame charge": Move("Physical", "Fire", "Flame Charge", random.randint(80, 100)),
                        "aqua jet": Move("Physical", "Water", "Aqua Jet", random.randint(80, 100)),
                        "leaf blade": Move("Physical", "Grass", "Leaf Blade", random.randint(80, 100)),
                        "volt tackle": Move("Physical", "Electric", "Volt Tackle", random.randint(80, 100)),
                        "glacial lance": Move("Physical", "Ice", "Glacial Lance", random.randint(80, 100)),
                        "night slash": Move("Physical", "Dark", "Night Slash", random.randint(80, 100)),
                        "psyblade": Move("Physical", "Psychic", "Psyblade", random.randint(80, 100)),
                        "play rough": Move("Physical", "Fairy", "Play Rough", random.randint(80, 100)),
                        "drill peck": Move("Physical", "Flying", "Drill Peck", random.randint(80, 100)),
                        "fell stinger": Move("Physical", "Bug", "Fell Stinger", random.randint(80, 100)),
                        "dragon rush": Move("Physical", "Dragon", "Dragon Rush", random.randint(80, 100)),
                        "hammer arm": Move("Physical", "Fighting", "Hammer Arm", random.randint(80, 100)),
                        "poltergeist": Move("Physical", "Ghost", "Poltergeist", random.randint(80, 100)),
                        "earthquake": Move("Physical", "Ground", "Earthquake", random.randint(80, 100)),
                        "giga impact": Move("Physical", "Normal", "Giga Impact", random.randint(80, 100)),
                        "cross poison": Move("Physical", "Poison", "Cross Poison", random.randint(80, 100)),
                        "stone edge": Move("Physical", "Rock", "Stone Edge", random.randint(80, 100)),
                        "iron head": Move("Physical", "Steel", "Iron Head", random.randint(80, 100))
                     }
    # method to get the matchUp multiplicity given the 
    # attacker's type and the defender's type
    @staticmethod
    def get_match_up_multiplier(attackerType: str, defenderType: str):
        defender_matchups = Data.matchUpDictionary[defenderType.lower()]
        return getattr(defender_matchups, attackerType.lower())
    
    # method that reads all the pokemon from the csv file
    def populate_pokemon_data(self):
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

                p = PokemonData(name, hp, attack, defense, spatt, spdef, type1.capitalize(), type2.capitalize())

                Data.pokemonDataDictionary[name.lower()] = p
    
    # methods that reads the first 18 monotype pokemon
    # from the csv and records the type match up
    def populate_match_ups(self):
        with open('pokemon.csv', 'r') as file:
            reader = csv.DictReader(file)

            typesToComplete = ["bug", "dark", "dragon", "electric", "fairy", "fighting", "fire", "flying",
                                "ghost", "grass", "ground", "ice", "normal", "poison", "psychic", "rock", "steel", "water"]
            
            for row in reader:

                firstType = row["type1"].lower()

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

                    t = TypeMatchUps(firstType.capitalize(), bug, dark, dragon, electric, fairy, fighting, fire, flying,
                                        ghost, grass, ground, ice, normal, poison, psychic, rock, steel, water)
                    
                    Data.matchUpDictionary[firstType] = t

                    typesToComplete.remove(firstType)

                    # exit loop if no types left to complete
                    if len(typesToComplete) == 0:
                        break