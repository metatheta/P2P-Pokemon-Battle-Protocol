import csv
from Templates import Pokemon
from Templates import TypeMatchUps

# a class the Host and Joiner Peers can use
# the host calls populatePokemon() and populateMatchUps() once
# now every peer (except spectator) can access the pokemon and matchUps
class Data:
    pokemonDictionary = {}
    matchUpDictionary = {}

    def populatePokemon(self):
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

                p = Pokemon(name, hp, attack, defense, spatt, spdef, type1, type2)

                Data.pokemonDictionary[name] = p
    
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
                    
                    Data.matchUpDictionary[firstType] = t

                    typesToComplete.remove(firstType)

                    if len(typesToComplete) == 0:
                        break