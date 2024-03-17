from typing import Optional, Tuple, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from battle_map_tv.aoe import AreaOfEffectManager
from battle_map_tv.grid import Grid
from battle_map_tv.image import Image
from battle_map_tv.initiative import InitiativeOverlayManager
from battle_map_tv.storage import get_from_storage, StorageKeys
from battle_map_tv.ui_elements import get_window_icon


class ImageWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battle Map TV")
        self.setWindowIcon(get_window_icon())
        self.setStyleSheet(
            """
            background-color: #000000;
            border: 0px
        """
        )
        self.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]

        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, self.size().width(), self.size().height())
        self.setScene(scene)

        self.image: Optional[Image] = None
        self.grid: Optional[Grid] = None
        self.initiative_overlay_manager = InitiativeOverlayManager(scene=scene)
        self.area_of_effect_manager = AreaOfEffectManager(scene=scene)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def add_image(self, image_path: str):
        self.image = Image(
            image_path=image_path,
            scene=self.scene(),
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

    def add_grid(self, screen_size_mm: Optional[tuple[int, int]], opacity: int):
        if self.grid is not None:
            self.remove_grid()
        self.grid = Grid(
            scene=self.scene(),
            screen_size_px=self.screen().size().toTuple(),  # type: ignore[arg-type]
            screen_size_mm=screen_size_mm,
            window_size_px=self.size().toTuple(),  # type: ignore[arg-type]
            opacity=opacity,
        )

    def update_screen_size_mm(self, screen_size_mm: Optional[Tuple[int, int]]):
        if self.grid is not None:
            self.grid.update_screen_mm(screen_size_mm)

    def remove_grid(self):
        if self.grid is not None:
            self.grid.delete()
            self.grid = None

    def add_initiative(self, text: str):
        self.initiative_overlay_manager.create(text=text)

    def initiative_change_font_size(self, by: int):
        self.initiative_overlay_manager.change_font_size(by=by)

    def remove_initiative(self):
        self.initiative_overlay_manager.clear()

    def add_area_of_effect(self, shape: str, color: str, callback: Callable):
        self.area_of_effect_manager.wait_for(shape=shape, color=color, callback=callback)

    def cancel_area_of_effect(self):
        self.area_of_effect_manager.cancel()

    def clear_area_of_effect(self):
        self.area_of_effect_manager.clear_all()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene().setSceneRect(0, 0, self.size().width(), self.size().height())
        if self.grid is not None:
            self.grid.update_window_px(self.size().toTuple())  # type: ignore[arg-type]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():  # type: ignore[attr-defined]
            self.toggle_fullscreen()
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.area_of_effect_manager.mouse_press_event(event):
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() != Qt.MouseButton.LeftButton:
            return
        if not self.area_of_effect_manager.mouse_move_event(event):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.area_of_effect_manager.mouse_release_event(event):
            super().mouseReleaseEvent(event)
