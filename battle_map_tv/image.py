import os.path
from io import BytesIO

import cv2
import numpy as np
import pyglet
from battle_map_tv.broker import event_broker, EventKeys
from pyglet.sprite import Sprite

from battle_map_tv.storage import (
    set_image_in_storage,
    ImageKeys,
    get_image_from_storage,
    set_in_storage,
    StorageKeys,
)


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

        image_path = os.path.abspath(image_path)
        self.filepath: str = image_path
        self.image_filename = os.path.basename(image_path)
        set_in_storage(key=StorageKeys.previous_image, value=image_path)

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
        try:
            self.sprite.scale = get_image_from_storage(
                self.image_filename,
                ImageKeys.scale,
                do_raise=True,
            )
        except KeyError:
            new_scale = min(
                window_width_px / self.sprite.width,
                window_height_px / self.sprite.height,
            )
            if new_scale < 1.0:
                self.scale(new_scale)
        else:
            event_broker.trigger(EventKeys.change_scale, self.sprite.scale)

        self.center(store=False)
        dx, dy = get_image_from_storage(self.image_filename, ImageKeys.offsets, default=(0, 0))
        self.pan(dx=dx, dy=dy, store=False)

    def draw(self):
        self.sprite.draw()

    def update_window_px(self, width_px: int, height_px: int):
        diff_x = width_px - self.window_width_px
        diff_y = height_px - self.window_height_px
        self.pan(dx=int(diff_x / 2), dy=int(diff_y / 2))
        self.window_width_px = width_px
        self.window_height_px = height_px

    def are_coordinates_within_image(self, x: int, y: int) -> bool:
        width_half = self.sprite.width / 2
        height_half = self.sprite.height / 2
        return (
            self.sprite.x - width_half <= x <= self.sprite.x + width_half
            and self.sprite.y - height_half <= y <= self.sprite.y + height_half
        )

    def get_scale(self) -> float:
        return self.sprite.scale

    def scale(self, value: float):
        self.sprite.scale = value
        event_broker.trigger(EventKeys.change_scale, value)
        set_image_in_storage(self.image_filename, ImageKeys.scale, value)

    def pan(self, dx: int, dy: int, store: bool = True):
        self.sprite.x += dx
        self.sprite.y += dy
        if store:
            self.store_offsets()

    def center(self, store: bool = True):
        self.pan(*self._get_offsets(), store=store)

    def _get_offsets(self) -> tuple[int, int]:
        return (
            int(self.window_width_px / 2 - self.sprite.x),
            int(self.window_height_px / 2 - self.sprite.y),
        )

    def store_offsets(self):
        dx, dy = self._get_offsets()
        set_image_in_storage(self.image_filename, ImageKeys.offsets, (-dx, -dy))

    def delete(self):
        self.sprite.delete()
