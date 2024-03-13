import math
from typing import Dict, Union

from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem


class AreaOfEffectHolder:
    def __init__(self, scene):
        self.scene = scene
        self._objects: Dict[int, BaseAreaOfEffect] = {}

    def add(self, area_of_effect: "BaseAreaOfEffect"):
        self._objects[id(area_of_effect)] = area_of_effect

    def remove(self, area_of_effect: "BaseAreaOfEffect"):
        self._objects.pop(id(area_of_effect), None)

    def mouse_press_event(self, event):
        try:
            for area_of_effect in self._objects.values():
                area_of_effect.mouse_press_event(event)
        except RuntimeError:
            # only remove one object per click
            pass


class BaseAreaOfEffect:
    def __init__(self, size: int, holder: AreaOfEffectHolder):
        self.scene = holder.scene
        self.holder = holder
        self.holder.add(self)
        self.waiting_for_click = True
        self.shape: Union[None, QGraphicsEllipseItem, QGraphicsRectItem] = None
        self.size = size

    def _create_shape(self, x: int, y: int) -> QGraphicsEllipseItem:
        raise NotImplementedError()

    def _is_click_in_shape(self, x: int, y: int) -> bool:
        raise NotImplementedError()

    def mouse_press_event(self, event):
        x, y = event.x(), event.y()
        if self.waiting_for_click:
            self.waiting_for_click = False
            self.shape = self._create_shape(x=x, y=y)
            self.scene.addItem(self.shape)
        elif self._is_click_in_shape(x=x, y=y):
            self.remove()

    def remove(self):
        if self.shape is not None:
            self.scene.removeItem(self.shape)
        self.holder.remove(self)


class AreaOfEffectCircle(BaseAreaOfEffect):
    def _create_shape(self, x: int, y: int):
        shape = QGraphicsEllipseItem(
            x - self.size,
            y - self.size,
            2 * self.size,
            2 * self.size,
        )
        shape.setPen(QPen(QColor(255, 0, 0)))
        shape.setBrush(QBrush(QColor(255, 0, 0, 127)))
        shape.setZValue(2)
        return shape

    def _is_click_in_shape(self, x: int, y: int) -> bool:
        if self.shape is None:
            return False

        # calculate the distance between the click and the center of the circle
        dx = x - (self.shape.rect().x() + self.shape.rect().width() / 2)
        dy = y - (self.shape.rect().y() + self.shape.rect().height() / 2)
        distance = math.sqrt(dx**2 + dy**2)
        # check if the click was within the circle
        return distance <= self.size


class AreaOfEffectSquare(BaseAreaOfEffect):
    def _create_shape(self, x: int, y: int):
        shape = QGraphicsRectItem(
            x - self.size,
            y - self.size,
            2 * self.size,
            2 * self.size,
        )
        shape.setPen(QPen(QColor(255, 0, 0)))
        shape.setBrush(QBrush(QColor(255, 0, 0, 127)))
        shape.setZValue(2)
        return shape

    def _is_click_in_shape(self, x: int, y: int) -> bool:
        if self.shape is None:
            return False

        shape_x = self.shape.rect().x()
        shape_y = self.shape.rect().y()
        return (
            shape_x <= x <= shape_x + self.shape.rect().width()
            and shape_y <= y <= shape_y + self.shape.rect().height()
        )
