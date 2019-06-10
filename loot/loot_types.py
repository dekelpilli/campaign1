import random
from enum import IntEnum


class LootType(IntEnum):
    junk = 1
    mundane = 2
    consumable = 3
    low_gold = 4
    ring = 5
    single_enchant_item = 6
    amulet = 7
    high_gold = 8
    double_enchant_item = 9
    crafting_item = 10
    prayer_stone = 11
    artifact = 12


LOOT_TYPES = dict()
for loot_type in LootType:
    LOOT_TYPES[loot_type.value] = loot_type


class ChallengeRating:
    def __init__(self, name, monsters, xp):
        self.xp = xp
        self.monsters = monsters
        self.name = name

    def get_random_creature(self):
        return self.monsters[random.randint(0, len(self.monsters) - 1)] if len(self.monsters) > 0 else None


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
        random.shuffle(self.loot_options)

    def get_random_item(self):
        return self.loot_options[random.randint(0, len(self.loot_options) - 1)]
