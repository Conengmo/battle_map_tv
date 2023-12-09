from typing import Optional

from pyglet.window import Window, mouse, FPSDisplay

from battle_map_tv.effects.fire import Fire
from battle_map_tv.grid import Grid
from battle_map_tv.image import Image
from battle_map_tv.storage import get_from_storage, StorageKeys


class ImageWindow(Window):
    def __init__(self, show_fps: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image: Optional[Image] = None
        self.grid: Optional[Grid] = None
        self.fire: Optional[Fire] = None
        self.fps_display = FPSDisplay(self) if show_fps else None
        self.invalid = False
        self.continuous = False

    def on_draw(self):
        if self.invalid or self.continuous:
            self.switch_to()
            self.clear()
            if self.image is not None:
                self.image.draw()
            if self.grid is not None:
                self.grid.draw()
            if self.fire is not None:
                self.fire.draw()
            if self.fps_display is not None:
                self.fps_display.draw()
            self.invalid = False

    def on_resize(self, width: int, height: int):
        super().on_resize(width=width, height=height)
        if self.image is not None:
            self.image.update_window_px(width_px=width, height_px=height)
        if self.grid is not None:
            self.grid.update_window_px(width_px=width, height_px=height)
        if self.fire is not None:
            self.fire.update_window_px(width=width, height=height)
        self.invalid = True

    def add_image(self, image_path: str, rotation: int = 0):
        self.switch_to()
        self.remove_image()
        self.image = Image(
            image_path=image_path,
            window_width_px=self.width,
            window_height_px=self.height,
            rotation=rotation,
        )
        self.invalid = True

    def remove_image(self):
        self.switch_to()
        if self.image is not None:
            self.image.delete()
            self.image = None
        self.invalid = True

    def restore_image(self):
        try:
            previous_image = get_from_storage(StorageKeys.previous_image)
        except KeyError:
            pass
        else:
            self.add_image(image_path=previous_image)

    def add_grid(self, width_mm: int, height_mm: int):
        self.switch_to()
        if self.grid is not None:
            self.remove_grid()
        self.grid = Grid(
            screen_size_px=(self.screen.width, self.screen.height),
            screen_size_mm=(width_mm, height_mm),
            window_size_px=(self.width, self.height),
        )
        self.invalid = True

    def remove_grid(self):
        self.switch_to()
        if self.grid is not None:
            self.grid.delete()
            self.grid = None
        self.invalid = True

    def add_fire(self):
        self.switch_to()
        self.remove_fire()
        self.fire = Fire(window_width=self.width, window_height=self.height)
        self.continuous = True

    def remove_fire(self):
        if self.fire is not None:
            self.fire.delete()
            self.fire = None
            self.continuous = False
            self.invalid = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if (
            self.image is not None
            and buttons
            and mouse.LEFT
            and self.image.are_coordinates_within_image(x, y)
        ):
            self.switch_to()
            self.image.pan(dx=dx, dy=dy, store=False)
            self.image.dragging = True
            self.invalid = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.image is not None and self.image.dragging:
            self.image.dragging = False
            self.image.store_offsets()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.image is not None and self.image.are_coordinates_within_image(x, y):
            self.switch_to()
            self.image.scale(self.image.get_scale() * (1 + scroll_y / 10))
            self.invalid = True
