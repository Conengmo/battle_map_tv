import os.path
from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from battle_map_tv.events import global_event_dispatcher, EventKeys
from battle_map_tv.storage import (
    set_image_in_storage,
    ImageKeys,
    get_image_from_storage,
    set_in_storage,
    StorageKeys,
)


class CustomGraphicsPixmapItem(QGraphicsPixmapItem):
    def __init__(self, image_path: str):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)
        self.image_filename = os.path.basename(image_path)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)
        self.position_original = self._pos_as_tuple()

    def _pos_as_tuple(self) -> Tuple[int, int]:
        return int(self.pos().x()), int(self.pos().y())

    def wheelEvent(self, event):
        self.set_scale(self.scale() + event.delta() / 1500)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        position = self._pos_as_tuple()
        offset = tuple(a - b for a, b in zip(self.position_original, position))
        set_image_in_storage(self.image_filename, ImageKeys.offsets, offset)

    def set_scale(self, value: float):
        self.setScale(value)
        global_event_dispatcher.dispatch_event(EventKeys.change_scale, value)
        set_image_in_storage(self.image_filename, ImageKeys.scale, value)


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
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("border: 0px")

        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self.pixmap_item = CustomGraphicsPixmapItem(image_path)
        self.scene.addItem(self.pixmap_item)

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
                window_width_px / self.pixmap_item.pixmap().size().width(),
                window_height_px / self.pixmap_item.pixmap().size().height(),
            )
            if new_scale < 1.0:
                self.scale(new_scale)
        else:
            global_event_dispatcher.dispatch_event(EventKeys.change_scale, self._scale)

        try:
            offset = get_image_from_storage(
                self.image_filename,
                ImageKeys.offsets,
                do_raise=True,
            )
        except KeyError:
            pass
        else:
            rect = self.scene.sceneRect()
            self.pixmap_item.moveBy(-1 * offset[0], -1 * offset[1])
            self.scene.setSceneRect(rect)

    def delete(self):
        self.scene.clear()
        self.layout.removeWidget(self.view)

    def rotate(self):
        self.rotation = (self.rotation + 90) % 360
        self.view.rotate(90)
        set_image_in_storage(self.image_filename, ImageKeys.rotation, self.rotation)

    def scale(self, value: float):
        self.pixmap_item.set_scale(value)
