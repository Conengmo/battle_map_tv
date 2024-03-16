import os.path
from typing import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QSlider,
    QTextEdit,
    QWidget,
    QGridLayout,
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
    def __init__(self, *args, checkable: bool = False, padding_factor: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(checkable)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #101010;
                padding: {10 * padding_factor:.0f}px {20 * padding_factor:.0f}px;
                border: 2px solid #3E3E40;
                border-radius: 6px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #202020;
            }}
            QPushButton:checked {{
                background-color: #808080;
            }}
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


class ColorSelectionButton(QPushButton):
    def __init__(self, color: str):
        super().__init__()
        self.color = color
        stylesheet_template = """
            background-color: {color};
            border: 2px solid {border_color};
            padding: 6px 0;
        """
        self.default_stylesheet = stylesheet_template.format(color=color, border_color="grey")
        self.selected_stylesheet = stylesheet_template.format(color=color, border_color="white")
        self.setStyleSheet(self.default_stylesheet)


class ColorSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        grid = FixedRowGridLayout(rows=2)
        self.setLayout(grid)
        self.colors = [
            "#ff3d00",
            "#48ABB4",
            "#009E00",
            "#9702A7",
            "#FFF800",
            "grey",
            "black",
            "white",
        ]
        self.buttons = []
        for color in self.colors:
            button = ColorSelectionButton(color=color)
            button.clicked.connect(self.create_color_selected_handler(color))
            grid.add_widget(button)
            self.buttons.append(button)
        self.selected_color: str
        self.create_color_selected_handler(self.colors[-1])()

    def create_color_selected_handler(self, color):
        def handler():
            self.selected_color = color
            for button in self.buttons:
                if button.color == color:
                    button.setStyleSheet(button.selected_stylesheet)
                else:
                    button.setStyleSheet(button.default_stylesheet)

        return handler


class FixedRowGridLayout(QGridLayout):
    def __init__(self, rows: int):
        super().__init__()
        self.rows = rows
        self._i = 0
        self._j = 0
        self.setHorizontalSpacing(8)
        self.setVerticalSpacing(5)

    def add_widget(self, widget):
        super().addWidget(widget, self._i, self._j)
        self._i += 1
        if self._i >= self.rows:
            self._i = 0
            self._j += 1
