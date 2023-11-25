from typing import Optional, Dict, List, Union

from pyglet.graphics import Batch
from pyglet.gui import Frame
from pyglet.text import Label
from pyglet.window import Window, mouse

from .grid import Grid, mm_to_inch
from .gui_elements import ToggleButton, TextEntry, Slider, PushButton
from .image import Image
from .scale_detection import find_image_scale
from .storage import get_from_storage, StorageKeys, set_in_storage


class ImageWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image: Optional[Image] = None
        self.grid: Optional[Grid] = None

    def on_draw(self):
        self.clear()
        if self.image is not None:
            self.image.draw()
        if self.grid is not None:
            self.grid.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width=width, height=height)
        if self.image is not None:
            self.image.update_screen_px(width_px=width, height_px=height)
        if self.grid is not None:
            self.grid.update_window_px(width_px=width, height_px=height)

    def add_image(self, image_path: str):
        if self.image is not None:
            self.remove_image()
        self.image = Image(
            image_path=image_path,
            screen_width_px=self.width,
            screen_height_px=self.height,
        )

    def remove_image(self):
        if self.image is not None:
            self.image.delete()
            self.image = None

    def add_grid(self, width_mm: int, height_mm: int):
        if self.grid is not None:
            self.remove_grid()
        self.grid = Grid(
            screen_size_px=(self.screen.width, self.screen.height),
            screen_size_mm=(width_mm, height_mm),
            window_size_px=(self.width, self.height),
        )

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if (
            self.image is not None
            and buttons
            and mouse.LEFT
            and self.image.are_coordinates_within_image(x, y)
        ):
            self.image.pan(dx=dx, dy=dy)
            self.image.dragging = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.image is not None and self.image.dragging:
            self.image.dragging = False
            self.image.store_coordinates()


class GMWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(file_drops=True, *args, **kwargs)
        self.gui: GMGui

    def add_gui(self, image_window: ImageWindow):
        self.gui = GMGui(image_window=image_window, parent_window=self)

    def on_draw(self):
        self.clear()
        self.gui.draw()

    def on_file_drop(self, x: int, y: int, paths: List[str]):
        self.gui.image_window.add_image(image_path=paths[0])
        self.gui.slider_scale.reset()


class GMGui:
    def __init__(self, image_window: ImageWindow, parent_window: GMWindow):
        self.image_window = image_window
        self.batch = Batch()
        self.frame = Frame(window=parent_window)

        margin_x = 40
        margin_y = 60
        padding_x = 30
        margin_label = 10

        row_y = margin_y

        def slider_scale_callback(value: Union[float, str]):
            value = float(value)
            if image_window.image is not None:
                image_window.image.scale(value)
            self.slider_scale.value = value

        self.slider_scale = Slider(
            x=margin_x,
            y=row_y,
            value_min=0.1,
            value_max=4,
            default=1,
            batch=self.batch,
            callback=slider_scale_callback,
            label="Scale",
        )
        self.frame.add_widget(self.slider_scale)

        def button_callback_autoscale(button_value: bool) -> bool:
            if button_value and image_window.image is not None:
                try:
                    width_mm = get_from_storage(StorageKeys.width_mm)
                except KeyError:
                    return False
                screen_px_per_mm = image_window.width / width_mm
                px_per_inch = find_image_scale(image_window.image.filepath)
                px_per_mm = px_per_inch * mm_to_inch
                scale = screen_px_per_mm / px_per_mm
                image_window.image.scale(scale)
                self.slider_scale.value = scale
                return True
            return False

        self.button_autoscale = ToggleButton(
            x=self.slider_scale.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=button_callback_autoscale,
            label="Autoscale image",
        )
        self.frame.add_widget(self.button_autoscale)

        row_y += 100

        self.text_entry_screen_width = TextEntry(
            text=get_from_storage(StorageKeys.width_mm, optional=True),
            x=margin_x,
            y=row_y,
            width=200,
            batch=self.batch,
        )
        self.frame.add_widget(self.text_entry_screen_width)
        self.text_entry_screen_height = TextEntry(
            text=get_from_storage(StorageKeys.height_mm, optional=True),
            x=self.text_entry_screen_width.x2 + padding_x,
            y=row_y,
            width=200,
            batch=self.batch,
        )
        self.frame.add_widget(self.text_entry_screen_height)
        self.label_width = Label(
            text="Screen width (mm)",
            x=margin_x,
            y=self.text_entry_screen_width.y2 + margin_label,
            batch=self.batch,
        )
        self.label_height = Label(
            text="Screen height (mm)",
            x=self.text_entry_screen_height.x,
            y=self.text_entry_screen_height.y2 + margin_label,
            batch=self.batch,
        )

        def button_callback_grid(button_value: bool) -> bool:
            if button_value:
                try:
                    width_mm = int(self.text_entry_screen_width.value)
                    height_mm = int(self.text_entry_screen_height.value)
                except ValueError:
                    print("Invalid input for screen size")
                    return False
                else:
                    image_window.add_grid(
                        width_mm=width_mm,
                        height_mm=height_mm,
                    )
                    set_in_storage(StorageKeys.width_mm, width_mm)
                    set_in_storage(StorageKeys.height_mm, height_mm)
                    return True
            else:
                image_window.remove_grid()
                return False

        self.button_grid = ToggleButton(
            x=self.text_entry_screen_height.x2 + padding_x,
            y=row_y - int((50 - self.text_entry_screen_width.height) / 2),
            batch=self.batch,
            callback=button_callback_grid,
            label="Grid overlay",
        )
        self.frame.add_widget(self.button_grid)

        row_y += 100

        self.button_remove_image = PushButton(
            x=margin_x,
            y=row_y,
            batch=self.batch,
            callback=lambda: image_window.remove_image(),
            label="Remove image",
        )
        self.frame.add_widget(self.button_remove_image)

    def draw(self):
        self.batch.draw()
