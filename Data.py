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
                        "flamethrower" : Move("Special", "Fire", "Flamethrower", 90),
                        "hydro pump": Move("Special", "Water", "Hydro Pump", 110),
                        "frenzy plant": Move("Special", "Grass", "Frenzy Plant", 150),
                        "thunderbolt": Move("Special", "Electric", "Thunderbolt", 90),
                        "aurora beam": Move("Special", "Ice", "Aurora Beam", 65),
                        "dark pulse": Move("Special", "Dark", "Dark Pulse", 80),
                        "future sight": Move("Special", "Psychic", "Future Sight", 120),
                        "dazzling gleam": Move("Special", "Fairy", "Dazzling Gleam", 80),
                        "hurricane": Move("Special", "Flying", "Hurricane", 110),
                        "pollen puff": Move("Special", "Bug", "Pollen Puff", 90),
                        "draco meteor": Move("Special", "Dragon", "Draco Meteor", 130),
                        "aura sphere": Move("Special", "Fighting", "Aura Sphere", 80),
                        "hex": Move("Special", "Ghost", "Hex", 65),
                        "mud shot": Move("Special", "Ground", "Mud Shot", 55),
                        "uproar": Move("Special", "Normal", "Uproar", 90),
                        "venoshock": Move("Special", "Poison", "Venoshock", 65),
                        "power gem": Move("Special", "Rock", "Power Gem", 80),
                        "flash cannon": Move("Special", "Steel", "Flash Cannon", 80),
                        "flame charge": Move("Physical", "Fire", "Flame Charge", 90),
                        "aqua jet": Move("Physical", "Water", "Aqua Jet", 110),
                        "leaf blade": Move("Physical", "Grass", "Leaf Blade", 150),
                        "volt tackle": Move("Physical", "Electric", "Volt Tackle", 90),
                        "glacial lance": Move("Physical", "Ice", "Glacial Lance", 65),
                        "night slash": Move("Physical", "Dark", "Night Slash", 80),
                        "psyblade": Move("Physical", "Psychic", "Psyblade", 120),
                        "play rough": Move("Physical", "Fairy", "Play Rough", 80),
                        "drill peck": Move("Physical", "Flying", "Drill Peck", 110),
                        "fell stinger": Move("Physical", "Bug", "Fell Stinger", 90),
                        "dragon rush": Move("Physical", "Dragon", "Dragon Rush", 130),
                        "hammer arm": Move("Physical", "Fighting", "Hammer Arm", 80),
                        "poltergeist": Move("Physical", "Ghost", "Poltergeist", 65),
                        "earthquake": Move("Physical", "Ground", "Earthquake", 55),
                        "giga impact": Move("Physical", "Normal", "Giga Impact", 90),
                        "cross poison": Move("Physical", "Poison", "Cross Poison", 65),
                        "stone edge": Move("Physical", "Rock", "Stone Edge", 80),
                        "iron head": Move("Physical", "Steel", "Iron Head", 80)
                     }
    # method to get the matchUp multiplicity given the 
    # attacker's type and the defender's type
    @staticmethod
    def get_match_up_multiplier(attackerType: str, defenderType: str):
        defender_matchups = Data.matchUpDictionary[defenderType.lower()]
        return getattr(defender_matchups, attackerType.lower())
    
    # method that reads all the pokemon from the csv file
    @staticmethod
    def populate_pokemon_data():
        with open('pokemon.csv', 'r', encoding='utf-8') as file:
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
    @staticmethod
    def populate_match_ups():
        with open('pokemon.csv', 'r', encoding='utf-8') as file:
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