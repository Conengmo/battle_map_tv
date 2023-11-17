import json
import os.path
from enum import Enum
from typing import Any, Dict

import platformdirs


path = platformdirs.user_config_dir(
    appname="battle-map-tv",
    ensure_exists=True,
)
filepath = os.path.join(path, "config.json")


def _load() -> Dict[str, Any]:
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _dump(data: Dict[str, Any]):
    with open(filepath, "w") as f:
        json.dump(data, f)


class StorageKeys(Enum):
    width_mm = "width_mm"
    height_mm = "height_mm"


def get_from_storage(key: StorageKeys, optional: bool = False):
    data = _load()
    try:
        return data[key.value]
    except KeyError:
        if optional:
            return None
        else:
            raise


def set_in_storage(key: StorageKeys, value: Any):
    data = _load()
    data[key.value] = value
    _dump(data)
