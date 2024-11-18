import re
from typing import Dict, Optional, List

from PySide6.QtGui import QFont, QColor, Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsRectItem

from battle_map_tv.storage import get_from_storage, StorageKeys, set_in_storage


class InitiativeOverlayManager:
    def __init__(self, scene):
        self.scene = scene
        try:
            self.font_size = get_from_storage(StorageKeys.initiative_font_size)
        except KeyError:
            self.font_size = 20
        self.overlays = []

    def create(self, text: str):
        self.clear()
        if text:
            self.overlays = [
                InitiativeOverlay(text, self.scene, self.font_size).move(position=0),
                InitiativeOverlay(text, self.scene, self.font_size).move(position=4),
            ]

    def change_font_size(self, by: int):
        if self.overlays:
            self.font_size = self.font_size + by
            set_in_storage(StorageKeys.initiative_font_size, self.font_size)
            current_text = self.overlays[0].text_raw
            self.clear()
            self.create(text=current_text)

    def move(self):
        for overlay in self.overlays:
            overlay.move()

    def clear(self):
        for overlay in self.overlays:
            overlay.remove()
        self.overlays = []


class InitiativeOverlay:
    margin = 10
    padding = 5

    def __init__(self, text: str, scene: QGraphicsScene, font_size: int):
        self.text_raw = text
        self.scene = scene

        text = self._format_text(text)
        self.text_item = QGraphicsTextItem(text)
        self.text_item.setDefaultTextColor(Qt.black)  # type: ignore[attr-defined]
        font = QFont("Courier")
        font.setPointSize(font_size)
        self.text_item.setFont(font)
        self.text_item.setZValue(3)

        text_rect = self.text_item.boundingRect()
        background_rect = text_rect.adjusted(0, 0, 2 * self.padding, 2 * self.padding)

        self.background = QGraphicsRectItem(background_rect)
        self.background.setBrush(QColor(255, 255, 255, 220))
        self.background.setPen(QColor(255, 255, 255, 150))
        self.background.setZValue(2)

        scene.addItem(self.background)
        scene.addItem(self.text_item)

        self.position: int = 0

    @staticmethod
    def _format_text(text: str) -> str:
        lines = text.split("\n")
        # Group by initiative count
        out: Dict[Optional[str], List[str]] = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # leftpad the number if it has only one digit
            number_match = re.match(r"^\d+", line)
            if number_match:
                number = number_match.group()
                number_padded = str(number).rjust(2)
                line = re.sub(r"^\d+\s?", "", line)
                out.setdefault(number_padded, []).append(line)
            else:
                out.setdefault(None, []).append(line)
        # sort groups by initiative count descending, then sort lines within each group ascending
        out_lines = []
        for key in sorted(out.keys(), key=lambda k: (k is not None, k), reverse=True):
            for line in sorted(out[key]):
                if key is not None:
                    line = f"{key} {line}"
                out_lines.append(line)
        return "\n".join(out_lines)

    def move(self, position: int | None = None) -> "InitiativeOverlay":
        positions = {
            0: self.to_top_left,
            1: self.to_top_right,
            2: self.to_top_right_rotated,
            3: self.to_bottom_right_rotated,
            4: self.to_bottom_right,
            5: self.to_bottom_left,
            6: self.to_bottom_left_rotated,
            7: self.to_top_left_rotated,
        }
        if position is not None:
            self.position = position
        else:
            self.position += 1
            if self.position == 8:
                self.position = 0
        positions[self.position]()
        return self

    def _width(self) -> float:
        return self.background.boundingRect().width()

    def _height(self) -> float:
        return self.background.boundingRect().height()

    def to_top_left(self):
        self.background.setRotation(180)
        self.text_item.setRotation(180)
        self.background.setPos(self.margin + self._width(), self.margin + self._height())
        self.text_item.setPos(
            self.background.x() - self.padding, self.background.y() - self.padding
        )

    def to_top_left_rotated(self):
        self.background.setRotation(90)
        self.text_item.setRotation(90)
        self.background.setPos(self.margin + self._height(), self.margin)
        self.text_item.setPos(
            self.background.x() - self.padding, self.background.y() + self.padding
        )

    def to_top_right(self):
        self.background.setRotation(180)
        self.text_item.setRotation(180)
        self.background.setPos(self.scene.width() - self.margin, self.margin + self._height())
        self.text_item.setPos(
            self.background.x() - self.padding, self.background.y() - self.padding
        )

    def to_top_right_rotated(self):
        self.background.setRotation(270)
        self.text_item.setRotation(270)
        self.background.setPos(
            self.scene.width() - self._height() - self.margin, self.margin + self._width()
        )
        self.text_item.setPos(
            self.background.x() + self.padding, self.background.y() - self.padding
        )

    def to_bottom_left(self):
        self.background.setRotation(0)
        self.text_item.setRotation(0)
        self.background.setPos(self.margin, self.scene.height() - self._height() - self.margin)
        self.text_item.setPos(
            self.background.x() + self.padding, self.background.y() + self.padding
        )

    def to_bottom_left_rotated(self):
        self.background.setRotation(90)
        self.text_item.setRotation(90)
        self.background.setPos(
            self.margin + self._height(), self.scene.height() - self._width() - self.margin
        )
        self.text_item.setPos(
            self.background.x() - self.padding, self.background.y() + self.padding
        )

    def to_bottom_right(self):
        self.background.setRotation(0)
        self.text_item.setRotation(0)
        self.background.setPos(
            self.scene.width() - self._width() - self.margin,
            self.scene.height() - self._height() - self.margin,
        )
        self.text_item.setPos(
            self.background.x() + self.padding, self.background.y() + self.padding
        )

    def to_bottom_right_rotated(self):
        self.background.setRotation(270)
        self.text_item.setRotation(270)
        self.background.setPos(
            self.scene.width() - self._height() - self.margin, self.scene.height() - self.margin
        )
        self.text_item.setPos(
            self.background.x() + self.padding, self.background.y() - self.padding
        )

    def remove(self):
        self.scene.removeItem(self.background)
        self.scene.removeItem(self.text_item)
