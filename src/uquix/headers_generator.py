#!/usr/bin/python3

################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################

import random, re, collections, fake_useragent

# NOTE: Please ask for PERMISSIONS before testing any web server.
class MyMainHeaders:

    def __init__(self, rules_file):

        self.rules = rules_file

    async def validate_rules(self) -> None:

        try:
            if not isinstance(self.rules, dict):
                raise ValueError("rules file must contain a dictionary at the top level")

            for header, rule in self.rules.items():
                if not rule.get("type"):
                    raise ValueError(f"'type' rule is NOT exist for '{header}' header")
                if not isinstance(rule.get("type"), str):
                    raise ValueError(f"header '{header}', 'type' rule must be \"simple\" or \"multi\"")
                for current_rule in rule:
                    if current_rule not in ["isalways", "type", "sep", "isunique", "items", "israndom_count", "count", "israndomplace", "repeat", "is403"]:
                        raise ValueError(f"'{current_rule}' rule isn't exist for header '{header}'")
                    if rule['type'].strip().lower() == "simple" and current_rule not in ["isalways", "type", "items", "israndomplace", "repeat", "is403"]:
                        raise ValueError(f"'{current_rule}' rule isn't exist for 'simple' type rule, header '{header}'. 'simple' type rule accept only these rules: 'isalways', 'israndomplace', 'items', 'is403'")
                if not isinstance(rule, dict):
                    raise ValueError(f"rules for header '{header}' must be a dictionary")
                if 'type' not in rule:
                    raise ValueError(f"'type' rule for header '{header}' is missing")
                if 'items' not in rule:
                    raise ValueError(f"'items' rule for header '{header}' is missing")
                if rule['type'].strip().lower() not in ['simple', 'multi']:
                    raise ValueError(f"Invalid type rule '{rule['type']}' for header '{header}'. valid types rule only: 'simple', 'multi'")
                if not isinstance(rule['items'], list):
                    raise ValueError(f"'items' rule for header '{header}' must be a list")
                if not all(isinstance(item, str) for item in rule['items']):
                    raise ValueError(f"items list for 'items' rule must contain a strings only. header '{header}'")
                if rule.get('israndom_count') and not isinstance(rule['israndom_count'], bool):
                    raise ValueError(f"'israndom_count' rule must be boolean, header '{header}'")
                if rule.get('israndom_count') and rule.get('count'):
                    raise ValueError(f"'count' rule can't be used when 'israndom_count' rule is true, header '{header}'")
                if rule.get('israndom_count') is False and not rule.get('count') and rule['type'].strip().lower() == "multi":
                    raise ValueError(f"'count' rule is required when 'israndom_count' rule is false, header '{header}'")
                if rule.get('count') and ((isinstance(rule['count'], str) and not (rule['count'].strip().startswith("{NUM->") or rule['count'].strip().upper() == "MAX" or rule['count'].strip().startswith("{["))) or (isinstance(rule['count'], list) or isinstance(rule['count'], bool))):
                    raise ValueError(f"header '{header}', "+"'count' rule can be:\n\tString: \"{NUM->range_separated_by_underscore:'_'}\" (ex, \"{NUM->5_10}\")\n\tString: \"MAX\". \"MAX\" means it will pick random items as number of all items\n\tString: \"{[numbers_to_random_choose_separated_by_comma',']}\" (ex, \"{[1, 3, 10, 20, 0, 15]}\")\n\tInteger: number of items will be picked randomly (ex, 8)\n\tNOTE: 'MAX' can be used instead of any number")
                if rule.get('repeat') and ((isinstance(rule['repeat'], str) and not (rule['repeat'].strip().startswith("{NUM->") or rule['repeat'].strip().upper() == "MAX" or rule['repeat'].strip().startswith("{["))) or (isinstance(rule['repeat'], list) or isinstance(rule['repeat'], bool))):
                    raise ValueError(f"header '{header}', "+"'repeat' rule can be:\n\tString: \"{NUM->range_separated_by_underscore:'_'}\" (ex, \"{NUM->5_10}\")\n\tString: \"MAX\". \"MAX\" means it will pick random items as number of all items\n\tString: \"{[numbers_to_random_choose_separated_by_comma',']}\" (ex, \"{[1, 3, 10, 20, 0, 15]}\")\n\tInteger: number of items will be picked randomly (ex, 8)\n\tNOTE: 'MAX' can be used instead of any number")
                if rule.get('isunique') and not isinstance(rule['isunique'], bool):
                    raise ValueError(f"'isunique' rule must be boolean, header '{header}'")
                if rule.get('sep') and not isinstance(rule['sep'], str):
                    raise ValueError(f"'sep' rule must be a string, header '{header}'")
                if rule.get('is403') is not None and not isinstance(rule['is403'], bool):
                    raise ValueError(f"'is403' rule must be boolean, header '{header}'")
                if rule.get('isalways') is not None and not isinstance(rule['isalways'], bool):
                    raise ValueError(f"'isalways' rule must be boolean, header '{header}'")
                if rule.get('israndomplace') is not None and not isinstance(rule['israndomplace'], bool):
                    raise ValueError(f"'israndomplace' rule must be boolean, header '{header}'")
        except ValueError as e:
            print(f"[-] Error, Failed to validate rules file: {e}")
            exit(1)


    def generate_random_number(self, range_str) -> str:

        match = re.match(r"\{NUM->(\d+)_(\d+)\}", range_str)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            return str(random.randint(start, end))
        return range_str

    def process_dynamic_placeholder(self, item) -> str:

        if isinstance(item, str):
            if "{NUM->" in item:
                allrange=len(item)
                tries=0
                count=0
                while tries<=allrange:
                    if item[tries:tries+6] == "{NUM->":
                        count+=1
                    tries+=6
                times=-1
            while "{NUM->" in item and times < count:
                item = re.sub(r"\{NUM->(\d+)_(\d+)\}", lambda m: self.generate_random_number(m.group(0)), item)
                times+=1
            while "{[" in item:
                item = re.sub(r"\{\[([^\]]+)\]\}", lambda m: random.choice(m.group(1).split(",")), item)
        return item


    def count_repeat_rules(self, count, max) -> int:

        if isinstance(count, str) and count.strip().startswith("{NUM->"):
            try:
                count = int(self.generate_random_number(count.strip().replace("'", "").replace("MAX", str(max))))
            except ValueError:
                raise ValueError(f"'count/repeat' rule has invalid range format '{count}', "+"numbers must be positive integers and separated by underscore (ex, \"{NUM->0_10}\")")
        elif isinstance(count, str) and count.strip().upper() == "MAX":
            count = max
        elif isinstance(count, str) and count.strip().startswith("{["):
            try:
                count = random.choice(
                    [int(x) for x in count.replace("-", "").replace("'", "").replace("{[", "").replace("]}", "").replace(" ", "").replace("MAX", str(max)).split(",")]
                )
            except ValueError:
                raise ValueError(f"'count/repeat' rule has invalid numbers list format '{count}', "+"list must contain positive integers and separated by comma (ex, \"{[0, 1, 5, 20]}\")")
        else:
            if count < 0:
                raise ValueError(f"'count/repeat' rule has invalid number '{count}', "+"number must be positive")
            count = int(count)        

        return count


    def process_items(self, items, isunique, sep, israndom_count, count) -> str:

        processed_items = list()

        if israndom_count:
            count = random.randint(1, len(items))
        else:
            count = self.count_repeat_rules(count, len(items))

        if isunique:
            if count > len(items):
                count = len(items)
            processed_items = random.sample(items, count)
        else:
            processed_items = random.choices(items, k=count)

        return sep.join(self.process_dynamic_placeholder(item) for item in processed_items)


    async def generate_headers_from_rules(self, israndom_agent, headers_num, is_403) -> dict[str, str]:

        headers = {}
        allkeys_to_stay = list()
        list_of_randoming = list()
        for header, rule in self.rules.items():
            if is_403 and rule.get('is403') is True:
                continue
            isalways = rule.get('isalways', False)
            if not isalways and headers_num > 0:
                isalways = random.choice([True, False])
            if isalways:
                items = rule['items']
                if rule['type'].strip().lower() == 'simple':
                    try:
                        processed_value = random.choice(items)
                    except IndexError:
                        processed_value = ""
                    headers[header] = self.process_dynamic_placeholder(processed_value)

                elif rule['type'].strip().lower() == 'multi':
                    headers[header] = self.process_items(
                        items,
                        isunique=rule.get('isunique', True),
                        sep=rule.get('sep', ", "),
                        israndom_count=rule.get('israndom_count', True),
                        count=rule.get('count', None)
                    )
                if header.lower() == "user-agent" and israndom_agent:
                    headers[header] = fake_useragent.UserAgent().random
                repeat = self.count_repeat_rules(rule.get('repeat', 0), len(items))
                headers[header]*=repeat+1
                israndomplace = rule.get('israndomplace', True)
                if not israndomplace:
                    key_to_stay = header
                    allkeys = list(headers.keys())
                    allkeys_to_stay.append(allkeys.index(key_to_stay))
                    allkeys.clear()
                else:
                    list_of_randoming.append(header)

        if list_of_randoming:
            for header in list_of_randoming:
                key_to_move = header
                position = random.randint(0, len(headers))
                while position in allkeys_to_stay:
                    position = random.randint(0, len(headers))
                allitems = list(headers.items())
                key_value = (key_to_move, headers.pop(key_to_move))
                headers = collections.OrderedDict(allitems[:position] + [key_value] + allitems[position:])
                allitems.clear()

        return dict(headers)


    async def mainheads(self, israndom_agent, headers_num, is_403) -> dict[str, str]:

        try:
            return await self.generate_headers_from_rules(israndom_agent, headers_num, is_403)
        except ValueError as e:
            print(f"[-] Error, Failed to validate rules file: {e}")
            exit(1)
        except Exception as e:
            print(f"[-] Error, Failed to validate rules file: {e}")
            exit(1)


if __name__ == "__main__":

    import asyncio
    import json
    import pathlib

    try:
        hdrs_rules_file = pathlib.Path(__file__).parent.parent.parent / "configs" / "headers_rules.json"
        if not hdrs_rules_file.exists():
            print(f"[-] Error, '{hdrs_rules_file}' file not found")
            exit(0)
        with open(hdrs_rules_file, "r") as f:
            ff = json.load(f)
    except FileNotFoundError:
        print(f"[-] Error, '{hdrs_rules_file}' file not found")
        exit(0)
    except Exception as e:
        print(f"[-] Error in '{hdrs_rules_file}' file: {e}")
        exit(0)
    asyncio.run(MyMainHeaders(ff).validate_rules())
    test_headers = asyncio.run(MyMainHeaders(ff).mainheads(True, 1, False))
    print(
        f"[*] This is an example headers based on '{hdrs_rules_file}' rules, but '--random-headers' is 1 and '--random-agents' is True and '--no-403headers' is False:\n"
    )
    for header, value in test_headers.items():
        print(f"\t{header}: {value}")


################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################
