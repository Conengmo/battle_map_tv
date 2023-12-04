from typing import Union, List

import pyglet
from pyglet.graphics import Batch
from pyglet.gui import Frame
from pyglet.shapes import Rectangle
from pyglet.window import Window

from battle_map_tv.events import global_event_dispatcher, EventKeys
from battle_map_tv.grid import mm_to_inch
from battle_map_tv.gui_elements import Slider, ToggleButton, TextEntry, PushButton, TabButton
from battle_map_tv.scale_detection import find_image_scale
from battle_map_tv.storage import get_from_storage, StorageKeys, set_in_storage
from battle_map_tv.window_image import ImageWindow


class GuiWindow(Window):
    def __init__(self, image_window: ImageWindow, *args, **kwargs):
        super().__init__(file_drops=True, *args, **kwargs)
        self.draw(dt=0)

        self.image_window = image_window
        self.batch = Batch()
        self.group_background = pyglet.graphics.Group(order=0)
        self.frame = Frame(window=self, cell_size=30)

        margin_x = 40
        margin_y = 60
        padding_x = 30
        padding_y = 30
        margin_label = 10

        row_y = margin_y

        def slider_scale_callback(value: Union[float, str]):
            value = float(value)
            if image_window.image is not None:
                image_window.image.scale(value)

        self.slider_scale = Slider(
            x=margin_x,
            y=row_y,
            value_min=0.1,
            value_max=4,
            default=1,
            batch=self.batch,
            callback=slider_scale_callback,
            label="Scale",
            label_formatter=lambda x: f"{x:.2f}",
        )
        self.frame.add_widget(self.slider_scale)

        def update_slider_scale_callback(value: float):
            self.switch_to()
            self.slider_scale.set_value(value)

        global_event_dispatcher.add_handler(EventKeys.change_scale, update_slider_scale_callback)

        def button_callback_autoscale(button_value: bool) -> bool:
            if button_value and image_window.image is not None:
                try:
                    width_mm = get_from_storage(StorageKeys.width_mm)
                except KeyError:
                    return False
                screen_px_per_mm = image_window.screen.width / width_mm
                px_per_inch = find_image_scale(image_window.image.filepath)
                px_per_mm = px_per_inch * mm_to_inch
                scale = screen_px_per_mm / px_per_mm
                image_window.switch_to()
                image_window.image.scale(scale)
                return True
            return False

        self.button_autoscale = ToggleButton(
            x=self.slider_scale.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=button_callback_autoscale,
            label="Autoscale image",
            icon="autoscale",
        )
        self.frame.add_widget(self.button_autoscale)

        row_y += 100

        self.button_remove_image = PushButton(
            x=margin_x,
            y=row_y,
            batch=self.batch,
            callback=lambda: image_window.remove_image(),
            label="Remove",
            icon="remove",
        )
        self.frame.add_widget(self.button_remove_image)

        self.button_restore_image = PushButton(
            x=self.button_remove_image.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=lambda: image_window.restore_image(),
            label="Restore",
            icon="restore",
        )
        self.frame.add_widget(self.button_restore_image)

        def callback_button_rotate_image():
            if image_window.image is not None:
                current_rotation = image_window.image.rotation
                current_image_filepath = image_window.image.filepath
                new_rotation = (current_rotation + 90) % 360
                image_window.add_image(image_path=current_image_filepath, rotation=new_rotation)

        self.button_rotate_image = PushButton(
            x=self.button_restore_image.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=callback_button_rotate_image,
            label="Rotate",
            icon="rotate",
        )
        self.frame.add_widget(self.button_rotate_image)

        def callback_button_center_image():
            if image_window.image is not None:
                image_window.image.center()

        self.button_center_image = PushButton(
            x=self.button_rotate_image.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=callback_button_center_image,
            label="Center",
            icon="center",
        )
        self.frame.add_widget(self.button_center_image)

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
            x=self.button_center_image.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=button_callback_grid,
            label="Grid overlay",
            icon="grid",
        )
        self.frame.add_widget(self.button_grid)

        def callback_button_fire(value):
            if value:
                image_window.add_fire()
            else:
                image_window.remove_fire()

        self.button_fire = ToggleButton(
            x=self.button_grid.x2 + padding_x,
            y=row_y,
            batch=self.batch,
            callback=callback_button_fire,
            label="Fire",
            icon="fire",
        )
        self.frame.add_widget(self.button_fire)

        self.button_fullscreen = PushButton(
            x=self.button_autoscale.x,
            y=row_y,
            batch=self.batch,
            callback=lambda: image_window.set_fullscreen(),
            label="Fullscreen",
            icon="fullscreen",
        )
        self.frame.add_widget(self.button_fullscreen)

        row_y += 100

        tab_height = 200

        def hide_tab_content():
            self.text_entry_screen_width.hide()
            self.text_entry_screen_height.hide()
            self.slider_grid_opacity.hide()

        self.text_entry_screen_width = TextEntry(
            text=get_from_storage(StorageKeys.width_mm, optional=True),
            x=margin_x + padding_x,
            y=row_y + padding_y,
            width=200,
            label="Screen width (mm)",
            batch=self.batch,
        )
        self.push_handlers(self.text_entry_screen_width)
        self.text_entry_screen_height = TextEntry(
            text=get_from_storage(StorageKeys.height_mm, optional=True),
            x=self.text_entry_screen_width.x2 + padding_x,
            y=row_y + padding_y,
            width=200,
            label="Screen height (mm)",
            batch=self.batch,
        )
        self.push_handlers(self.text_entry_screen_height)

        def callback_tab_screen_size():
            self.switch_to()
            hide_tab_content()
            self.text_entry_screen_width.show()
            self.text_entry_screen_height.show()

        self.tab_screen_size = TabButton(
            x=margin_x,
            y=row_y + tab_height,
            batch=self.batch,
            callback=callback_tab_screen_size,
            label="Screen size",
        )
        self.frame.add_widget(self.tab_screen_size)

        def slider_grid_opacity_callback(value: float):
            if image_window.grid is not None:
                image_window.grid.update_opacity(int(value))
            return value

        self.slider_grid_opacity = Slider(
            x=2 * margin_x,
            y=row_y + padding_y,
            value_min=0,
            value_max=255,
            default=200,
            batch=self.batch,
            callback=slider_grid_opacity_callback,
            label="Grid opacity",
            label_formatter=lambda value: str(int(value)),
        )
        self.push_handlers(self.slider_grid_opacity)

        def callback_tab_grid_opacity():
            self.switch_to()
            hide_tab_content()
            self.slider_grid_opacity.show()

        self.tab_grid_opacity = TabButton(
            x=self.tab_screen_size.x2,
            y=row_y + tab_height,
            batch=self.batch,
            callback=callback_tab_grid_opacity,
            label="Grid opacity",
        )
        self.frame.add_widget(self.tab_grid_opacity)

        callback_tab_screen_size()

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_file_drop(self, x: int, y: int, paths: List[str]):
        self.image_window.add_image(image_path=paths[0])
        self.switch_to()
        self.slider_scale.reset()
