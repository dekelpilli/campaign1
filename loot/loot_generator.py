import random
import json
from pprint import PrettyPrinter
import completer
import loot_types
import readline
from os import sep

DATA_DIR = "data" + sep


class LootController:
    def __init__(self, do_flush=False):
        print("Loading...")
        self.junk = LootController._create_loot_option("junk", do_flush)
        self.crafting_item = LootController._create_loot_option("crafting_item", do_flush)
        self.mundane = LootController._create_loot_option("mundane", do_flush)
        self.ring = LootController._create_loot_option("ring", do_flush)
        self.enchant = LootController._create_loot_option("enchant", do_flush)
        self.consumable = LootController._create_loot_option("consumable", do_flush)
        self.prayer_stone = LootController._create_prayer_stone(do_flush)
        self.challenge_rating = LootController._create_challenge_ratings(do_flush)
        self.all_crs = list(self.challenge_rating.keys())
        self.found_relics, self.unfound_relics = LootController._create_relics(do_flush)

    def level_up_prayer_path(self):
        prayer_paths_started = list(filter(
            lambda prayer_stone: prayer_stone.owner is not None
                                 and prayer_stone.enabled
                                 and prayer_stone.progress != 10,
            set(self.prayer_stone.loot_options)))

        if len(prayer_paths_started) == 0:
            return "No paths to level"

        owners = set(map(lambda prayer_stone: prayer_stone.owner, prayer_paths_started))
        readline.set_completer(completer.Completer(owners).complete)
        print(owners)
        prayer_path_owner_choice = input("\nWhich owner's path do you want to level? ")
        readline.set_completer(lambda text, state: None)
        if prayer_path_owner_choice not in owners:
            return prayer_path_owner_choice + " is not a valid prayer path owner choice"

        return list(filter(lambda prayer_stone: prayer_path_owner_choice == prayer_stone.owner,
                           prayer_paths_started))[0].get_next()

    def level_up_relic_by_choice(self):
        found_relics = self._get_found_relics()
        if len(found_relics) == 0:
            return "No relics to level"

        readline.set_completer(completer.Completer(found_relics).complete)
        print(found_relics)
        relic_choice = input("\nWhich relic do you want to level? ")
        readline.set_completer(lambda text, state: None)
        if relic_choice not in found_relics:
            return relic_choice + " is not a valid relic choice"

        return self._level_up_relic_by_name(relic_choice)

    def _level_up_relic_by_name(self, relic_name):
        relic = self.found_relics[relic_name]
        return self._level_up_relic(relic)

    def _level_up_relic(self, relic, num_choices=2):
        options = 2  # new random mod, new relic mod
        upgradeable_mods = []
        for existing_mod in relic.existing:
            if existing_mod.upgradeable:
                upgradeable_mods.append(existing_mod)
        if len(upgradeable_mods) > 0:
            options += 2  # double weighting

        output = "Options:\n\t"
        for i in range(num_choices):
            if i != 0:
                output += "\nOR\n\t"
            output += self._get_upgrade_option(relic, random.randint(1, options), upgradeable_mods)
        return output

    def _get_upgrade_option(self, relic, option_id, upgradeable_mods):
        option_string = ""
        if option_id == 1:
            option_string += "New mod: "
            if relic.type == "weapon":
                option_string += self.get_weapon_enchant()
            elif relic.type == "armour":
                option_string += self.get_armour_enchant()
            else:
                option_string += self.get_enchant()
            return option_string

        if option_id == 2:
            option_string += "New Relic mod: "
            mod = random.choice(relic.available)
            return option_string + mod.value

        if option_id > 2:
            option_string += "Upgrade existing mod: "
            return option_string + random.choice(upgradeable_mods).value

    def get_new_relic(self):
        keys = list(self.unfound_relics.keys())
        randomly_chosen_key = keys[random.randint(0, len(keys) - 1)]
        relic = self.unfound_relics[randomly_chosen_key]
        return str(relic)

    def _get_found_relics(self):
        return list(self.found_relics.keys())

    def get_random_creature(self):
        return self.get_random_creature_of_cr(input("\nMonster CR: "))

    def get_random_creature_of_cr(self, max_cr):
        cr = max_cr
        while True:
            creature = self.challenge_rating[cr].get_random_creature()
            if creature is None:
                cr = str(int(cr) - 1)  # Not protecting against 0.125/0.25/0.5 because those have creatures
            else:
                if cr != max_cr:
                    print("Creature is of CR " + cr + " instead of " + max_cr)
                return creature

    def get_amulet(self):
        max_allowed_cr_index = self.all_crs.index(str(random.randint(2, 4)))
        amulet_cr_capacity_idx = random.randint(2, max_allowed_cr_index)
        amulet_max_cr = self.all_crs[amulet_cr_capacity_idx]
        return "CR: " + amulet_max_cr + "\n\tCreature: " + self.get_random_creature_of_cr(amulet_max_cr)

    def get_mundane(self):
        return self.mundane.get_random_item().value

    def get_ring(self):
        return self.ring.get_random_item().value

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
        amount = None
        for metadata_tag in item.metadata:
            if metadata_tag == "disadvantage":
                amount = min(randomisation_function(), randomisation_function())
            elif metadata_tag == "advantage":
                amount = max(randomisation_function(), randomisation_function())
            elif metadata_tag[0] == "x":
                amount = amount * get_int_from_str(metadata_tag[1:], 1)
            else:
                potentially_static_value = get_int_from_str(metadata_tag)
                if potentially_static_value is not None:
                    amount = potentially_static_value

        if amount is None:
            amount = randomisation_function()
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

        return self.get_double_enchanted_item()  # got a ring, try again

    def get_single_enchanted_item(self):
        base_type = self.mundane.get_random_item()
        if "weapon" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_weapon_enchant()

        if "armour" in base_type.metadata:
            return base_type.value \
                   + "\n\t" + self.get_armour_enchant()

        return self.get_single_enchanted_item()  # got a ring, try again

    def get_junk(self):
        return self.junk.get_random_item().value

    @staticmethod
    def _create_challenge_ratings(do_flush=False):
        file_contents = LootController._get_file_contents("monster", do_flush)
        cr_dicts = json.loads(file_contents)
        crs = dict()
        for cr in cr_dicts:
            crs[cr] = loot_types.ChallengeRating(cr, cr_dicts[cr]["monsters"], cr_dicts[cr]["XP"])
        return crs

    @staticmethod
    def _create_loot_option(name, do_flush=False):
        file_contents = LootController._get_file_contents(name, do_flush)
        item_dicts = json.loads(file_contents)
        loot_option_items = []
        for item_dict in item_dicts:
            loot_option_items.append(loot_types.LootOptionItem(item_dict["value"],
                                                               item_dict.get("weighting", 10),
                                                               item_dict.get("enabled", True),
                                                               item_dict.get("metadata", [])))
        loot_option = loot_types.LootOption(name)
        for loot_option_item in loot_option_items:
            loot_option.add_item(loot_option_item)

        return loot_option

    @staticmethod
    def _create_prayer_stone(do_flush=False):
        file_contents = LootController._get_file_contents("prayer_stone", do_flush)
        prayer_stone_dicts = json.loads(file_contents)
        prayer_stones = []
        for prayer_stone_dict in prayer_stone_dicts:
            prayer_stones.append(loot_types.PrayerStone(prayer_stone_dict["value"],
                                                        prayer_stone_dict.get("weighting", 10),
                                                        prayer_stone_dict.get("enabled", True),
                                                        prayer_stone_dict.get("metadata", []),
                                                        prayer_stone_dict["levels"],
                                                        prayer_stone_dict.get("owner", None),
                                                        prayer_stone_dict.get("progress", 0)))
        loot_option = loot_types.LootOption("prayer_stone")
        for loot_option_item in prayer_stones:
            loot_option.add_item(loot_option_item)

        return loot_option

    @staticmethod
    def _get_file_contents(name, do_flush=False):
        with open(DATA_DIR + name + ".json") as data_file:
            if do_flush:
                data_file.flush()
                return LootController._get_file_contents(name)
            return data_file.read()

    @staticmethod
    def _create_relics(do_flush=False):
        file_contents = LootController._get_file_contents("relic", do_flush)
        relic_dicts = json.loads(file_contents)
        found = dict()
        unfound = dict()
        for relic_dict in relic_dicts:
            relic = LootController._create_relic(relic_dict)
            if not relic.enabled:
                continue
            target_dict = found if relic.found else unfound
            target_dict[relic.name] = relic
        return found, unfound

    @staticmethod
    def _create_relic(relic_dict):
        existing = []
        available = []
        for mod in relic_dict["existing"]:
            existing.append(LootController._create_relic_mod(mod))
        for mod in relic_dict["available"]:
            available.append(LootController._create_relic_mod(mod))
        return loot_types.Relic(relic_dict["name"],
                                relic_dict["type"],
                                existing,
                                available,
                                relic_dict.get("found", False),
                                relic_dict.get("enabled", True),
                                relic_dict.get("level", 1))

    @staticmethod
    def _create_relic_mod(relic_mod_dict: dict) -> loot_types.RelicMod:
        return loot_types.RelicMod(relic_mod_dict["value"],
                                   relic_mod_dict.get("upgradeable", True))


