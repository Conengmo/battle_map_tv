import pyglet
from pyglet.sprite import Sprite


class Image:
    def __init__(
        self,
        image_path: str,
        screen_width_px: int,
        screen_height_px: int,
    ):
        self.screen_width_px = screen_width_px
        self.screen_height_px = screen_height_px
        self.sprite = self._load_sprite(image_path)
        self.sprite_dx: int = 0
        self.sprite_dy: int = 0

    def draw(self):
        self.sprite.draw()

    def update_screen_px(self, width_px: int, height_px: int):
        self.screen_width_px = width_px
        self.screen_height_px = height_px
        self._recalculate_sprite_size()

    @staticmethod
    def _load_sprite(image_path: str) -> Sprite:
        image = pyglet.image.load(image_path)
        return Sprite(image)

    def _recalculate_sprite_size(self):
        self.sprite.x = (self.screen_width_px - self.sprite.width) / 2 + self.sprite_dx
        self.sprite.y = (self.screen_height_px - self.sprite.height) / 2 + self.sprite_dy

    def scale(self, value: float):
        self.sprite.scale = value
        self._recalculate_sprite_size()

    def pan_x(self, value: float):
        self.sprite_dx = int(value)
        self._recalculate_sprite_size()

    def pan_y(self, value: float):
        self.sprite_dy = int(value)
        self._recalculate_sprite_size()

    def change(self, image_path: str):
        print("change image to", image_path)
        self.sprite.delete()
        self.sprite = self._load_sprite(image_path)
        self._recalculate_sprite_size()
