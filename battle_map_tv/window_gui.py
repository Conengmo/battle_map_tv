from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSlider,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QPushButton,
    QApplication,
    QLineEdit,
)

from battle_map_tv.events import global_event_dispatcher, EventKeys
from battle_map_tv.storage import set_in_storage, StorageKeys, get_from_storage
from battle_map_tv.window_image import ImageWindow


class GuiWindow(QWidget):
    def __init__(self, image_window: ImageWindow, app: QApplication):
        super().__init__()
        self.image_window = image_window
        self.app = app

        self.setStyleSheet(
            """
            background-color: #262626;
            color: #FFFFFF;
            font-size: 18px;
        """
        )

        self.screen_size_mm: Tuple[int, int] = (100, 100)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignVCenter)
        self.layout.setContentsMargins(80, 80, 80, 80)
        self.layout.setSpacing(100)

        self.add_row_image_buttons()
        self.add_row_scale_slider()
        self.add_row_screen_size()
        self.add_row_grid()
        self.add_row_app_controls()

    def _create_container(self):
        container = QHBoxLayout()
        container.setSpacing(20)
        self.layout.addLayout(container)
        return container

    def add_row_app_controls(self):
        container = self._create_container()

        button = QPushButton("Fullscreen")
        button.clicked.connect(self.image_window.toggle_fullscreen)
        container.addWidget(button)

        button = QPushButton("Exit")
        button.clicked.connect(self.app.quit)
        container.addWidget(button)

    def add_row_image_buttons(self):
        container = self._create_container()

        def open_file_dialog():
            file_dialog = QFileDialog(
                caption="Select an image file",
                directory=r"C:\Users\frank\Documents\Battle maps\good",
            )
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            if file_dialog.exec_():
                selected_file = file_dialog.selectedFiles()[0]
                self.image_window.remove_image()
                self.image_window.add_image(image_path=selected_file)
                print(f"Selected file: {selected_file}")

        button = QPushButton("Add")
        button.clicked.connect(open_file_dialog)
        container.addWidget(button)

        button = QPushButton("Remove")
        button.clicked.connect(self.image_window.remove_image)
        container.addWidget(button)

        button = QPushButton("Restore")
        button.clicked.connect(self.image_window.restore_image)
        container.addWidget(button)

        def callback_button_rotate_image():
            if self.image_window.image is not None:
                self.image_window.image.rotate()

        button = QPushButton("Rotate")
        button.clicked.connect(callback_button_rotate_image)
        container.addWidget(button)

    def add_row_scale_slider(self):
        container = self._create_container()

        label = QLabel("Scale")
        container.addWidget(label)

        slider_factor = 100

        def slider_scale_callback(value: int):
            if self.image_window.image is not None:
                self.image_window.image.scale(normalize_slider_value(value))

        def normalize_slider_value(value: int) -> float:
            return max(value, 1) / slider_factor

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(4 * slider_factor)
        slider.setValue(1 * slider_factor)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(slider_factor // 2)
        slider.valueChanged.connect(slider_scale_callback)
        slider.valueChanged.connect(lambda value: label.setText(str(normalize_slider_value(value))))
        container.addWidget(slider)

        def update_slider_scale_callback(value: float):
            slider.setValue(int(value * slider_factor))

        global_event_dispatcher.add_handler(EventKeys.change_scale, update_slider_scale_callback)

        label = QLabel(str(slider.value() / slider_factor))
        label.setMinimumWidth(40)
        container.addWidget(label)

    def add_row_screen_size(self):
        container = self._create_container()

        label = QLabel("Screen size (mm)")
        container.addWidget(label)

        screen_width_input = QLineEdit()
        screen_width_input.setMaxLength(4)
        screen_width_input.setPlaceholderText("width")
        container.addWidget(screen_width_input)

        screen_height_input = QLineEdit()
        screen_height_input.setMaxLength(4)
        screen_height_input.setPlaceholderText("height")
        container.addWidget(screen_height_input)

        try:
            self.screen_size_mm = get_from_storage(StorageKeys.screen_size_mm)
        except KeyError:
            pass
        else:
            screen_width_input.setText(str(self.screen_size_mm[0]))
            screen_height_input.setText(str(self.screen_size_mm[1]))

        def set_screen_size_callback():
            try:
                width_mm = int(screen_width_input.text())
                height_mm = int(screen_height_input.text())
            except ValueError:
                pass
            else:
                set_in_storage(StorageKeys.screen_size_mm, (width_mm, height_mm))
                if self.image_window.grid is not None:
                    self.image_window.grid.update_screen_mm(width_mm, height_mm)

        button = QPushButton("Set")
        button.clicked.connect(set_screen_size_callback)
        container.addWidget(button)

    def add_row_grid(self):
        container = self._create_container()

        label = QLabel("Grid opacity")
        container.addWidget(label)

        slider_factor = 100

        def slider_callback(value: int):
            if self.image_window.grid is not None:
                self.image_window.grid.update_opacity(normalize_slider_value(value))

        def normalize_slider_value(value: int) -> int:
            return int(255 * value / slider_factor)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(slider_factor)
        slider.setValue(0.7 * slider_factor)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(slider_factor // 10)
        slider.valueChanged.connect(slider_callback)
        container.addWidget(slider)

        def toggle_grid_callback():
            if self.image_window.grid is not None:
                self.image_window.remove_grid()
            else:
                self.image_window.add_grid(
                    screen_size_mm=self.screen_size_mm,
                    opacity=normalize_slider_value(slider.value()),
                )

        button = QPushButton("Toggle grid")
        button.setStyleSheet("padding:5px 20px")
        button.clicked.connect(toggle_grid_callback)
        container.addWidget(button)
