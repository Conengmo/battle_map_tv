import math
from typing import Optional, Tuple, List

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
            self.pixels_per_inch = self._as_tuple(
                int(screen_size_px[i] / screen_size_mm[i] / mm_to_inch) for i in range(2)
            )
        else:
            self.pixels_per_inch = (60, 60)

        self.n_lines = self._as_tuple(
            math.ceil(self.window_size_px[i] / self.pixels_per_inch[i]) for i in range(2)
        )

        self.offset = self._as_tuple(
            int((self.window_size_px[i] - ((self.n_lines[i] - 1) * self.pixels_per_inch[i])) / 2)
            for i in range(2)
        )

    @staticmethod
    def _as_tuple(generator) -> Tuple[int, int]:
        values = list(generator)
        return values[0], values[1]

    def get_lines(self, axis: int) -> List[Tuple[int, int, int, int]]:
        assert axis in (0, 1)
        lines = []
        for i in range(self.n_lines[axis]):
            start_point = (
                i * self.pixels_per_inch[axis] + self.offset[axis],
                0,
            )[:: 1 if axis == 0 else -1]
            end_point = (
                i * self.pixels_per_inch[axis] + self.offset[axis],
                self.window_size_px[1 if axis == 0 else 0],
            )[:: 1 if axis == 0 else -1]
            lines.append((start_point[0], start_point[1], end_point[0], end_point[1]))
        return lines

    def snap_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        point = (x, y)
        return self._as_tuple(
            self._snap(p=point[i], offset=self.offset[i], ppi=self.pixels_per_inch[i])
            for i in range(2)
        )

    @staticmethod
    def _snap(p: int, offset: int, ppi: int) -> int:
        return int(round(2 * (p - offset) / ppi) * ppi / 2 + offset)


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

        for axis in (0, 1):
            for line_coordinates in grid.get_lines(axis=axis):
                line = self.scene.addLine(QLineF(*line_coordinates), pen)
                self.group.addToGroup(line)