def get_int_from_str(string, default_integer=None):
    try:
        return int(string)
    except ValueError:
        return default_integer


def print_options():
    pp = PrettyPrinter(indent=4)
    print("\n")
    pp.pprint(loot_types.LOOT_TYPES)
    print("\t13: Random weapon enchant")
    print("\t14: Random armour enchant")
    print("\t15: Random enchant")
    print("\t16: Reload loot")
    print("\t17: Creature of a given CR")
    print("\t18: Level a relic")
    print("\t19: Level a prayer path")
    print("\t>19: Show this")


def define_action_map(mapped_loot_controller):
    return {
        loot_types.LootType.junk.value: mapped_loot_controller.get_junk,
        loot_types.LootType.mundane.value: mapped_loot_controller.get_mundane,
        loot_types.LootType.consumable.value: mapped_loot_controller.get_consumable,
        loot_types.LootType.low_gold.value: lambda: str(random.randint(30, 100)) + " gold",
        loot_types.LootType.ring.value: mapped_loot_controller.get_ring,
        loot_types.LootType.single_enchant_item.value: mapped_loot_controller.get_single_enchanted_item,
        loot_types.LootType.amulet.value: mapped_loot_controller.get_amulet,
        loot_types.LootType.high_gold.value:
            lambda: str(min(random.randint(200, 600), random.randint(200, 600))) + " gold",
        loot_types.LootType.double_enchant_item.value: mapped_loot_controller.get_double_enchanted_item,
        loot_types.LootType.crafting_item.value: mapped_loot_controller.get_crafting_item,
        loot_types.LootType.prayer_stone.value: mapped_loot_controller.get_prayer_stone,
        loot_types.LootType.relic.value: mapped_loot_controller.get_new_relic,
        13: mapped_loot_controller.get_weapon_enchant,
        14: mapped_loot_controller.get_armour_enchant,
        15: mapped_loot_controller.get_enchant,
        # 16: reload loot
        17: mapped_loot_controller.get_random_creature,
        18: mapped_loot_controller.level_up_relic_by_choice,
        19: mapped_loot_controller.level_up_prayer_path
    }


if __name__ == "__main__":
    loot_controller = LootController()
    loot_action_map = define_action_map(loot_controller)
    print_options()
    while True:
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        roll = get_int_from_str(input("\nLoot roll: "), 99)
        if roll == 0:
            roll = random.randint(1, 12)
            print("Random roll: " + str(roll) + ", (" + str(loot_action_map[roll]) + ")")
        if roll < 0:
            exit(0)
        print(loot_action_map.get(roll,
                                  lambda: str(roll) + " is not a normal loot option, checking extra options")())

        if roll == 16:
            loot_controller = LootController(True)
            loot_action_map = define_action_map(loot_controller)
            print("Reloaded loot from files")
        if roll > 19:
            print_options()
