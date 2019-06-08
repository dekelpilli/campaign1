import random
import json
from enum import IntEnum


DATA_DIR = "data/"


class LootType(IntEnum):
    junk = 1
    mundane = 2
    consumable = 3
    low_gold = 4
    jewellery = 5
    single_enchant_item = 6
    crafting_item = 7
    high_gold = 8
    double_enchant_item = 9
    prayer_stone = 10


LOOT_TYPES = dict()
for loot_type in LootType:
    LOOT_TYPES[loot_type.value] = loot_type.name


class LootOptionItem:
    def __init__(self, value, weighting=10, enabled=True):
        self.weighting = weighting
        self.value = value
        self.enabled = enabled

    def get_weighting_value(self):
        return self.enabled * self.weighting


class LootOption:
    def __init__(self, max_weighting, name):
        self.max_weighting = max_weighting
        self.name = name
        self.loot_options = []

    @staticmethod
    def load_loot_options():
        pass  # TODO: load from file with matching name and population loot options list


class LootController:
    def __init__(self):
        pass  # TODO: load loot

    def get_junk(self):
        pass

    def get_jewellery(self):
        pass


if __name__ == "__main__":
    loot_controller = LootController()
    loot_action_map = {
        LootType.junk: loot_controller.get_junk,
        LootType.mundane: None,
        LootType.consumable: None,
        LootType.low_gold: (lambda: random.randint(30, 80)),
        LootType.jewellery: loot_controller.get_jewellery,
        LootType.single_enchant_item: None,
        LootType.crafting_item: None,
        LootType.prayer_stone: None
    }
    while True:
        roll = input("\nLoot roll: ")
        if roll == "" or roll == "0":
            roll = random.randint(1, 8)
        loot_type = LOOT_TYPES[int(roll)]
        print(loot_action_map[loot_type]())
