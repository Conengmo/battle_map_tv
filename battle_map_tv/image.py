import os.path
from io import BytesIO

import cv2
import numpy as np
import pyglet
from pyglet.sprite import Sprite

from battle_map_tv.storage import set_image_in_storage, ImageKeys, get_image_from_storage


class Image:
    def __init__(
        self,
        image_path: str,
        window_width_px: int,
        window_height_px: int,
        rotation: int = 0,
    ):
        self.window_width_px = window_width_px
        self.window_height_px = window_height_px
        self.rotation = rotation
        self.dragging: bool = False

        self.filepath: str = image_path
        self.image_filename = os.path.basename(image_path)

        if rotation == 0:
            image = pyglet.image.load(image_path)
        else:
            image_cv = cv2.imread(image_path)
            image_cv = np.rot90(image_cv, k=rotation // 90)
            image_bytes = cv2.imencode(".png", image_cv)[1].tobytes()
            image = pyglet.image.load(filename=".png", file=BytesIO(image_bytes))

        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = Sprite(image)
        self.sprite.scale = get_image_from_storage(
            self.image_filename, ImageKeys.scale, default=1.0
        )

        self.dx: int = 0
        self.dy: int = 0
        self.dx, self.dy = get_image_from_storage(
            self.image_filename, ImageKeys.offsets, default=(0, 0)
        )

        self._recalculate_sprite_size()

    def draw(self):
        self.sprite.draw()

    def update_window_px(self, width_px: int, height_px: int):
        self.window_width_px = width_px
        self.window_height_px = height_px
        self._recalculate_sprite_size()

    def _recalculate_sprite_size(self):
        self.sprite.x = self.window_width_px / 2 + self.dx
        self.sprite.y = self.window_height_px / 2 + self.dy

    def are_coordinates_within_image(self, x: int, y: int) -> bool:
        return (
            self.sprite.x - self.sprite.width / 2 <= x <= self.sprite.x + self.sprite.width / 2
            and self.sprite.y - self.sprite.height / 2 <= y <= self.sprite.y + self.sprite.height / 2
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

    def delete(self):
        self.sprite.delete()
