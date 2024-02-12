from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSlider,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QPushButton, QApplication,
)

from battle_map_tv.events import global_event_dispatcher, EventKeys
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

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(80, 80, 80, 80)
        self.layout.setSpacing(50)

        self.add_row_image_buttons()
        self.add_row_scale_slider()
        self.add_row_app_controls()


    def open_file_dialog(self):
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

    def add_row_app_controls(self):
        container = QHBoxLayout()
        self.layout.addLayout(container)

        button = QPushButton("Fullscreen")
        button.clicked.connect(self.image_window.make_fullscreen)
        container.addWidget(button)

        button = QPushButton("Exit")
        button.clicked.connect(self.app.quit)
        container.addWidget(button)

    def add_row_image_buttons(self):
        container = QHBoxLayout()
        self.layout.addLayout(container)

        button = QPushButton("Add")
        button.clicked.connect(self.open_file_dialog)
        container.addWidget(button)

        button = QPushButton("Remove")
        button.clicked.connect(lambda: self.image_window.remove_image())
        container.addWidget(button)

        def callback_button_rotate_image():
            if self.image_window.image is not None:
                self.image_window.image.rotate()

        button = QPushButton("Rotate")
        button.clicked.connect(callback_button_rotate_image)
        container.addWidget(button)

    def add_row_scale_slider(self):
        container = QHBoxLayout()
        self.layout.addLayout(container)

        label = QLabel("Scale")
        container.addWidget(label)

        def slider_scale_callback(value: int):
            if self.image_window.image is not None:
                self.image_window.image.scale(normalize_slider_value(value))

        def normalize_slider_value(value: int) -> float:
            return max(value, 1) / 10

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(40)
        slider.setValue(10)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)
        slider.valueChanged.connect(slider_scale_callback)
        slider.valueChanged.connect(lambda value: label.setText(str(normalize_slider_value(value))))
        container.addWidget(slider)

        def update_slider_scale_callback(value: float):
            slider.setValue(int(value * 10))

        global_event_dispatcher.add_handler(EventKeys.change_scale, update_slider_scale_callback)

        label = QLabel(str(slider.value() / 10))
        container.addWidget(label)
