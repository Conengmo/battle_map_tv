from typing import Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedLayout, QGraphicsView, QGraphicsScene

from battle_map_tv.grid import Grid
from battle_map_tv.image import Image
from battle_map_tv.storage import get_from_storage, StorageKeys
from battle_map_tv.ui_elements import get_window_icon


class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battle Map TV")
        self.setWindowIcon(get_window_icon())
        self.setStyleSheet(
            """
            background-color: #000000;
        """
        )

        self.layout = QStackedLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.view = QGraphicsView()
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("border: 0px")
        self.layout.addWidget(self.view)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.size().width(), self.size().height())
        self.view.setScene(self.scene)

        self.image: Optional[Image] = None
        self.grid: Optional[Grid] = None

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def add_image(self, image_path: str):
        self.image = Image(
            image_path=image_path,
            scene=self.scene,
            window_width_px=self.width(),
            window_height_px=self.height(),
        )

    def remove_image(self):
        if self.image is not None:
            self.image.delete()
            self.image = None

    def restore_image(self):
        try:
            previous_image = get_from_storage(StorageKeys.previous_image)
        except KeyError:
            pass
        else:
            self.remove_image()
            self.add_image(image_path=previous_image)

    def add_grid(self, screen_size_mm: Tuple[int, int], opacity: int):
        if self.grid is not None:
            self.remove_grid()
        self.grid = Grid(
            scene=self.scene,
            screen_size_px=self.screen().size().toTuple(),
            screen_size_mm=screen_size_mm,
            window_size_px=self.size().toTuple(),
            opacity=opacity,
        )

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(0, 0, self.size().width(), self.size().height())
        if self.grid is not None:
            self.grid.update_window_px(self.size().toTuple())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.toggle_fullscreen()
        super().keyPressEvent(event)
