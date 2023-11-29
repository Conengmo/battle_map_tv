from enum import Enum
from typing import Callable

from pyglet.event import EventDispatcher


class EventKeys(Enum):
    change_scale = "change_scale"


class CustomEventDispatcher(EventDispatcher):
    def dispatch_event(self, event_type: EventKeys, *args):
        super().dispatch_event(str(event_type), *args)

    def add_handler(self, event_type: EventKeys, handler: Callable):
        super().push_handlers(**{str(event_type): handler})


CustomEventDispatcher.register_event_type(str(EventKeys.change_scale))


global_event_dispatcher = CustomEventDispatcher()
