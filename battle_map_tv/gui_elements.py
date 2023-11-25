from typing import Callable, Union, Optional

import pyglet
from pyglet.graphics import Batch


class CoordinatesMixin:
    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height


class TextEntry(CoordinatesMixin, pyglet.gui.TextEntry):
    def __init__(
        self,
        text: Union[str, int, None],
        x: int,
        y: int,
        width: int,
        batch: Batch,
        callback: Optional[Callable] = None,
    ):
        text_str = str(text) if text is not None else ""
        super().__init__(text=text_str, x=x, y=y, width=width, batch=batch)
        self._layout.x = x + 10
        self._layout.y = y - 5
        self.height = 30
        self.callback = callback

    def on_commit(self, text: str):
        super().on_commit(text=text)
        if self.callback is not None:
            self.callback(text)


class ToggleButton(CoordinatesMixin, pyglet.gui.ToggleButton):
    pressed = pyglet.resource.image(r"resources/button_on.png").get_texture()
    depressed = pyglet.resource.image(r"resources/button_off.png").get_texture()

    def __init__(self, x: int, y: int, batch: Batch, callback: Callable):
        super().__init__(x=x, y=y, pressed=self.pressed, depressed=self.depressed, batch=batch)
        self.callback = callback

    def on_mouse_press(self, *args, **kwargs):
        super().on_mouse_press(*args, **kwargs)
        self.value = self.callback(self.value)


class Slider(CoordinatesMixin, pyglet.gui.Slider):
    base = pyglet.resource.image(r"resources/slider_base.png").get_texture()
    knob = pyglet.resource.image(r"resources/slider_knob.png").get_texture()

    def __init__(
        self,
        x: int,
        y: int,
        value_min: float,
        value_max: float,
        default: float,
        batch: Batch,
        callback: Callable,
    ):
        super().__init__(
            x=x,
            y=y,
            base=self.base,
            knob=self.knob,
            batch=batch,
        )
        self.value_min = value_min
        self.value_max = value_max
        self.default = default
        self.value = default
        self.callback = callback

    @property
    def _range(self) -> float:
        return self.value_max - self.value_min

    def _value_to_internal(self, value):
        return (value - self.value_min) * 100 / self._range

    @property
    def value(self):
        return (self._range * self._value / 100) + self.value_min

    @value.setter
    def value(self, value: float):
        value = self._value_to_internal(value)
        self._value = value
        x = (
            (self._max_knob_x - self._min_knob_x) * value / 100
            + self._min_knob_x
            + self._half_knob_width
        )
        self._knob_spr.x = max(self._min_knob_x, min(x - self._half_knob_width, self._max_knob_x))

    def on_mouse_drag(self, *args, **kwargs):
        super().on_mouse_drag(*args, **kwargs)
        self.callback(self.value)
