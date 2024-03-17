import math
from typing import Optional

from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsItemGroup, QWidget

from battle_map_tv import global_vars
from battle_map_tv.utils import size_to_tuple

mm_to_inch = 0.03937007874


class Grid:
    def __init__(self, window: QWidget):
        screen_size_mm = global_vars.screen_size_mm
        screen_size_px = size_to_tuple(window.screen().size())
        self.window_size_px = size_to_tuple(window.size())

        if screen_size_mm is not None:
            self.pixels_per_inch_x = self._calc_pixels_per_inch(
                screen_size_px=screen_size_px[0],
                screen_size_mm=screen_size_mm[0],
            )
            self.pixels_per_inch_y = self._calc_pixels_per_inch(
                screen_size_px=screen_size_px[1],
                screen_size_mm=screen_size_mm[1],
            )
        else:
            self.pixels_per_inch_x, self.pixels_per_inch_y = 60, 60
        self.n_lines_vertical = self._calc_n_lines(
            window_size_px=self.window_size_px[0],
            pixels_per_inch=self.pixels_per_inch_x,
        )
        self.n_lines_horizontal = self._calc_n_lines(
            window_size_px=self.window_size_px[1],
            pixels_per_inch=self.pixels_per_inch_y,
        )
        self.offset_x = self._calc_offset(
            window_size_px=self.window_size_px[0],
            n_lines=self.n_lines_vertical,
            pixels_per_inch=self.pixels_per_inch_x,
        )
        self.offset_y = self._calc_offset(
            window_size_px=self.window_size_px[1],
            n_lines=self.n_lines_horizontal,
            pixels_per_inch=self.pixels_per_inch_y,
        )

    @staticmethod
    def _calc_pixels_per_inch(screen_size_px: int, screen_size_mm: int) -> int:
        return int(screen_size_px / screen_size_mm / mm_to_inch)

    @staticmethod
    def _calc_n_lines(window_size_px: int, pixels_per_inch: int) -> int:
        return math.ceil(window_size_px / pixels_per_inch)

    @staticmethod
    def _calc_offset(window_size_px: int, n_lines: int, pixels_per_inch: int) -> int:
        return int((window_size_px - ((n_lines - 1) * pixels_per_inch)) / 2)


class GridOverlay:
    def __init__(
        self,
        window,
        opacity: int,
    ):
        self.window = window
        self.scene = window.scene()
        self.opacity = opacity

        self.view = QGraphicsView()
        self.group: Optional[QGraphicsItemGroup] = None
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

        grid = Grid(window=self.window)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255, self.opacity))

        for i in range(grid.n_lines_vertical):
            line = self.scene.addLine(
                QLineF(
                    i * grid.pixels_per_inch_x + grid.offset_x,
                    0,
                    i * grid.pixels_per_inch_x + grid.offset_x,
                    grid.window_size_px[1],
                ),
                pen,
            )
            self.group.addToGroup(line)

        for i in range(grid.n_lines_horizontal):
            line = self.scene.addLine(
                QLineF(
                    0,
                    i * grid.pixels_per_inch_y + grid.offset_y,
                    grid.window_size_px[0],
                    i * grid.pixels_per_inch_y + grid.offset_y,
                ),
                pen,
            )
            self.group.addToGroup(line)
