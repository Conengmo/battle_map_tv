import os.path

import pyglet
from pyglet.sprite import Sprite

from battle_map_tv.storage import set_image_in_storage, ImageKeys, get_image_from_storage


class Image:
    def __init__(
        self,
        image_path: str,
        screen_width_px: int,
        screen_height_px: int,
    ):
        self.screen_width_px = screen_width_px
        self.screen_height_px = screen_height_px
        self.filepath: str
        self.image_filename: str
        self.dx: int = 0
        self.dy: int = 0
        self.sprite = self._load_sprite(image_path)
        self._recalculate_sprite_size()
        self.dragging: bool = False

    def draw(self):
        self.sprite.draw()

    def update_screen_px(self, width_px: int, height_px: int):
        self.screen_width_px = width_px
        self.screen_height_px = height_px
        self._recalculate_sprite_size()

    def _load_sprite(self, image_path: str) -> Sprite:
        self.filepath = image_path
        self.image_filename = os.path.basename(image_path)
        image = pyglet.image.load(image_path)
        sprite = Sprite(image)
        sprite.scale = get_image_from_storage(self.image_filename, ImageKeys.scale, default=1.0)
        self.dx, self.dy = get_image_from_storage(self.image_filename, ImageKeys.offsets, default=(0, 0))
        return sprite

    def _recalculate_sprite_size(self):
        self.sprite.x = (self.screen_width_px - self.sprite.width) / 2 + self.dx
        self.sprite.y = (self.screen_height_px - self.sprite.height) / 2 + self.dy

    def are_coordinates_within_image(self, x: int, y: int) -> bool:
        return (
            self.sprite.x <= x <= self.sprite.x + self.sprite.width
            and self.sprite.y <= y <= self.sprite.y + self.sprite.height
        )

    def scale(self, value: float):
        self.sprite.scale = value
        self._recalculate_sprite_size()
        set_image_in_storage(self.image_filename, ImageKeys.scale, value)

    def pan(self, dx: int, dy: int):
        self.dx += dx
        self.dy += dy
        self._recalculate_sprite_size()

    def store_coordinates(self):
        set_image_in_storage(self.image_filename, ImageKeys.offsets, (self.dx, self.dy))

    def change(self, image_path: str):
        print("change image to", image_path)
        self.sprite.delete()
        self.sprite = self._load_sprite(image_path)
        self._recalculate_sprite_size()
