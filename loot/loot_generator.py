import random
import json
import pprint
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
        self.prayer_stone = LootController._create_loot_option("prayer_stone", do_flush)
        self.challenge_rating = LootController._create_challenge_ratings(do_flush)
        self.all_crs = list(self.challenge_rating.keys())
        self.found_artifacts, self.unfound_artifacts = LootController._create_artifacts(do_flush)

    # TODO: level up artifact method

    def get_new_artifact(self):
        return str(random.choice(self.unfound_artifacts))

    def get_found_artifacts(self):
        return list(self.found_artifacts.keys())

    def get_random_creature(self, max_cr):
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
        max_allowed_cr_index = self.all_crs.index(str(random.randint(1, 6)))
        amulet_cr_capacity_idx = random.randint(0, max_allowed_cr_index)
        amulet_max_cr = self.all_crs[amulet_cr_capacity_idx]
        return "CR: " + amulet_max_cr + "\n\tCreature: " + self.get_random_creature(amulet_max_cr)

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
            elif "advantage" in item.metadata:
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
    def _get_file_contents(name, do_flush=False):
        with open(DATA_DIR + name + ".json") as file:
            if do_flush:
                file.flush()
                file.close()
                return LootController._get_file_contents(name)
            return file.read()

    @staticmethod
    def _create_artifacts(do_flush=False):
        file_contents = LootController._get_file_contents("artifact", do_flush)
        artifact_dicts = json.loads(file_contents)
        found = dict()
        unfound = dict()
        for artifact_dict in artifact_dicts:
            artifact = LootController._create_artifact(artifact_dict)
            if not artifact.enabled:
                continue
            target_dict = found if artifact.found else unfound
            target_dict[artifact.name] = artifact
        return found, unfound

    @staticmethod
    def _create_artifact(artifact_dict):
        existing = []
        available = []
        for mod in artifact_dict["existing"]:
            existing.append(LootController._create_artifact_mod(mod))
        for mod in artifact_dict["available"]:
            available.append(LootController._create_artifact_mod(mod))
        return loot_types.Artifact(artifact_dict["name"],
                                   artifact_dict["type"],
                                   existing,
                                   available,
                                   artifact_dict.get("found", False),
                                   artifact_dict.get("enabled", True),
                                   artifact_dict.get("level", 1))

    @staticmethod
    def _create_artifact_mod(artifact_mod_dict: dict) -> loot_types.ArtifactMod:
        return loot_types.ArtifactMod(artifact_mod_dict["value"],
                                      artifact_mod_dict.get("upgradeable", True))


def get_int_from_str(string, default_integer=None):
    try:
        return int(string)
    except ValueError:
        return default_integer


def print_options():
    pp = pprint.PrettyPrinter(indent=4)
    print("\n")
    pp.pprint(loot_types.LOOT_TYPES)
    print("\t13: Random weapon enchant")
    print("\t14: Random armour enchant")
    print("\t15: Random enchant")
    print("\t16: Reload loot")
    print("\t17: Creature of a given CR")
    print("\t18: Level an artifact")
    print("\t>18: Show this")


def define_action_map(mapped_loot_controller):
    return {
        loot_types.LootType.junk: mapped_loot_controller.get_junk,
        loot_types.LootType.mundane: mapped_loot_controller.get_mundane,
        loot_types.LootType.consumable: mapped_loot_controller.get_consumable,
        loot_types.LootType.low_gold: lambda: random.randint(30, 100),
        loot_types.LootType.ring: mapped_loot_controller.get_ring,
        loot_types.LootType.single_enchant_item: mapped_loot_controller.get_single_enchanted_item,
        loot_types.LootType.amulet: mapped_loot_controller.get_amulet,
        loot_types.LootType.high_gold: lambda: min(random.randint(200, 600), random.randint(200, 600)),
        loot_types.LootType.double_enchant_item: mapped_loot_controller.get_double_enchanted_item,
        loot_types.LootType.crafting_item: mapped_loot_controller.get_crafting_item,
        loot_types.LootType.prayer_stone: mapped_loot_controller.get_prayer_stone,
        loot_types.LootType.artifact: mapped_loot_controller.get_new_artifact
    }


if __name__ == "__main__":
    loot_controller = LootController()
    loot_action_map = define_action_map(loot_controller)
    print_options()
    while True:
        roll = get_int_from_str(input("\nLoot roll: "), random.randint(1, 12))
        if roll < 0:
            exit(0)
        print(loot_action_map.get(loot_types.LOOT_TYPES.get(roll),
                                  lambda: str(roll) + " is not a valid loot option, checking extra options")())
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
        if roll == 18:
            found_artifacts = loot_controller.get_found_artifacts()
            if len(found_artifacts) == 0:
                print("No artifacts to level")
                continue
            comp = completer.Completer(found_artifacts)
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(comp.complete)
            print(found_artifacts)
            input("\nWhich artifact do you want to level? ")
        if roll > 18:
            print_options()
