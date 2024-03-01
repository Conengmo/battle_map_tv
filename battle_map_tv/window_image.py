from typing import Optional, Tuple, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedLayout, QGraphicsView, QGraphicsScene

from battle_map_tv.grid import Grid
from battle_map_tv.image import Image
from battle_map_tv.storage import get_from_storage, StorageKeys, set_in_storage
from battle_map_tv.ui_elements import get_window_icon, InitiativeOverlay


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

        layout = QStackedLayout(self)
        layout.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = QGraphicsView()
        self.view.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]
        self.view.setStyleSheet("border: 0px")
        layout.addWidget(self.view)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.size().width(), self.size().height())
        self.view.setScene(self.scene)

        self.image: Optional[Image] = None
        self.grid: Optional[Grid] = None
        self.initiative_overlays: Optional[List[InitiativeOverlay]] = None

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
            screen_size_px=self.screen().size().toTuple(),  # type: ignore[arg-type]
            screen_size_mm=screen_size_mm,
            window_size_px=self.size().toTuple(),  # type: ignore[arg-type]
            opacity=opacity,
        )

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None

    def add_initiative(self, text: str, font_size: Optional[int] = None):
        if font_size is None:
            try:
                font_size = get_from_storage(StorageKeys.initiative_font_size)
            except KeyError:
                font_size = 20
        else:
            set_in_storage(StorageKeys.initiative_font_size, font_size)
        self.remove_initiative()
        if text:
            self.initiative_overlays = [
                InitiativeOverlay(text, self.scene, font_size).move_to_bottom_left(),
                InitiativeOverlay(text, self.scene, font_size).move_to_top_right().flip(),
            ]

    def initiative_change_font_size(self, by: int):
        if self.initiative_overlays is None:
            return
        current_font_size = self.initiative_overlays[0].font_size
        new_font_size = current_font_size + by
        current_text = self.initiative_overlays[0].text_raw
        self.remove_initiative()
        self.add_initiative(text=current_text, font_size=new_font_size)

    def remove_initiative(self):
        if self.initiative_overlays is not None:
            for overlay in self.initiative_overlays:
                overlay.remove()
            self.initiative_overlays = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(0, 0, self.size().width(), self.size().height())
        if self.grid is not None:
            self.grid.update_window_px(self.size().toTuple())  # type: ignore[arg-type]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():  # type: ignore[attr-defined]
            self.toggle_fullscreen()
        super().keyPressEvent(event)
