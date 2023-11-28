from typing import Callable, Union, Optional

import pyglet
from pyglet.graphics import Batch
from pyglet.text import Label

margin_y_label = 10


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
        label: str,
        batch: Batch,
        callback: Optional[Callable] = None,
    ):
        text_str = str(text) if text is not None else ""
        super().__init__(text=text_str, x=x, y=y, width=width, batch=batch)
        self._layout.x = x + 10
        self._layout.y = y - 5
        self.height = 30
        self.callback = callback
        self.label = Label(
            text=label,
            x=self.x,
            y=self.y2 + margin_y_label,
            batch=batch,
        )

    def on_commit(self, text: str):
        super().on_commit(text=text)
        if self.callback is not None:
            self.callback(text)


class PushButton(CoordinatesMixin, pyglet.gui.PushButton):
    pressed = pyglet.resource.image(r"resources/button_on.png").get_texture()
    depressed = pyglet.resource.image(r"resources/button_off.png").get_texture()

    def __init__(self, x: int, y: int, batch: Batch, callback: Callable, label: str):
        super().__init__(x=x, y=y, pressed=self.pressed, depressed=self.depressed, batch=batch)
        self.callback = callback
        self.label = Label(
            text=label,
            x=x + self.width / 2,
            y=self.y2 + margin_y_label,
            align="center",
            anchor_x="center",
            batch=batch,
        )

    def on_mouse_release(self, *args, **kwargs):
        super().on_mouse_release(*args, **kwargs)
        self.callback()


class ToggleButton(pyglet.gui.ToggleButton, PushButton):
    def on_mouse_press(self, *args, **kwargs):
        super().on_mouse_press(*args, **kwargs)
        self.value: bool = self.callback(self.value)


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
        label: str,
        label_formatter: Callable = lambda x: str(x),
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
        self.label = Label(
            text=label,
            x=self.x,
            y=self.y2 + margin_y_label,
            batch=batch,
        )
        self.label_value = Label(
            text=label_formatter(default),
            x=super().x2 + 20,
            y=self.y + self.height / 2,
            anchor_y="center",
            batch=batch,
        )
        self.label_formatter = label_formatter

    @property
    def x2(self) -> int:
        return super().x2 + 50

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
        value_internal = self._value_to_internal(value)
        self._value = value_internal
        x = (
            (self._max_knob_x - self._min_knob_x) * value_internal / 100
            + self._min_knob_x
            + self._half_knob_width
        )
        self._knob_spr.x = max(self._min_knob_x, min(x - self._half_knob_width, self._max_knob_x))
        if hasattr(self, "label_value"):
            self.label_value.text = self.label_formatter(value)

    def on_mouse_drag(self, *args, **kwargs):
        super().on_mouse_drag(*args, **kwargs)
        self.callback(self.value)

    def reset(self):
        self.value = self.default
