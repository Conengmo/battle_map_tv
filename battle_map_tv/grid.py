import math
from typing import Tuple, Optional

from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsItemGroup, QGraphicsScene

mm_to_inch = 0.03937007874


class Grid:
    # width_mm = 590
    # height_mm = 335

    def __init__(
        self,
        scene: QGraphicsScene,
        screen_size_px: tuple[int, int],
        screen_size_mm: Optional[tuple[int, int]],
        window_size_px: tuple[int, int],
        opacity: int,
    ):
        self.scene = scene
        self.screen_size_px = screen_size_px
        self.screen_size_mm = screen_size_mm
        self.window_size_px = window_size_px
        self.opacity = opacity

        self.view = QGraphicsView()
        self.group: Optional[QGraphicsItemGroup] = None
        self.reset()

    def update_window_px(self, window_px: Tuple[int, int]):
        self.window_size_px = window_px
        self.reset()

    def update_screen_mm(self, screen_size_mm: Optional[Tuple[int, int]]):
        self.screen_size_mm = screen_size_mm
        self.reset()

    def update_opacity(self, opacity: int):
        self.opacity = opacity
        self.reset()

    def delete(self):
        if self.group is not None:
            self.scene.removeItem(self.group)
            self.group = None

    def reset(self):
        self.delete()
        self.group = QGraphicsItemGroup()
        self.group.setZValue(1)
        self.scene.addItem(self.group)

        if self.screen_size_mm is not None:
            pixels_per_inch_x = self.screen_size_px[0] / self.screen_size_mm[0] / mm_to_inch
            pixels_per_inch_y = self.screen_size_px[1] / self.screen_size_mm[1] / mm_to_inch
        else:
            pixels_per_inch_x, pixels_per_inch_y = 60, 60
        n_lines_vertical = math.ceil(self.window_size_px[0] / pixels_per_inch_x)
        n_lines_horizontal = math.ceil(self.window_size_px[1] / pixels_per_inch_y)
        offset_x = (self.window_size_px[0] - ((n_lines_vertical - 1) * pixels_per_inch_x)) / 2
        offset_y = (self.window_size_px[1] - ((n_lines_horizontal - 1) * pixels_per_inch_y)) / 2

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255, self.opacity))

        for i in range(n_lines_vertical):
            line = self.scene.addLine(
                QLineF(
                    int(i * pixels_per_inch_x + offset_x),
                    0,
                    int(i * pixels_per_inch_x + offset_x),
                    self.window_size_px[1],
                ),
                pen,
            )
            self.group.addToGroup(line)

        for i in range(n_lines_horizontal):
            line = self.scene.addLine(
                QLineF(
                    0,
                    int(i * pixels_per_inch_y + offset_y),
                    self.window_size_px[0],
                    int(i * pixels_per_inch_y + offset_y),
                ),
                pen,
            )
            self.group.addToGroup(line)
