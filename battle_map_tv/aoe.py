import math
from typing import Optional, Callable, Tuple, TYPE_CHECKING, Dict

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt, QPolygonF, QTransform, QFont
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsSceneMouseEvent,
    QAbstractGraphicsShapeItem,
    QGraphicsTextItem,
)

from battle_map_tv.aoe_rasterization import (
    circle_to_polygon,
    rasterize_cone,
    calculate_cone_points,
)
from battle_map_tv.grid import Grid

if TYPE_CHECKING:
    from battle_map_tv.window_image import ImageWindow


class AreaOfEffectManager:
    def __init__(self, window: "ImageWindow", grid: Grid):
        self.window = window
        self.scene = window.scene()
        self.shape_store: Dict[int, BaseShape] = {}
        self.rasterize = False
        self.snap_to_grid = False
        self.waiting_for: Optional[str] = None
        self.color = "white"
        self.start_point: Optional[Tuple[int, int]] = None
        self.temp_obj: Optional[BaseShape] = None
        self.callback: Optional[Callable] = None
        self.grid = grid
        self._previous_size: Optional[float] = None

    def wait_for(self, shape: str, callback: Callable):
        self.waiting_for = shape
        self.callback = callback

    def cancel(self):
        if self.temp_obj is not None:
            self.temp_obj.remove()
            self.temp_obj = None
        self.waiting_for = None
        self.start_point = None
        self.callback = None

    def clear_all(self):
        for shape_obj in list(self.shape_store.values()):
            shape_obj.remove()

    def mouse_press_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            self.start_point = (event.pos().x(), event.pos().y())
            return True
        return False

    def mouse_move_event(self, event: QMouseEvent):
        if self.waiting_for is not None:
            if self.temp_obj is not None:
                self.temp_obj.remove()
            self.temp_obj = self._create_shape_obj(event=event)
            if self.snap_to_grid:
                assert self.grid
                assert self.temp_obj
                self.temp_obj.add_label(x=event.pos().x(), y=event.pos().y(), grid=self.grid)
            return True
        return False

    def mouse_release_event(self, event: QMouseEvent) -> bool:
        if self.waiting_for is not None:
            assert self.callback
            shape_obj = self._create_shape_obj(event=event)
            shape_obj.set_is_movable()
            self.shape_store[id(shape_obj)] = shape_obj
            self.callback()
            self.cancel()
            return True
        return False

    def _create_shape_obj(self, event):
        assert self.waiting_for
        assert self.start_point
        shapes_dict = (
            area_of_effect_rasterized_shapes_to_class
            if self.rasterize
            else area_of_effect_shapes_to_class
        )
        shape_cls = shapes_dict[self.waiting_for]
        x1, y1 = self.start_point
        if self.snap_to_grid:
            x1, y1 = self.grid.snap_to_grid(x=x1, y=y1)
        shape_obj = shape_cls(
            x1=x1,
            y1=y1,
            x2=event.pos().x(),
            y2=event.pos().y(),
            manager=self,
            size=self._previous_size if event.modifiers() == Qt.ShiftModifier else None,  # type: ignore[attr-defined]
        )
        shape_obj.set_color(color=self.color)
        self._previous_size = shape_obj.size
        return shape_obj


