import math
from typing import Optional, Callable, List, Tuple, TYPE_CHECKING

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QMouseEvent, Qt, QPolygonF, QTransform, QFont
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsSceneMouseEvent,
    QAbstractGraphicsShapeItem,
    QGraphicsScene,
    QGraphicsTextItem,
)

from battle_map_tv.aoe_rasterization import circle_to_polygon
from battle_map_tv.grid import Grid
from battle_map_tv.utils import sign

if TYPE_CHECKING:
    from battle_map_tv.window_image import ImageWindow


class AreaOfEffectManager:
    def __init__(self, window: "ImageWindow"):
        self.window = window
        self.scene = window.scene()
        self._store: List[BaseShape] = []
        self.rasterize = False
        self.snap_to_grid = False
        self.waiting_for: Optional[str] = None
        self.color = "white"
        self.start_point: Optional[Tuple[int, int]] = None
        self.temp_obj: Optional[BaseShape] = None
        self.callback: Optional[Callable] = None
        self.grid: Optional[Grid] = None

    def wait_for(self, shape: str, callback: Callable):
        self.waiting_for = shape
        self.callback = callback

    def cancel(self):
        if self.temp_obj is not None:
            self.temp_obj.remove()
        self.waiting_for = None
        self.start_point = None
        self.callback = None
        self.grid = None

    def clear_all(self):
        for shape_obj in self._store:
            shape_obj.remove()
        self._store = []

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
            if self.temp_obj is not None:
                self.temp_obj.remove()
            shape_obj = self._create_shape_obj(event=event)
            shape_obj.set_is_movable()
            self._store.append(shape_obj)
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
            self.grid = Grid(window=self.window)
            x1, y1 = self.grid.snap_to_grid(x=x1, y=y1)
        shape_obj = shape_cls(
            x1=x1,
            y1=y1,
            x2=event.pos().x(),
            y2=event.pos().y(),
            grid=self.grid,
            scene=self.scene,
        )
        shape_obj.set_color(color=self.color)
        return shape_obj


class BaseShape:
    shape: QAbstractGraphicsShapeItem
    label: QGraphicsTextItem
    label_background: QGraphicsRectItem
    size: float

    def __init__(self, scene: QGraphicsScene):
        self.shape.mousePressEvent = self._mouse_press_event  # type: ignore[method-assign]
        self.scene = scene
        self.scene.addItem(self.shape)

    def remove(self):
        self.scene.removeItem(self.shape)
        try:
            self.scene.removeItem(self.label)
            self.scene.removeItem(self.label_background)
        except AttributeError:
            pass

    def _mouse_press_event(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:  # type: ignore[attr-defined]
            self.remove()

    def _rotate(self, x1: int, y1: int, x2: int, y2: int, snap_factor: Optional[int] = None):
        transform = QTransform()
        transform.translate(x1, y1)
        angle_radians = math.atan2(y2 - y1, x2 - x1)
        angle_degrees = math.degrees(angle_radians)
        if snap_factor is not None:
            factor = snap_factor / 360
            angle_degrees = round(angle_degrees * factor) / factor
        transform.rotate(angle_degrees)
        self.shape.setTransform(transform)

    @staticmethod
    def _calculate_size(x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid]) -> float:
        size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if grid is not None:
            size = grid.normalize_size(size=size)
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

        self.scene.addItem(self.label)
        self.scene.addItem(self.label_background)


class Circle(BaseShape):
    def __init__(
        self, x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid], scene: QGraphicsScene
    ):
        self.size = self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid)
        self.shape = QGraphicsEllipseItem(
            x1 - self.size,
            y1 - self.size,
            2 * self.size,
            2 * self.size,
        )
        super().__init__(scene=scene)


class CircleRasterized(BaseShape):
    def __init__(
        self, x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid], scene: QGraphicsScene
    ):
        self.size = int(self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid))
        polygon = QPolygonF.fromList(
            [
                QPointF(*point)
                for point in circle_to_polygon(x_center=x1, y_center=y1, radius=self.size)
            ]
        )
        self.shape = QGraphicsPolygonItem(polygon)
        super().__init__(scene=scene)


class Square(BaseShape):
    def __init__(
        self, x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid], scene: QGraphicsScene
    ):
        x2, y2 = self._fix_aspect_ratio(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top
        self.shape = QGraphicsRectItem(left, top, width, height)
        self.size = width
        super().__init__(scene=scene)

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


class Cone(BaseShape):
    def __init__(
        self, x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid], scene: QGraphicsScene
    ):
        self.size = self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid)
        triangle = QPolygonF.fromList(
            [
                QPointF(0, 0),
                QPointF(self.size, self.size / 2),
                QPointF(self.size, -self.size / 2),
            ]
        )
        self.shape = QGraphicsPolygonItem(triangle)
        self._rotate(x1=x1, y1=y1, x2=x2, y2=y2, snap_factor=32 if grid is not None else None)
        super().__init__(scene=scene)


class Line(BaseShape):
    def __init__(
        self, x1: int, y1: int, x2: int, y2: int, grid: Optional[Grid], scene: QGraphicsScene
    ):
        width = 20
        self.size = self._calculate_size(x1=x1, y1=y1, x2=x2, y2=y2, grid=grid)
        self.shape = QGraphicsRectItem(0, -width / 2, self.size, width)
        self._rotate(x1=x1, y1=y1, x2=x2, y2=y2, snap_factor=32 if grid is not None else None)
        super().__init__(scene=scene)


area_of_effect_shapes_to_class = {
    "circle": Circle,
    "square": Square,
    "cone": Cone,
    "line": Line,
}

area_of_effect_rasterized_shapes_to_class = {
    "circle": CircleRasterized,
    "square": Square,
    "cone": Cone,
    "line": Line,
}
