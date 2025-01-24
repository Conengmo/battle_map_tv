import math
from typing import Optional, Tuple, List

from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsItemGroup, QWidget

from battle_map_tv.utils import size_to_tuple

mm_to_inch = 0.03937007874


class Grid:
    def __init__(self, window: QWidget):
        self.window = window

        self.pixels_per_square: int = 40
        self.n_lines: Tuple[int, int]
        self.offset: Tuple[int, int]

        self.calculate()

    @staticmethod
    def _as_tuple(generator) -> Tuple[int, int]:
        values = list(generator)
        return values[0], values[1]

    @property
    def window_size_px(self):
        return size_to_tuple(self.window.size())

    def calculate(self):
        self.n_lines = self._as_tuple(
            math.ceil(self.window_size_px[i] / self.pixels_per_square) for i in range(2)
        )

        self.offset = self._as_tuple(
            int(self.window_size_px[i] / 2 - self.pixels_per_square * int(self.n_lines[i] / 2))
            for i in range(2)
        )

    def set_size(self, value: int):
        """Value is in pixels"""
        self.pixels_per_square = value
        self.calculate()

    def get_lines(self, axis: int) -> List[Tuple[int, int, int, int]]:
        assert axis in (0, 1)
        lines = []
        for i in range(self.n_lines[axis]):
            start_point = (i * self.pixels_per_square + self.offset[axis], 0)
            end_point = (
                i * self.pixels_per_square + self.offset[axis],
                self.window_size_px[1 if axis == 0 else 0],
            )
            if axis == 1:
                start_point = start_point[::-1]
                end_point = end_point[::-1]
            lines.append((start_point[0], start_point[1], end_point[0], end_point[1]))
        return lines

    def snap_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        point = (x, y)
        return self._as_tuple(
            self._snap(p=point[i], offset=self.offset[i], ppi=self.pixels_per_square, divide_by=2)
            for i in range(2)
        )

    def normalize_size(self, size: float) -> int:
        return self._snap(p=size, offset=0, ppi=self.pixels_per_square, divide_by=1)

    @staticmethod
    def _snap(p: float, offset: int, ppi: int, divide_by: int) -> int:
        return int(round(divide_by * (p - offset) / ppi) * ppi / divide_by + offset)

    def pixels_to_feet(self, value: float) -> float:
        return 5 * value / self.pixels_per_square


class GridOverlay:
    def __init__(
        self,
        window,
        grid: Grid,
        opacity: int,
    ):
        self.window = window
        self.scene = window.scene()
        self.grid = grid
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

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255, self.opacity))

        for axis in (0, 1):
            for line_coordinates in self.grid.get_lines(axis=axis):
                line = self.scene.addLine(QLineF(*line_coordinates), pen)
                self.group.addToGroup(line)
