import random
import json

############
# Potential improvements
############
# Turn if-elses into a dictionary returning first-class functions

DATA_DIR = "data/"

class LootController:
    def __init__(self):
        print("Loading...")
        self.mainTable = {}

        f = open(DATA_DIR + "junk.json")
        self.mainTable[1] = json.loads(f.read()) #junk
        f.close()
        
        self.mainTable[2] = None #lowGold
        
        f = open(DATA_DIR + "mundane.json")
        self.mainTable[3] = json.loads(f.read()) #mundane
        f.close()
        
        self.mainTable[4] = None #rations

        f = open(DATA_DIR + "genericPotion.json")
        self.mainTable[5] = json.loads(f.read()) #genericPotion
        f.close()
        
        f = open(DATA_DIR + "amulet.json")
        self.mainTable[6] = json.loads(f.read()) #amulet
        f.close()
        
        self.mainTable[7] = None #medGold

        self.mainTable[8] = None #crystal

        self.mainTable[9] = None #magic

        self.mainTable[10] = None #double enchant

        self.mainTable[11] = None #highGold

        self.mainTable[12] = None #magic thematic

        self.mainTable[13] = None #triple enchant

        self.mainTable[14] = None #double enchant thematic

        f = open(DATA_DIR + "contract.json")
        self.mainTable[15] = json.loads(f.read()) #contract stone
        f.close()

        self.mainTable[16] = ["Ra'Zi Rock"] #ra'zi rock

        self.mainTable[17] = ["Union Stone"] #union stone

        self.mainTable[18] = ["Glyph"] #glyph

        self.mainTable[19] = ["Fate Stone"] #fate stone

        self.mainTable[20] = ["Artifact + reroll"] #artifact + reroll

        f = open(DATA_DIR + "affix.json")
        affixes = json.loads(f.read())
        f.close()
        self.mainTable["weaponAffix"] = affixes["global"] + affixes["weapon"] #weaponAffix
        self.mainTable["armourAffix"] = affixes["global"] + affixes["armour"] #weaponAffix
        self.mainTable["jewelAffix"] = affixes["global"] #jewelAffix

        f = open(DATA_DIR + "crystal.json")
        self.mainTable["crystal"] = json.loads(f.read())
        f.close()

    def get(self,roll):
        try:
            print(random.choice(self.mainTable[int(roll)]))
        except (TypeError, KeyError) as e:
            roll = int(roll)
            if roll == 2:
                rand = random.randint(1,20)
                print("%i gold." %rand)
            elif roll == 4:
                rand = random.randint(1, 6)
                print("%i rations." %rand)
            elif roll == 7:
                rand = random.randint(51,70)
                print("%i gold." %rand)
            elif roll == 8:
                partyLevel = 1
                while True:
                    try:
                        partyLevel = int(input("Crystal. Enter party level: "))
                        break
                    except ValueError:
                        print("Party level must be an integer.")
                print("Contains random CR %f creature." %(self.getCrystalCr(partyLevel)))
            elif roll == 9:
                item = random.choice(self.mainTable[3])
                print("Magic item. Item type: %s." %(item))
            elif roll == 10:
                item = random.choice(self.mainTable[3])
                print("Double enchant. Item type: %s." %(item))
            elif roll == 11:
                rand = random.randint(151,170)
                print("%i gold." %rand)
            elif roll == 12:
                item = random.choice(self.mainTable[3])
                print("Thematic magic item. Item type: %s." %(item))
            elif roll == 13:
                item = random.choice(self.mainTable[3])
                print("Triple enchant. Item type: %s." %(item))
            elif roll == 14:
                item = random.choice(self.mainTable[3])
                print("Thematic double enchant. Item type: %s." %(item))
            else:
                print("Error? roll = %s" %roll)
        except ValueError:
            if roll == "relic":
                rolls = [random.randint(1,4), random.randint(1,4)]
                results = []
                for roll in rolls:
                    if roll <= 2:
                        results.append("upgrade")
                    elif roll <= 3:
                        results.append("new random")
                    else:
                        results.append("new thematic")
                print("Relic improvements: %s; %s" %(results[0], results[1]))
            elif roll == "wep":
                print(random.choice(self.mainTable["weaponAffix"]))
            elif roll == "arm":
                print(random.choice(self.mainTable["armourAffix"]))
            elif roll == "jew":
                print(random.choice(self.mainTable["jewelAffix"]))
            elif "crystal" in roll:
                queryBits = roll.split(" ")
                try:
                    monster = random.choice(list(self.mainTable["crystal"][queryBits[1]].keys()))
                    print(monster)
                    for idx in range(len(self.mainTable["crystal"][queryBits[1]][monster])):
                        print("%i. %s" %(idx+1, self.mainTable["crystal"][queryBits[1]][monster][idx]))
                except KeyError:
                    print("Crystal CR must be a valid CR value")
                except IndexError:
                    print("Crystal requires an argument (the crystal's CR)")
            else:
                print("Error? roll = %s" %roll)

    def getCrystalCr(self, lvl):
        crChoices = []
        for i in range(lvl+4):
            crChoices.append(0)
        for i in range(lvl+3):
            crChoices.append(1/8)
        for i in range(lvl+2):
            crChoices.append(1/4)
        for i in range(lvl+1):
            crChoices.append(1/2)
        for i in range(1, 21):
            for j in range(max(0, lvl+1 -i)):
                crChoices.append(i)
        return random.choice(crChoices)
                
if __name__ == "__main__":
    lc = LootController()
    while True:
        roll = input("\nLoot roll: ")
        if roll != "":
            if roll == "0":
                roll = random.randint(1,20)
            lc.get(roll)
