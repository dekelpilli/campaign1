import random
import json
from enum import IntEnum
import pprint

DATA_DIR = "data/"


class LootType(IntEnum):
    junk = 1
    mundane = 2
    consumable = 3
    low_gold = 4
    ring = 5
    amulet = 6
    single_enchant_item = 7
    crafting_item = 8
    double_enchant_item = 9
    high_gold = 10
    prayer_stone = 11
    artifact = 12


LOOT_TYPES = dict()
for loot_type in LootType:
    LOOT_TYPES[loot_type.value] = loot_type


class LootOptionItem:
    def __init__(self, value, weighting, enabled, metadata):
        self.weighting = weighting
        self.value = value
        self.enabled = enabled
        self.metadata = metadata

    def get_weighting_value(self):
        return self.enabled * self.weighting


class LootOption:
    def __init__(self, name):
        self.name = name
        self.loot_options = []

    def add_item(self, loot_option_item):
        item_weighting = loot_option_item.get_weighting_value()
        for i in range(item_weighting):
            self.loot_options.append(loot_option_item)

    def get_random_item(self):
        return self.loot_options[random.randint(0, len(self.loot_options) - 1)]


class LootController:
    def __init__(self):
        self.junk = LootController.create_loot_option("junk")
        self.crafting_item = LootController.create_loot_option("crafting_item")
        self.mundane = LootController.create_loot_option("mundane")
        self.enchant = LootController.create_loot_option("enchant")

    def get_mundane(self):
        return self.mundane.get_random_item()

    def get_enchant(self):
        return self.enchant.get_random_item().value

    def get_weapon_enchant(self):
        enchantment = self.enchant.get_random_item()
        if "armour" in enchantment.metadata:
            return self.get_weapon_enchant()
        return enchantment.value

    def get_armour_enchant(self):
        enchantment = self.enchant.get_random_item()
        if "weapon" in enchantment.metadata:
            return self.get_weapon_enchant()
        return enchantment.value

    def get_crafting_item(self):
        return self.crafting_item.get_random_item().value

    def get_double_enchanted_item(self):
        base_type = self.mundane.get_random_item()
        if "weapon" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_weapon_enchant() \
                   + "\n\t" + self.get_weapon_enchant()

        if "armour" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_armour_enchant() \
                   + "\n\t" + self.get_armour_enchant()

        return base_type \
               + "\n\t" + self.get_enchant() \
               + "\n\t" + self.get_enchant()

    def get_single_enchanted_item(self):
        base_type = self.mundane.get_random_item()
        if "weapon" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_weapon_enchant()

        if "armour" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_armour_enchant()

        return base_type \
               + "\n\t" + self.get_enchant()

    def get_junk(self):
        return self.junk.get_random_item().value

    @staticmethod
    def create_loot_option(name):
        with open(DATA_DIR + name + ".json") as file:
            item_dicts = json.loads(file.read())
        loot_option_items = []
        for item_dict in item_dicts:
            loot_option_items.append(LootOptionItem(item_dict["value"],
                                                    item_dict.get("weighting", 10),
                                                    item_dict.get("enabled", True),
                                                    item_dict.get("metadata", None)))
        loot_option = LootOption(name)
        for loot_option_item in loot_option_items:
            loot_option.add_item(loot_option_item)

        return loot_option


def get_int_from_str(string, default_integer=None):
    try:
        return int(string)
    except ValueError:
        return default_integer


if __name__ == "__main__":
    loot_controller = LootController()
    loot_action_map = {
        LootType.junk: loot_controller.get_junk,
        LootType.mundane: loot_controller.get_mundane,
        LootType.consumable: None,
        LootType.low_gold: lambda: random.randint(30, 80),
        LootType.ring: None,
        LootType.amulet: None,
        LootType.single_enchant_item: loot_controller.get_single_enchanted_item,
        LootType.crafting_item: loot_controller.get_crafting_item,
        LootType.double_enchant_item: loot_controller.get_double_enchanted_item,
        LootType.high_gold: lambda: min(random.randint(100, 800), random.randint(100, 800)),
        LootType.prayer_stone: None,
        LootType.artifact: None
    }
    pp = pprint.PrettyPrinter(indent=4)
    count = 0
    while True:
        if count % 8 == 0:
            print("\n")
            pp.pprint(LOOT_TYPES)
            print("\t13: Random weapon enchant")
            print("\t14: Random armour enchant")
            print("\t15: Random enchant")
            print("\t16: Reload mods")
        roll = get_int_from_str(input("\nLoot roll: "), random.randint(1, 8))
        if roll < 0:
            exit(0)
        loot_type = LOOT_TYPES.get(roll)
        print(loot_action_map.get(loot_type, lambda: str(roll) + " is not a valid option")())
        count += 1
        if roll == 13:
            loot_controller.get_weapon_enchant()
        if roll == 14:
            loot_controller.get_armour_enchant()
        if roll == 15:
            loot_controller.get_enchant()
        if roll == 16:
            loot_controller = LootController()
