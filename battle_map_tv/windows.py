from typing import Optional, Dict, List

from pyglet.graphics import Batch
from pyglet.gui import Frame
from pyglet.window import Window

from .grid import Grid, mm_to_inch
from .gui_elements import ToggleButton, TextEntry, Slider
from .image import Image
from .scale_detection import find_image_scale
from .storage import get_from_storage, StorageKeys, set_in_storage


class ImageWindow(Window):
    def __init__(self, image_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = Image(
            image_path=image_path,
            screen_width_px=self.width,
            screen_height_px=self.height,
        )
        self.grid: Optional[Grid] = None

    def on_draw(self):
        self.clear()
        self.image.draw()
        if self.grid is not None:
            self.grid.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width=width, height=height)
        print("resize image window", (width, height))
        self.image.update_screen_px(width_px=width, height_px=height)
        if self.grid is not None:
            self.grid.update_screen_px(width_px=width, height_px=height)

    def add_grid(self, width_mm: int, height_mm: int):
        self.grid = Grid(
            width_px=self.width,
            height_px=self.height,
            width_mm=width_mm,
            height_mm=height_mm,
        )

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None


class GMWindow(Window):
    def __init__(self, image_window: ImageWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_window = image_window
        self.batch = Batch()
        self.frame = Frame(window=self)
        self.text_entries: Dict[str, TextEntry] = {
            "screen_width": TextEntry(
                text=get_from_storage(StorageKeys.width_mm, optional=True),
                x=0,
                y=300,
                width=200,
                batch=self.batch,
            ),
            "screen_height": TextEntry(
                text=get_from_storage(StorageKeys.height_mm, optional=True),
                x=250,
                y=300,
                width=200,
                batch=self.batch,
            ),
        }
        for widget in self.text_entries.values():
            self.frame.add_widget(widget)

        def button_callback_grid(button_value: bool) -> bool:
            if button_value:
                try:
                    width_mm = int(self.text_entries["screen_width"].value)
                    height_mm = int(self.text_entries["screen_height"].value)
                except ValueError:
                    print("Invalid input for screen size")
                    return False
                else:
                    self.image_window.add_grid(
                        width_mm=width_mm,
                        height_mm=height_mm,
                    )
                    set_in_storage(StorageKeys.width_mm, width_mm)
                    set_in_storage(StorageKeys.height_mm, height_mm)
                    return True
            else:
                self.image_window.remove_grid()
                return False

        self.button = ToggleButton(
            x=500,
            y=300,
            batch=self.batch,
            callback=button_callback_grid,
        )
        self.frame.add_widget(self.button)

        def button_callback_autoscale(button_value: bool) -> bool:
            if button_value:
                try:
                    width_mm = get_from_storage(StorageKeys.width_mm)
                except KeyError:
                    return False
                screen_px_per_mm = self.image_window.width / width_mm
                px_per_inch = find_image_scale(self.image_window.image.filepath)
                px_per_mm = px_per_inch * mm_to_inch
                scale = screen_px_per_mm / px_per_mm
                self.image_window.image.scale(scale)
                return True
            return False

        self.button_autoscale = ToggleButton(
            x=500,
            y=400,
            batch=self.batch,
            callback=button_callback_autoscale,
        )
        self.frame.add_widget(self.button_autoscale)

        self.slider_scale = Slider(
            x=0,
            y=200,
            value_min=0.1,
            value_max=4,
            default=1,
            batch=self.batch,
            callback=image_window.image.scale,
        )
        self.frame.add_widget(self.slider_scale)
        self.slider_pan_x = Slider(
            x=0,
            y=100,
            value_min=-image_window.width,
            value_max=image_window.width,
            default=0,
            batch=self.batch,
            callback=image_window.image.pan_x,
        )
        self.frame.add_widget(self.slider_pan_x)
        self.slider_pan_y = Slider(
            x=0,
            y=0,
            value_min=-image_window.height,
            value_max=image_window.height,
            default=0,
            batch=self.batch,
            callback=image_window.image.pan_y,
        )
        self.frame.add_widget(self.slider_pan_y)

    def on_draw(self):
        self.batch.draw()

    def on_file_drop(self, x: int, y: int, paths: List[str]):
        self.image_window.image.change(paths[0])
        self.slider_scale.value = self.slider_scale.default_value
        self.slider_pan_x.value = self.slider_pan_x.default_value
        self.slider_pan_y.value = self.slider_pan_y.default_value
