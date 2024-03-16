import json
import os.path
from enum import Enum
from typing import Any, Dict

import platformdirs

path = platformdirs.user_data_dir("battle-map-tv", ensure_exists=True)
filepath = os.path.join(path, "config.json")


def _load() -> Dict[str, Any]:
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _dump(data: Dict[str, Any]):
    # catch errors before start writing to the file
    json_str = json.dumps(data, indent=2)
    with open(filepath, "w") as f:
        f.write(json_str)


class StorageKeys(Enum):
    screen_size_mm = "screen_size_mm"
    previous_image = "previous_image"
    initiative_font_size = "initiative_font_size"
    thumbnail_0 = "thumbnail_0"
    thumbnail_1 = "thumbnail_1"
    thumbnail_2 = "thumbnail_2"
    thumbnail_3 = "thumbnail_3"


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


def remove_from_storage(key: StorageKeys):
    data = _load()
    data.pop(key.value, None)
    _dump(data)


class ImageKeys(Enum):
    scale = "scale"
    position = "position"
    rotation = "rotation"


def get_image_from_storage(
    image_filename: str,
    key: ImageKeys,
    default=None,
    do_raise: bool = False,
):
    data = _load()
    try:
        image_data = data[image_filename]
        return image_data[key.value]
    except KeyError:
        if do_raise:
            raise
        return default


def set_image_in_storage(image_filename: str, key: ImageKeys, value):
    data = _load()
    image_data = data.setdefault(image_filename, {})
    image_data[key.value] = value
    _dump(data)
