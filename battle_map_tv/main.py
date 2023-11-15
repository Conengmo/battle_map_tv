import pyglet
import pyglet.gui


class ImageDisplayWindow(pyglet.window.Window):

    def __init__(self, image_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        image = pyglet.image.load(image_path)
        self.sprite = pyglet.sprite.Sprite(image)

    def on_draw(self):
        self.clear()
        self.sprite.draw()

    def image_scale(self, value: float):
        self.sprite.scale = value

    def image_pan_x(self, value: float):
        self.sprite.x = int(value)

    def image_pan_y(self, value: float):
        self.sprite.y = int(value)


class GMWindow(pyglet.window.Window):

    def __init__(self, image_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        self.frame = pyglet.gui.Frame(self)
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


class MySlider(pyglet.gui.Slider):

    def __init__(self, x, y, value_min, value_max, default, batch, callback):
        base = pyglet.image.load(r"C:\Users\frank\Downloads\slider-base.png").get_texture()
        knob = pyglet.image.load(r"C:\Users\frank\Downloads\slider-knob.png").get_texture()
        super().__init__(x=x, y=y, base=base, knob=knob, batch=batch)
        self.value_min = value_min
        self.value_max = value_max
        self.value = (default - value_min) * 100 / (value_max - value_min)
        self.callback = callback

    def on_mouse_drag(self, *args, **kwargs):
        super().on_mouse_drag(*args, **kwargs)
        value_scaled = ((self.value_max - self.value_min) * self.value / 100) + self.value_min
        self.callback(value_scaled)


def main():
    image_path = r"C:\Users\frank\Downloads\Evrys Castle final.JPG"

    image_window = ImageDisplayWindow(image_path, width=1600, height=1000, fullscreen=False, caption="TV window")

    GMWindow(image_window=image_window, width=600, height=500, caption="GM window")

    pyglet.app.run(interval=1/20)


if __name__ == "__main__":
    main()
