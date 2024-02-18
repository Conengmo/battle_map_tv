import os.path
import re
from typing import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QColor, QFont
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QSlider,
    QGraphicsTextItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QTextEdit,
)


def get_window_icon():
    path = os.path.dirname(os.path.abspath(__file__))
    return QIcon(os.path.join(path, "icon.png"))


class StyledLineEdit(QLineEdit):
    def __init__(self, max_length: int, placeholder: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaxLength(max_length)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #101010;
                color: #E5E5E5;
                padding: 9px 20px;
                border: 1px solid #3E3E40;
                border-radius: 6px;
            }
        """
        )


class StyledButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #101010;
                padding: 10px 20px;
                border: 2px solid #3E3E40;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #202020;
            }
        """
        )


class StyledSlider(QSlider):
    def __init__(self, lower: int, upper: int, default: int, *args, **kwargs):
        super().__init__(Qt.Horizontal, *args, **kwargs)  # type: ignore[attr-defined]
        self.setMinimum(lower)
        self.setMaximum(upper)
        self.setValue(default)
        self.setStyleSheet(
            """
            QSlider {
                height: 40px;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: #404040;
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background: #717173;
                border: 1px solid #3E3E40;
                width: 20px;
                margin: -15px 0;
                border-radius: 6px;
            }
        """
        )


class StyledTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            background-color: #101010;
            color: #E5E5E5;
            padding: 9px 20px;
            border: 1px solid #3E3E40;
            border-radius: 6px;
        """
        )

    def connect_text_changed_callback_with_timer(self, callback: Callable):
        typing_timer = QTimer()
        typing_timer.setSingleShot(True)
        typing_timer.timeout.connect(callback)

        def reset_typing_timer():
            typing_timer.start(700)

        self.textChanged.connect(reset_typing_timer)


class InitiativeOverlay:
    margin = 10
    padding = 5

    def __init__(self, text: str, scene: QGraphicsScene):
        self.scene = scene

        text = self._format_text(text)
        self.text_item = QGraphicsTextItem(text)
        self.text_item.setDefaultTextColor(Qt.black)  # type: ignore[attr-defined]
        font = QFont("Courier")
        font.setPointSize(20)
        self.text_item.setFont(font)
        self.text_item.setZValue(3)

        text_rect = self.text_item.boundingRect()
        background_rect = text_rect.adjusted(0, 0, 2 * self.padding, 2 * self.padding)

        self.background = QGraphicsRectItem(background_rect)
        self.background.setBrush(QColor(255, 255, 255, 220))
        self.background.setPen(QColor(255, 255, 255, 150))  # No border
        self.background.setZValue(2)

        self._put_text_in_background()

        scene.addItem(self.background)
        scene.addItem(self.text_item)

    @staticmethod
    def _format_text(text: str) -> str:
        lines = text.split("\n")
        out = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # leftpad the number if it has only one digit
            number_match = re.match(r"^\d+", line)
            if number_match:
                number = number_match.group()
                number_padded = str(number).rjust(2)
                line = re.sub(r"^\d+", number_padded, line)
            out.append(line)
        out = sorted(out)
        return "\n".join(out)

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
