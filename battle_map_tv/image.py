import os.path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QLabel, QLayout

from battle_map_tv.events import global_event_dispatcher, EventKeys
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
        layout: QLayout,
        window_width_px: int,
        window_height_px: int,
    ):
        self.layout = layout
        self.window_width_px = window_width_px
        self.window_height_px = window_height_px
        self.rotation = 0
        self.dragging: bool = False

        image_path = os.path.abspath(image_path)
        self.filepath: str = image_path
        self.image_filename = os.path.basename(image_path)
        set_in_storage(key=StorageKeys.previous_image, value=image_path)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.pixmap = QPixmap(image_path)
        self.pixmap_original = self.pixmap.copy()
        self.label.setPixmap(self.pixmap)

        try:
            self.rotation = get_image_from_storage(
                self.image_filename,
                ImageKeys.rotation,
                do_raise=True,
            )
        except KeyError:
            pass
        else:
            self.pixmap = self.pixmap.transformed(QTransform().rotate(self.rotation))
            self.label.setPixmap(self.pixmap)

        self._scale: float = 1.0
        try:
            self.scale(
                get_image_from_storage(
                    self.image_filename,
                    ImageKeys.scale,
                    do_raise=True,
                )
            )
        except KeyError:
            new_scale = min(
                window_width_px / self.pixmap.size().width(),
                window_height_px / self.pixmap.size().height(),
            )
            if new_scale < 1.0:
                self.scale(new_scale)
        else:
            global_event_dispatcher.dispatch_event(EventKeys.change_scale, self._scale)

        # self.center(store=False)
        # dx, dy = get_image_from_storage(self.image_filename, ImageKeys.offsets, default=(0, 0))
        # self.pan(dx=dx, dy=dy, store=False)

    def delete(self):
        self.label.deleteLater()

    def rotate(self):
        self.rotation = (self.rotation + 90) % 360
        self.pixmap = self.pixmap.transformed(QTransform().rotate(90))
        self.label.setPixmap(self.pixmap)
        set_image_in_storage(self.image_filename, ImageKeys.rotation, self.rotation)

    def scale(self, value: float):
        self.pixmap = self.pixmap_original.scaled(self.pixmap_original.size() * value)
        self.label.setPixmap(self.pixmap)
        self._scale = value
        global_event_dispatcher.dispatch_event(EventKeys.change_scale, value)
        set_image_in_storage(self.image_filename, ImageKeys.scale, value)
