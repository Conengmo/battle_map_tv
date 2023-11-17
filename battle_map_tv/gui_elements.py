import pyglet


class MyTextEntry(pyglet.gui.TextEntry):
    def __init__(self, x, y, width, batch):
        super().__init__(text='', x=x, y=y, width=width, batch=batch)


class MyToggleButton(pyglet.gui.ToggleButton):
    pressed = pyglet.resource.image(r"resources/button_on.png").get_texture()
    depressed = pyglet.resource.image(r"resources/button_off.png").get_texture()

    def __init__(self, x, y, batch, callback):
        super().__init__(
            x,
            y,
            pressed=self.pressed,
            depressed=self.depressed,
            batch=batch
        )
        self.callback = callback

    def on_mouse_press(self, *args, **kwargs):
        super().on_mouse_press(*args, **kwargs)
        self.value = self.callback(self.value)


class MySlider(pyglet.gui.Slider):
    base = pyglet.resource.image(r"resources/slider_base.png").get_texture()
    knob = pyglet.resource.image(r"resources/slider_knob.png").get_texture()

    def __init__(self, x, y, value_min, value_max, default, batch, callback):
        super().__init__(x=x, y=y, base=self.base, knob=self.knob, batch=batch)
        self.value_min = value_min
        self.value_max = value_max
        self.default_value = (default - value_min) * 100 / (value_max - value_min)
        self.value = self.default_value
        self.callback = callback

    def on_mouse_drag(self, *args, **kwargs):
        super().on_mouse_drag(*args, **kwargs)
        value_scaled = ((self.value_max - self.value_min) * self.value / 100) + self.value_min
        self.callback(value_scaled)
