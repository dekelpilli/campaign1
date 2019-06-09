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


class LootController:
    def __init__(self, do_flush=False):
        self.junk = LootController.create_loot_option("junk", do_flush)
        self.crafting_item = LootController.create_loot_option("crafting_item", do_flush)
        self.mundane = LootController.create_loot_option("mundane", do_flush)
        self.enchant = LootController.create_loot_option("enchant", do_flush)
        self.consumable = LootController.create_loot_option("consumable", do_flush)
        self.prayer_stone = LootController.create_loot_option("prayer_stone", do_flush)
        self.challenge_rating = LootController.create_challenge_ratings(do_flush)
        self.all_crs = list(self.challenge_rating.keys())

    def get_random_creature(self, cr):
        while True:
            creature = self.challenge_rating[cr].get_random_creature()
            if creature is None:
                cr = str(int(cr) - 1)  # Not protecting against 0.125/0.5 because those have creatures
            else:
                return creature

    def get_amulet(self):
        max_allowed_cr_index = self.all_crs.index(str(random.randint(1, 6)))
        amulet_cr_capacity_idx = random.randint(0, max_allowed_cr_index)
        amulet_max_cr = self.all_crs[amulet_cr_capacity_idx]
        return "CR: " + amulet_max_cr + "\n\tCreature: " + self.get_random_creature(amulet_max_cr)

    def get_mundane(self):
        return self.mundane.get_random_item().value

    def get_prayer_stone(self):
        return self.prayer_stone.get_random_item().value

    def get_enchant(self):
        return self.enchant.get_random_item().value

    def get_consumable(self):
        return LootController.get_multiple_items(self.consumable.get_random_item(), lambda: random.randint(1, 4))

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
        return LootController.get_multiple_items(self.crafting_item.get_random_item(), lambda: random.randint(1, 3))

    @staticmethod
    def get_multiple_items(item, randomisation_function):
        if "disadvantage" in item.metadata:
            amount = min(randomisation_function(), randomisation_function())
        elif "advantage" in item.metadata:
            amount = max(randomisation_function(), randomisation_function())
        else:
            amount = randomisation_function()
        for metadata_tag in item.metadata:
            if metadata_tag[0] == "x":
                amount = amount * get_int_from_str(metadata_tag[1:], 1)
            potentially_static_value = get_int_from_str(metadata_tag)
            if potentially_static_value is not None:
                amount = potentially_static_value

        return str(amount) + " " + item.value

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

        print("This item is not an armour or a weapon - " + base_type.value)
        return base_type.value \
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

        print("This item is not an armour or a weapon - " + base_type.value)
        return base_type \
            + "\n\t" + self.get_enchant()

    def get_junk(self):
        return self.junk.get_random_item().value

    @staticmethod
    def create_challenge_ratings(do_flush=False):
        with open(DATA_DIR + "monster.json") as file:
            if do_flush:
                file.flush()
                file.close()
                return LootController.create_challenge_ratings()
            file_contents = file.read()
        cr_dicts = json.loads(file_contents)
        crs = dict()
        for cr in cr_dicts:
            crs[cr] = ChallengeRating(cr, cr_dicts[cr]["monsters"], cr_dicts[cr]["XP"])
        return crs

    @staticmethod
    def create_loot_option(name, do_flush=False):
        with open(DATA_DIR + name + ".json") as file:
            if do_flush:
                file.flush()
                file.close()
                return LootController.create_loot_option(name)
            file_contents = file.read()
        item_dicts = json.loads(file_contents)
        loot_option_items = []
        for item_dict in item_dicts:
            loot_option_items.append(LootOptionItem(item_dict["value"],
                                                    item_dict.get("weighting", 10),
                                                    item_dict.get("enabled", True),
                                                    item_dict.get("metadata", [])))
        loot_option = LootOption(name)
        for loot_option_item in loot_option_items:
            loot_option.add_item(loot_option_item)

        return loot_option


def get_int_from_str(string, default_integer=None):
    try:
        return int(string)
    except ValueError:
        return default_integer


def print_options():
    pp = pprint.PrettyPrinter(indent=4)
    print("\n")
    pp.pprint(LOOT_TYPES)
    print("\t13: Random weapon enchant")
    print("\t14: Random armour enchant")
    print("\t15: Random enchant")
    print("\t16: Reload mods")
    print("\t17: Creature of a given CR")
    print("\t>17: Show this")


def define_action_map(mapped_loot_controller):
    return {
        LootType.junk: mapped_loot_controller.get_junk,
        LootType.mundane: mapped_loot_controller.get_mundane,
        LootType.consumable: mapped_loot_controller.get_consumable,  # TODO: Need more
        LootType.low_gold: lambda: random.randint(30, 99),
        LootType.ring: None,
        LootType.single_enchant_item: mapped_loot_controller.get_single_enchanted_item,
        LootType.amulet: mapped_loot_controller.get_amulet,
        LootType.high_gold: lambda: min(random.randint(200, 600), random.randint(200, 600)),
        LootType.double_enchant_item: mapped_loot_controller.get_double_enchanted_item,
        LootType.crafting_item: mapped_loot_controller.get_crafting_item,
        LootType.prayer_stone: mapped_loot_controller.get_prayer_stone,
        LootType.artifact: None
    }


if __name__ == "__main__":
    loot_controller = LootController()
    loot_action_map = define_action_map(loot_controller)
    count = 0
    print_options()
    while True:
        roll = get_int_from_str(input("\nLoot roll: "), random.randint(1, 8))
        if roll < 0:
            exit(0)
        loot_type = LOOT_TYPES.get(roll)
        print(loot_action_map.get(loot_type, lambda: str(roll) + " is not a valid loot option, "
                                                                 "checking extra options")())
        count += 1
        if roll == 13:
            print(loot_controller.get_weapon_enchant())
        if roll == 14:
            print(loot_controller.get_armour_enchant())
        if roll == 15:
            print(loot_controller.get_enchant())
        if roll == 16:
            loot_controller = LootController(True)
            loot_action_map = define_action_map(loot_controller)
            print("Reloaded loot from files")
        if roll == 17:
            print(loot_controller.get_random_creature(input("\nMonster CR: ")))
        if roll > 17:
            print_options()
