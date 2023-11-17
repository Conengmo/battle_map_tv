import math
from typing import Optional

import pyglet
import pyglet.gui


class ImageDisplayWindow(pyglet.window.Window):
    def __init__(self, image_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite = self._load_sprite(image_path)
        self.sprite_dx = 0
        self.sprite_dy = 0
        self._recalculate_sprite_size()
        self.batch = pyglet.graphics.Batch()
        self.grid: Optional[Grid] = None

    def on_draw(self):
        self.clear()
        self.sprite.draw()
        self.batch.draw()

    def on_resize(self, width, height):
        super().on_resize(width=width, height=height)
        print('resize image window', (width, height))
        if self.grid is not None:
            self.grid.update_screen_px(width_px=width, height_px=height)

    @staticmethod
    def _load_sprite(image_path):
        image = pyglet.image.load(image_path)
        return pyglet.sprite.Sprite(image)

    def _recalculate_sprite_size(self):
        self.sprite.x = (self.width - self.sprite.width) / 2 + self.sprite_dx
        self.sprite.y = (self.height - self.sprite.height) / 2 + self.sprite_dy

    def add_grid(self, width_mm: int, height_mm: int):
        width_px, height_px = self.get_framebuffer_size()
        self.grid = Grid(
            width_px=width_px,
            height_px=height_px,
            width_mm=width_mm,
            height_mm=height_mm,
            batch=self.batch,
        )

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None

    def image_scale(self, value: float):
        self.sprite.scale = value
        self._recalculate_sprite_size()

    def image_pan_x(self, value: float):
        self.sprite_dx = int(value)
        self._recalculate_sprite_size()

    def image_pan_y(self, value: float):
        self.sprite_dy = int(value)
        self._recalculate_sprite_size()

    def image_change(self, image_path):
        print('change image to', image_path)
        self.sprite.delete()
        self.sprite = self._load_sprite(image_path)
        self._recalculate_sprite_size()


class GMWindow(pyglet.window.Window):
    def __init__(self, image_window: ImageDisplayWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_window = image_window
        self.batch = pyglet.graphics.Batch()
        self.frame = pyglet.gui.Frame(window=self)
        self.text_entries = {
            'screen_width': MyTextEntry(
                x=0,
                y=300,
                width=200,
                batch=self.batch,
            ),
            'screen_height': MyTextEntry(
                x=250,
                y=300,
                width=200,
                batch=self.batch,
            )
        }
        for widget in self.text_entries.values():
            self.frame.add_widget(widget)

        def button_callback_grid(button_value):
            if button_value:
                try:
                    width_mm = int(self.text_entries['screen_width'].value)
                    height_mm = int(self.text_entries['screen_height'].value)
                except ValueError:
                    print('Invalid input for screen size')
                    return False
                else:
                    self.image_window.add_grid(
                        width_mm=width_mm,
                        height_mm=height_mm,
                    )
                    return True
            else:
                self.image_window.remove_grid()
                return False

        self.button = MyToggleButton(
            x=500,
            y=300,
            batch=self.batch,
            callback=button_callback_grid,
        )
        self.frame.add_widget(self.button)

        self.slider_scale = MySlider(
            x=0,
            y=200,
            value_min=0.1,
            value_max=4,
            default=1,
            batch=self.batch,
            callback=image_window.image_scale,
        )
        self.frame.add_widget(self.slider_scale)
        self.slider_pan_x = MySlider(
            x=0,
            y=100,
            value_min=-image_window.width,
            value_max=image_window.width,
            default=0,
            batch=self.batch,
            callback=image_window.image_pan_x,
        )
        self.frame.add_widget(self.slider_pan_x)
        self.slider_pan_y = MySlider(
            x=0,
            y=0,
            value_min=-image_window.height,
            value_max=image_window.height,
            default=0,
            batch=self.batch,
            callback=image_window.image_pan_y,
        )
        self.frame.add_widget(self.slider_pan_y)

    def on_draw(self):
        self.batch.draw()

    def on_file_drop(self, x, y, paths):
        self.image_window.image_change(paths[0])
        self.slider_scale.value = self.slider_scale.default_value
        self.slider_pan_x.value = self.slider_pan_x.default_value
        self.slider_pan_y.value = self.slider_pan_y.default_value


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


class Grid:
    # width_mm = 590
    # height_mm = 335

    def __init__(self, width_px, height_px, width_mm, height_mm, batch):
        self.lines = []
        self.width_px = width_px
        self.height_px = height_px
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.batch = batch
        self.draw()

    def update_screen_px(self, width_px, height_px):
        self.width_px = width_px
        self.height_px = height_px
        self.draw()

    def update_screen_mm(self, width_mm, height_mm):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.draw()

    def delete(self):
        for line in self.lines:
            line.delete()

    def draw(self):
        self.delete()
        mm_to_inch = 0.03937007874
        pixels_per_inch_x = self.width_px / self.width_mm / mm_to_inch
        pixels_per_inch_y = self.height_px / self.height_mm / mm_to_inch
        n_lines_vertical = math.ceil(self.width_px / pixels_per_inch_x)
        n_lines_horizontal = math.ceil(self.height_px / pixels_per_inch_y)
        offset_x = (self.width_px - ((n_lines_vertical - 1) * pixels_per_inch_x)) / 2
        offset_y = (self.height_px - ((n_lines_horizontal - 1) * pixels_per_inch_x)) / 2
        self.lines = [
            *[
                pyglet.shapes.Line(
                    x=int(i * pixels_per_inch_x + offset_x),
                    y=0,
                    x2=int(i * pixels_per_inch_x + offset_x),
                    y2=self.height_px,
                    batch=self.batch
                )
                for i in range(n_lines_vertical)
            ],
            *[
                pyglet.shapes.Line(
                    x=0,
                    y=int(i * pixels_per_inch_y + offset_y),
                    x2=self.width_px,
                    y2=int(i * pixels_per_inch_y + offset_y),
                    batch=self.batch
                )
                for i in range(n_lines_horizontal)
            ]
        ]


def main():
    image_path = r"C:\Users\frank\Downloads\Evrys Castle final.JPG"

    display = pyglet.canvas.get_display()
    screens = display.get_screens()

    image_window = ImageDisplayWindow(
        image_path=image_path,
        caption="TV window",
        resizable=True,
        screen=screens[-1],
        width=screens[-1].width,
        height=screens[-1].height,
    )

    GMWindow(
        image_window=image_window,
        width=600,
        height=500,
        caption="GM window",
        file_drops=True,
    )

    pyglet.app.run(interval=1 / 20)


if __name__ == "__main__":
    main()
