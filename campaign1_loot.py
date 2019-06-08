import random
import json
from enum import IntEnum


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
            self.loot_options.append(loot_option_item.value)

    def get_random_item(self):
        return self.loot_options[random.randint(0, len(self.loot_options) - 1)]


class LootController:
    def __init__(self):
        self.junk = LootController.create_loot_option("junk")
        self.jewellery = LootController.create_loot_option("jewellery")
        self.crafting_item = LootController.create_loot_option("crafting_item")

    def get_junk(self):
        return self.junk.get_random_item()

    def get_jewellery(self):
        return self.jewellery.get_random_item()

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
        LootType.mundane: None,
        LootType.consumable: None,
        LootType.low_gol: lambda: random.randint(30, 80),
        LootType.jewellery: None,
        LootType.single_enchant_item: None,
        LootType.crafting_item: None,
        LootType.double_enchant_item: None,
        LootType.high_gold: None,
        LootType.prayer_stone: None,
    }
    while True:
        roll = get_int_from_str(input("\nLoot roll: "), random.randint(1, 8))
        if roll < 0:
            exit(0)
        loot_type = LOOT_TYPES.get(roll)
        print(loot_action_map.get(loot_type, lambda: str(roll) + " is not a valid option")())