class BaseShape:
    manager: AreaOfEffectManager
    shape: QAbstractGraphicsShapeItem
    label: QGraphicsTextItem
    label_background: QGraphicsRectItem
    size: float
    angle_snap_factor = 32 / 2 / math.pi

    def __init__(self, manager: AreaOfEffectManager):
        self.manager = manager

    def _add_shape(self, shape: QAbstractGraphicsShapeItem):
        self.shape = shape
        self.shape.mousePressEvent = self._mouse_press_event  # type: ignore[method-assign]
        self.manager.scene.addItem(self.shape)

    def remove(self):
        self.manager.scene.removeItem(self.shape)
        try:
            self.manager.scene.removeItem(self.label)
            self.manager.scene.removeItem(self.label_background)
        except AttributeError:
            pass
        try:
            del self.manager.shape_store[id(self)]
        except KeyError:
            pass

    def _mouse_press_event(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.remove()

    def _get_angle_radians(self, x1: int, y1: int, x2: int, y2: int) -> float:
        angle = math.atan2(y2 - y1, x2 - x1)
        if self.manager.snap_to_grid:
            angle = round(angle * self.angle_snap_factor) / self.angle_snap_factor
        return angle

    @staticmethod
    def _calculate_size_without_snapping(x1: int, y1: int, x2: int, y2: int) -> float:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _calculate_size(self, x1: int, y1: int, x2: int, y2: int) -> float:
        size = self._calculate_size_without_snapping(x1=x1, y1=y1, x2=x2, y2=y2)
        if self.manager.snap_to_grid:
            size = self.manager.grid.normalize_size(size=size)
        return size

    def set_color(self, color):
        color_obj = QColor(color)
        pen = QPen(color_obj)
        pen.setWidth(3)
        self.shape.setPen(pen)
        color_obj.setAlpha(127)
        self.shape.setBrush(QBrush(color_obj))
        self.shape.setZValue(1)

    def set_is_movable(self):
        self.shape.setFlag(self.shape.GraphicsItemFlag.ItemIsMovable)

    def add_label(self, x: int, y: int, grid: Grid):
        self.label = QGraphicsTextItem()
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setDefaultTextColor(QColor("black"))

        value = grid.pixels_to_feet(self.size)
        self.label.setPlainText(f"{value:.0f}")

        self.label_background = QGraphicsRectItem(self.label.boundingRect())
        self.label_background.setBrush(QColor(255, 255, 255, 220))
        self.label_background.setPen(QColor(255, 255, 255, 255))

        self.label.setPos(x + 25, y + 15)
        self.label_background.setPos(self.label.pos())

        self.label.setZValue(3)
        self.label_background.setZValue(2)

        self.manager.scene.addItem(self.label)
        self.manager.scene.addItem(self.label_background)


class Circle(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        self.size = size or self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        self._add_shape(
            QGraphicsEllipseItem(
                x1 - self.size,
                y1 - self.size,
                2 * self.size,
                2 * self.size,
            )
        )


class CircleRasterized(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        assert manager.snap_to_grid
        self.size: int = int(size or self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2))
        polygon = QPolygonF.fromList(
            [
                QPointF(*point)
                for point in circle_to_polygon(
                    x_center=x1, y_center=y1, radius=self.size, grid=manager.grid
                )
            ]
        )
        self._add_shape(QGraphicsPolygonItem(polygon))


class Square(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        if size is not None:
            self.size = size
        else:
            self.size = self._calculate_size_without_snapping(
                x1=x1, y1=y1, x2=x2, y2=y2
            ) / math.sqrt(2)
            if manager.snap_to_grid:
                self.size = manager.grid.normalize_size(size=self.size)
        angle = self._get_angle_radians(x1=x1, y1=y1, x2=x2, y2=y2)
        point_2 = (
            x1 + self.size * math.sqrt(2) * math.cos(angle),
            y1 + self.size * math.sqrt(2) * math.sin(angle),
        )
        point_1 = (
            x1 + self.size * math.cos(angle + math.pi / 4),
            y1 + self.size * math.sin(angle + math.pi / 4),
        )
        point_3 = (
            x1 + self.size * math.cos(angle - math.pi / 4),
            y1 + self.size * math.sin(angle - math.pi / 4),
        )
        self._add_shape(
            QGraphicsPolygonItem(
                QPolygonF.fromList([QPointF(*p) for p in [(x1, y1), point_1, point_2, point_3]])
            )
        )


class Cone(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        self.size = size or self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        angle = self._get_angle_radians(x1=x1, y1=y1, x2=x2, y2=y2)
        point_1, point_2 = calculate_cone_points(point_0=(x1, y1), size=self.size, angle=angle)
        triangle = QPolygonF.fromList([QPointF(*p) for p in [(x1, y1), point_1, point_2]])
        self._add_shape(QGraphicsPolygonItem(triangle))


class ConeRasterized(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        assert manager.snap_to_grid
        self.size: int = int(size or self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2))
        angle = self._get_angle_radians(x1=x1, y1=y1, x2=x2, y2=y2)
        polygon = QPolygonF.fromList(
            [
                QPointF(*point)
                for point in rasterize_cone(
                    x1=x1, y1=y1, size=self.size, angle=angle, grid=manager.grid
                )
            ]
        )
        self._add_shape(QGraphicsPolygonItem(polygon))


class Line(BaseShape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        manager: AreaOfEffectManager,
        size: Optional[float] = None,
    ):
        super().__init__(manager=manager)
        width = 20
        self.size = size or self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2)
        shape = QGraphicsRectItem(0, -width / 2, self.size, width)
        transform = QTransform()
        transform.translate(x1, y1)
        angle_radians = self._get_angle_radians(x1=x1, y1=y1, x2=x2, y2=y2)
        angle_degrees = math.degrees(angle_radians)
        transform.rotate(angle_degrees)
        shape.setTransform(transform)
        self._add_shape(shape=shape)


area_of_effect_shapes_to_class = {
    "circle": Circle,
    "square": Square,
    "cone": Cone,
    "line": Line,
}

area_of_effect_rasterized_shapes_to_class = {
    "circle": CircleRasterized,
    "square": Square,
    "cone": ConeRasterized,
    "line": Line,
}
