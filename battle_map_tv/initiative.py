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
                InitiativeOverlay(text, self.scene, self.font_size).move_to_bottom_left(),
                InitiativeOverlay(text, self.scene, self.font_size).move_to_top_right().flip(),
            ]

    def change_font_size(self, by: int):
        if self.overlays:
            self.font_size = self.font_size + by
            set_in_storage(StorageKeys.initiative_font_size, self.font_size)
            current_text = self.overlays[0].text_raw
            self.clear()
            self.create(text=current_text)

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

        self._put_text_in_background()

        scene.addItem(self.background)
        scene.addItem(self.text_item)

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

    def _put_text_in_background(self):
        self.text_item.setPos(
            self.background.x() + self.padding, self.background.y() + self.padding
        )

    def move_to_bottom_left(self):
        self.background.setPos(
            self.margin, self.scene.height() - self.background.boundingRect().height() - self.margin
        )
        self._put_text_in_background()
        return self

    def move_to_top_right(self):
        self.background.setPos(
            self.scene.width() - self.background.boundingRect().width() - self.margin, self.margin
        )
        self._put_text_in_background()
        return self

    def flip(self):
        self.text_item.setRotation(180)
        self.background.setRotation(180)
        self.background.setPos(
            self.background.x() + self.background.boundingRect().width(),
            self.background.y() + self.background.boundingRect().height(),
        )
        self.text_item.setPos(
            self.background.x() - self.padding, self.background.y() - self.padding
        )
        return self

    def remove(self):
        self.scene.removeItem(self.background)
        self.scene.removeItem(self.text_item)
