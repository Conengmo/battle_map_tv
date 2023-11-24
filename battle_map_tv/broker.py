from enum import Enum
from typing import Dict, Callable, List


class EventKeys(Enum):
    change_scale = "change_scale"
    change_pan_x = "change_pan_x"
    change_pan_y = "change_pan_y"
    change_image = "change_image"


class EventBroker:
    """A simple event broker."""

    def __init__(self):
        self._callbacks: Dict[EventKeys, List[Callable]] = {}

    def register(self, key: EventKeys, callback: Callable):
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)

    def unregister(self, key: EventKeys, callback: Callable):
        self._callbacks[key].remove(callback)

    def trigger(self, key: EventKeys, *args, **kwargs):
        if key not in self._callbacks:
            return
        for callback in self._callbacks[key]:
            callback(*args, **kwargs)


event_broker = EventBroker()
