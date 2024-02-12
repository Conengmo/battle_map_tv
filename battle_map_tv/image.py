import os.path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QLabel, QLayout, QGraphicsView, QGraphicsScene

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

        self.view = QGraphicsView()
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("border: 0px")

        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self.pixmap = QPixmap(image_path)
        self.pixmap_original = self.pixmap.copy()
        self.scene.addPixmap(self.pixmap)

        try:
            self.rotation = get_image_from_storage(
                self.image_filename,
                ImageKeys.rotation,
                do_raise=True,
            )
        except KeyError:
            pass
        else:
            self.view.rotate(self.rotation)

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

        # dx, dy = get_image_from_storage(self.image_filename, ImageKeys.offsets, default=(0, 0))
        # self.pan(dx=dx, dy=dy, store=False)

    def delete(self):
        self.scene.clear()
        self.layout.removeWidget(self.view)

    def rotate(self):
        self.rotation = (self.rotation + 90) % 360
        self.view.rotate(90)
        set_image_in_storage(self.image_filename, ImageKeys.rotation, self.rotation)

    def scale(self, value: float):
        scaling = value / self._scale
        self.view.scale(scaling, scaling)
        self._scale = value
        global_event_dispatcher.dispatch_event(EventKeys.change_scale, value)
        set_image_in_storage(self.image_filename, ImageKeys.scale, value)
