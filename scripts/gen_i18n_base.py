import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "status_dwarf"
PATTERN = r'(?<!def )_\(\"(.*)\"\)'

matches = []


def traverse_dir(target_dir):
    for item in target_dir.iterdir():
        if item.is_dir() and (item.name != "i18n" or item.name != "__pycache__"):
            traverse_dir(item)
        elif item.is_file():
            with open(item) as file:
                try:
                    for match in re.findall(PATTERN, file.read()):
                        matches.append(match)
                except UnicodeDecodeError:
                    pass


traverse_dir(BASE_DIR)

json_dict = {"en": {value: value for value in matches}}
with open(BASE_DIR / "i18n" / "i18n_base.json", "w") as f1:
    json.dump(json_dict, f1, indent=4)
