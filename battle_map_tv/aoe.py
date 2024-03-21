import math
from typing import Union, Optional, Callable, List, Tuple, TYPE_CHECKING

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt, QPolygonF, QTransform
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsSceneMouseEvent,
    QAbstractGraphicsShapeItem,
)

from battle_map_tv.grid import Grid
from battle_map_tv.utils import sign

if TYPE_CHECKING:
    from battle_map_tv.window_image import ImageWindow


class AreaOfEffectManager:
    def __init__(self, window: "ImageWindow"):
        self.window = window
        self.scene = window.scene()
        self._store: List[TypeShapes] = []
        self.snap_to_grid = False
        self.waiting_for: Optional[str] = None
        self.color = "white"
        self.start_point: Optional[Tuple[int, int]] = None
        self.temp_obj: Optional[TypeShapes] = None
        self.callback: Optional[Callable] = None
        self.grid: Optional[Grid] = None

    def wait_for(self, shape: str, callback: Callable):
        self.waiting_for = shape
        self.callback = callback

    def cancel(self):
        if self.temp_obj is not None:
            self.scene.removeItem(self.temp_obj)
        self.waiting_for = None
        self.start_point = None
        self.callback = None
        self.grid = None

    def clear_all(self):
        for obj in self._store:
            self.scene.removeItem(obj)
        self._store = []

    def mouse_press_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            self.start_point = (event.pos().x(), event.pos().y())
            return True
        return False

    def mouse_move_event(self, event: QMouseEvent):
        if self.waiting_for is not None:
            if self.temp_obj is not None:
                self.scene.removeItem(self.temp_obj)
            self.temp_obj = self._create_shape_obj(event=event)
            return True
        return False

    def mouse_release_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            assert self.callback
            shape_obj = self._create_shape_obj(event=event)
            shape_obj.setFlag(shape_obj.GraphicsItemFlag.ItemIsMovable)
            self._store.append(shape_obj)
            self.callback()
            self.cancel()
            return True
        return False

    def _optional_snap_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        if self.snap_to_grid:
            if self.grid is None:
                self.grid = Grid(window=self.window)
            x, y = self.grid.snap_to_grid(x=x, y=y)
        return x, y

    def _create_shape_obj(self, event):
        assert self.waiting_for
        assert self.start_point
        shape_cls = area_of_effect_shapes_to_class[self.waiting_for]
        x1, y1 = self._optional_snap_to_grid(*self.start_point)
        x2, y2 = event.pos().x(), event.pos().y()
        size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if self.snap_to_grid:
            assert self.grid
            size = self.grid.normalize_size(size=size)
        x2, y2 = self._optional_snap_to_grid(x=x2, y=y2)
        shape_obj = shape_cls(x1=x1, y1=y1, x2=x2, y2=y2, size=size, grid=self.grid)
        common_shape_operations(shape=shape_obj, color=self.color)
        self.scene.addItem(shape_obj)
        return shape_obj


def _get_transform(x1: int, y1: int, x2: int, y2: int) -> QTransform:
    transform = QTransform()
    transform.translate(x1, y1)
    angle = math.atan2(y2 - y1, x2 - x1)
    transform.rotate(math.degrees(angle))
    return transform


class DeleteShapeMixin:
    scene: Callable

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.scene().removeItem(self)


class Circle(DeleteShapeMixin, QGraphicsEllipseItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, size: float, grid: Optional[Grid]):
        super().__init__(
            x1 - size,
            y1 - size,
            2 * size,
            2 * size,
        )


class Square(DeleteShapeMixin, QGraphicsRectItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, size: float, grid: Optional[Grid]):
        x2, y2 = self._fix_aspect_ratio(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top
        super().__init__(left, top, width, height)

    @staticmethod
    def _fix_aspect_ratio(
        x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid]
    ) -> Tuple[int, int]:
        dx = x2 - x1
        dy = y2 - y1
        d_abs = max(abs(dx), abs(dy))
        if grid is not None:
            d_abs = grid.normalize_size(size=d_abs)
        x2 = x1 + sign(dx) * d_abs
        y2 = y1 + sign(dy) * d_abs
        return x2, y2


class Cone(DeleteShapeMixin, QGraphicsPolygonItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, size: float, grid: Optional[Grid]):
        triangle = QPolygonF.fromList(
            [
                QPointF(0, 0),
                QPointF(size, size / 2),
                QPointF(size, -size / 2),
            ]
        )
        super().__init__(triangle)
        self.setTransform(_get_transform(x1=x1, y1=y1, x2=x2, y2=y2))


class Line(DeleteShapeMixin, QGraphicsRectItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, size: float, grid: Optional[Grid]):
        width = 20
        super().__init__(0, -width / 2, size, width)
        self.setTransform(_get_transform(x1=x1, y1=y1, x2=x2, y2=y2))


def common_shape_operations(shape: QAbstractGraphicsShapeItem, color: str):
    color_obj = QColor(color)
    pen = QPen(color_obj)
    pen.setWidth(3)
    shape.setPen(pen)
    color_obj.setAlpha(127)
    shape.setBrush(QBrush(color_obj))
    shape.setZValue(1)


TypeShapes = Union[Circle, Square, Cone, Line]

area_of_effect_shapes_to_class = {
    "circle": Circle,
    "square": Square,
    "cone": Cone,
    "line": Line,
}
