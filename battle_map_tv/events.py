from enum import Enum
from typing import Callable, Dict


class EventKeys(Enum):
    change_scale = "change_scale"


class EventDispatcher:
    def __init__(self):
        self._store: Dict[EventKeys, Callable] = {}

    def dispatch_event(self, event_type: EventKeys, *args, **kwargs):
        func = self._store.get(event_type)
        if func:
            func(*args, **kwargs)

    def add_handler(self, event_type: EventKeys, handler: Callable):
        self._store[event_type] = handler


global_event_dispatcher = EventDispatcher()
