import os.path
from typing import Callable, Union, Optional

import pyglet
from pyglet.graphics import Batch
from pyglet.text import Label

margin_y_label = 10

pyglet.resource.path = [os.path.join(pyglet.resource.get_script_home(), "resources")]
pyglet.resource.reindex()


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
    total_height = 60

    def __init__(
        self,
        text: Union[str, int, None],
        x: int,
        y: int,
        width: int,
        label: str,
        batch: Batch,
    ):
        text_str = str(text) if text is not None else ""
        super().__init__(
            text=text_str,
            x=x,
            y=y,
            width=width,
            batch=batch,
            color=(76, 76, 76, 255),
            text_color=(254, 254, 254, 255),
            caret_color=(254, 254, 254, 255),
        )
        self.y_original = y
        self.height = 30
        self.label = Label(text=label, x=self.x, batch=batch)

    def hide(self):
        self.y = -100
        self.label.y = -100

    def show(self):
        self.y = self.y_original
        self._layout.x = self.x + 10
        self._layout.y = self.y - 5
        self.label.y = self.y2 + margin_y_label


class PushButton(CoordinatesMixin, pyglet.gui.PushButton):
    def __init__(
        self,
        x: int,
        y: int,
        batch: Batch,
        callback: Optional[Callable],
        label: str,
        icon: str,
    ):
        pressed = pyglet.resource.image(f"button_{icon}_hover.png").get_texture()
        depressed = pyglet.resource.image(f"button_{icon}.png").get_texture()
        super().__init__(x=x, y=y, pressed=pressed, depressed=depressed, batch=batch)
        self.label = Label(
            text=label,
            x=x + self.width / 2,
            y=self.y2 + margin_y_label,
            align="center",
            anchor_x="center",
            batch=batch,
        )
        if callback is not None:
            self.set_handler("on_release", callback)


class ToggleButton(pyglet.gui.ToggleButton, PushButton):
    def __init__(self, x: int, y: int, batch: Batch, callback: Callable, label: str, icon: str):
        super().__init__(x=x, y=y, batch=batch, callback=None, label=label, icon=icon)
        self.set_handler("on_toggle", callback)


class EffectToggleButton(pyglet.gui.ToggleButton):
    total_height = 100

    def __init__(self, x: int, y: int, batch: Batch, callback: Callable, effect: str):
        self.y_original = y
        pressed = pyglet.resource.image(f"effect_{effect}_hover.png").get_texture()
        depressed = pyglet.resource.image(f"effect_{effect}.png").get_texture()
        super().__init__(x=x, y=y, pressed=pressed, depressed=depressed, batch=batch)
        self.set_handler("on_toggle", callback)

    def hide(self):
        self.y = -100

    def show(self):
        self.y = self.y_original


class TabButton(CoordinatesMixin, pyglet.gui.PushButton):
    pressed = pyglet.resource.image("tab_depressed.png").get_texture()
    depressed = pyglet.resource.image("tab_hover.png").get_texture()
    hover = pyglet.resource.image("tab_depressed.png").get_texture()

    def __init__(
        self,
        x: int,
        y: int,
        batch: Batch,
        callback: Callable,
        label: str,
    ):
        super().__init__(
            x=x, y=y, pressed=self.pressed, depressed=self.depressed, hover=self.hover, batch=batch
        )
        self.label = Label(
            text=label,
            x=x + self.width / 2,
            y=self.y + self.height / 2,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=batch,
        )
        self.set_handler("on_release", callback)


class Slider(CoordinatesMixin, pyglet.gui.Slider):
    base = pyglet.resource.image("slider_base.png").get_texture()
    knob = pyglet.resource.image("slider_knob.png").get_texture()
    total_height = 70

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
        self.y_original = y
        self.value_min = value_min
        self.value_max = value_max
        self.default = self._external_to_internal(default)
        self.value = self.default
        self.callback = callback

        self.label = Label(
            text=label,
            x=self.x,
            batch=batch,
        )
        self.label_value = Label(
            text=label_formatter(default),
            x=super().x2 + 20,
            anchor_y="center",
            batch=batch,
        )
        self.label_formatter = label_formatter
        self.show()

    @property
    def x2(self) -> int:
        return super().x2 + 50

    @property
    def _range(self) -> float:
        return self.value_max - self.value_min

    def _external_to_internal(self, value: float) -> float:
        return (value - self.value_min) * 100 / self._range

    def _internal_to_external(self, value: float) -> float:
        return (self._range * value / 100) + self.value_min

    def on_change(self, value: float):
        value = self._internal_to_external(value)
        self.update_label_text(value)
        self.callback(value)

    def set_value(self, value: float):
        self.value = self._external_to_internal(value)
        self.update_label_text(value)

    def update_label_text(self, value: float):
        self.label_value.text = self.label_formatter(value)

    def reset(self):
        self.value = self.default

    def hide(self):
        self.y = -100
        self.label.y = -100
        self.label_value.y = -100

    def show(self):
        self.y = self.y_original
        self.label.y = self.y2 + margin_y_label
        self.label_value.y = self.y + self.height / 2
        self.value = self.value
