import math
from functools import partial
from typing import Dict, Union

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt, QPolygonF
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPolygonItem


class AreaOfEffectHolder:
    def __init__(self, scene):
        self.scene = scene
        self._objects: Dict[int, "TypeShapes"] = {}
        self.event_coords = None
        self.waiting_for = None
        self.temp_obj = None

    def wait_for(self, shape: str, color: str):
        shape_cls = area_of_effect_shapes_to_class[shape]
        self.waiting_for = partial(shape_cls, color=color)

    def add(self, area_of_effect: "TypeShapes"):
        self._objects[id(area_of_effect)] = area_of_effect
        self.scene.addItem(area_of_effect)

    def remove(self, area_of_effect: "TypeShapes"):
        self._objects.pop(id(area_of_effect), None)
        self.scene.removeItem(area_of_effect)

    def mouse_press_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            self.event_coords = (event.pos().x(), event.pos().y())
            return True
        return False

    def mouse_move_event(self, event: QMouseEvent):
        if self.waiting_for is not None:
            if self.temp_obj is not None:
                self.scene.removeItem(self.temp_obj)
            self.temp_obj = self.waiting_for(
                *self.event_coords, *event.pos().toTuple(), holder=self
            )
            self.scene.addItem(self.temp_obj)
            return True
        return False

    def mouse_release_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            if self.temp_obj is not None:
                self.scene.removeItem(self.temp_obj)
            self.add(self.waiting_for(*self.event_coords, *event.pos().toTuple(), holder=self))
            self.waiting_for = None
            self.event_coords = None
            return True
        return False


def _calculate_size(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Circle(QGraphicsEllipseItem):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        holder: AreaOfEffectHolder,
    ):
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        super().__init__(
            x1 - size,
            y1 - size,
            2 * size,
            2 * size,
        )
        self.holder = holder
        common_shape_operations(shape=self, color=color)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.holder.remove(self)


class Square(QGraphicsRectItem):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        holder: AreaOfEffectHolder,
    ):
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        super().__init__(
            x1 - size,
            y1 - size,
            2 * size,
            2 * size,
        )
        self.holder = holder
        common_shape_operations(shape=self, color=color)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.holder.remove(self)


class Cone(QGraphicsPolygonItem):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        holder: AreaOfEffectHolder,
    ):
        angle = math.atan2(y2 - y1, x2 - x1)
        size = _calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)

        # Calculate the coordinates of the other two points
        xp2 = x1 + size * math.cos(angle + math.pi / 6)
        yp2 = y1 + size * math.sin(angle + math.pi / 6)
        xp3 = x1 + size * math.cos(angle - math.pi / 6)
        yp3 = y1 + size * math.sin(angle - math.pi / 6)

        triangle = QPolygonF.fromList(
            [
                QPointF(x1, y1),
                QPointF(xp2, yp2),
                QPointF(xp3, yp3),
            ]
        )
        super().__init__(triangle)
        self.holder = holder
        common_shape_operations(shape=self, color=color)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.holder.remove(self)


def common_shape_operations(shape: "TypeShapes", color: str):
    color = QColor(color)  # type: ignore[assignment]
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
}
