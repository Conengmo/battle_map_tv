import math
from functools import partial
from typing import Dict, Union

from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem


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
            size = self._calculate_size(event=event)
            self.temp_obj = self.waiting_for(*self.event_coords, size=size, holder=self)
            self.scene.addItem(self.temp_obj)
            return True
        return False

    def mouse_release_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            if self.temp_obj is not None:
                self.scene.removeItem(self.temp_obj)
            size = self._calculate_size(event=event)
            if size > 20:
                self.add(self.waiting_for(*self.event_coords, size=size, holder=self))
            self.waiting_for = None
            self.event_coords = None
            return True
        return False

    def _calculate_size(self, event: QMouseEvent) -> float:
        assert self.event_coords
        x1, y1 = self.event_coords
        x2, y2 = event.pos().x(), event.pos().y()
        size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return size


class Circle(QGraphicsEllipseItem):
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        color: str,
        holder: AreaOfEffectHolder,
    ):
        super().__init__(
            x - size,
            y - size,
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
        x: int,
        y: int,
        size: int,
        color: str,
        holder: AreaOfEffectHolder,
    ):
        super().__init__(
            x - size,
            y - size,
            2 * size,
            2 * size,
        )
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


TypeShapes = Union[Circle, Square]

area_of_effect_shapes_to_class = {
    "circle": Circle,
    "square": Square,
}
