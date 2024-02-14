import os.path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit, QPushButton, QSlider


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
        super().__init__(Qt.Horizontal, *args, **kwargs)
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
