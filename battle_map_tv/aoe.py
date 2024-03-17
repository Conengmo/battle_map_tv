import math
from functools import partial
from typing import Union, Optional, Type, Callable, List, Tuple

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt, QPolygonF, QTransform
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsSceneMouseEvent,
)

from battle_map_tv.utils import sign


class AreaOfEffectManager:
    def __init__(self, scene):
        self.scene = scene
        self._store: List[TypeShapes] = []
        self.waiting_for: Optional[Type[TypeShapes]] = None
        self.temp_obj: Optional[TypeShapes] = None
        self.callback: Optional[Callable] = None

    def wait_for(self, shape: str, color: str, callback: Callable):
        shape_cls = partial(area_of_effect_shapes_to_class[shape], color=color)
        self.waiting_for = shape_cls  # type: ignore[assignment]
        self.callback = callback

    def cancel(self):
        if self.temp_obj is not None:
            self.scene.removeItem(self.temp_obj)
        self.waiting_for = None
        self.callback = None

    def clear_all(self):
        for obj in self._store:
            self.scene.removeItem(obj)
        self._store = []

    def mouse_press_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            self.waiting_for = partial(  # type: ignore[assignment]
                self.waiting_for,
                x1=event.pos().x(),
                y1=event.pos().y(),
            )
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
            self._store.append(shape_obj)
            self.callback()
            self.cancel()
            return True
        return False

    def _create_shape_obj(self, event):
        assert self.waiting_for
        shape_obj = self.waiting_for(x2=event.pos().x(), y2=event.pos().y())  # type: ignore[call-arg]
        common_shape_operations(shape=shape_obj)
        self.scene.addItem(shape_obj)
        return shape_obj


def _calculate_size(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


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
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.color = color
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        super().__init__(
            x1 - size,
            y1 - size,
            2 * size,
            2 * size,
        )


class Square(DeleteShapeMixin, QGraphicsRectItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.color = color
        x2, y2 = self._fix_aspect_ratio(x1=x1, y1=y1, x2=x2, y2=y2)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top
        super().__init__(left, top, width, height)

    @staticmethod
    def _fix_aspect_ratio(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
        dx = x2 - x1
        dy = y2 - y1
        d_abs = min(abs(dx), abs(dy))
        x2 = x1 + sign(dx) * d_abs
        y2 = y1 + sign(dy) * d_abs
        return x2, y2


class Cone(DeleteShapeMixin, QGraphicsPolygonItem):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.color = color
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
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
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.color = color
        width = 20
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        super().__init__(0, -width / 2, size, width)
        self.setTransform(_get_transform(x1=x1, y1=y1, x2=x2, y2=y2))


def common_shape_operations(shape: "TypeShapes"):
    color = QColor(shape.color)  # type: ignore[assignment]
    pen = QPen(color)
    pen.setWidth(3)
    shape.setPen(pen)
    color.setAlpha(127)  # type: ignore[attr-defined]
    shape.setBrush(QBrush(color))
    shape.setZValue(1)
    shape.setFlag(shape.GraphicsItemFlag.ItemIsMovable)


TypeShapes = Union[Circle, Square, Cone]

area_of_effect_shapes_to_class = {
    "circle": Circle,
    "square": Square,
    "cone": Cone,
    "line": Line,
}
