from typing import Tuple, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QApplication,
)

from battle_map_tv.aoe import area_of_effect_shapes_to_class
from battle_map_tv.events import global_event_dispatcher, EventKeys
from battle_map_tv.storage import set_in_storage, StorageKeys, get_from_storage, remove_from_storage
from battle_map_tv.ui_elements import (
    StyledButton,
    StyledLineEdit,
    StyledSlider,
    get_window_icon,
    StyledTextEdit,
    ColorSelectionWindow,
    FixedRowGridLayout,
)
from battle_map_tv.window_image import ImageWindow


class GuiWindow(QWidget):
    def __init__(
        self,
        image_window: ImageWindow,
        app: QApplication,
        default_directory: Optional[str],
    ):
        super().__init__()
        self.image_window = image_window
        self.app = app
        self.default_directory = default_directory

        self.setWindowTitle("Controls")
        self.setWindowIcon(get_window_icon())
        self.setStyleSheet(
            """
            background-color: #000000;
            color: #E5E5E5;
            font-size: 18px;
        """
        )

        self.screen_size_mm: Optional[Tuple[int, int]] = None

        self._superlayout = QHBoxLayout(self)
        self._superlayout.setAlignment(Qt.AlignVCenter)  # type: ignore[attr-defined]
        self._superlayout.setContentsMargins(60, 80, 80, 80)
        self._superlayout.setSpacing(50)

        self.add_column_initiative()

        self._layout = QVBoxLayout()
        self._superlayout.addLayout(self._layout)

        self.add_row_image_buttons()
        self.add_row_scale_slider()
        self.add_row_screen_size()
        self.add_row_grid()
        self.add_row_area_of_effect()
        self.add_row_app_controls()

        # take focus away from the text area
        self.setFocus()

    def mousePressEvent(self, event):
        # user clicked in the blank space of the GUI, take focus away from other elements
        self.setFocus()
        super().mousePressEvent(event)

    def _create_container(self):
        container = QHBoxLayout()
        container.setSpacing(20)
        self._layout.addLayout(container)
        return container

    def add_row_app_controls(self):
        container = self._create_container()

        button = StyledButton("Fullscreen")
        button.clicked.connect(self.image_window.toggle_fullscreen)
        container.addWidget(button)

        button = StyledButton("Exit")
        button.clicked.connect(self.app.quit)
        container.addWidget(button)

    def add_row_image_buttons(self):
        container = self._create_container()

        def open_file_dialog():
            file_dialog = QFileDialog(
                caption="Select an image file",
                directory=self.default_directory,  # type: ignore[arg-type]
            )
            file_dialog.setFileMode(QFileDialog.ExistingFile)  # type: ignore[attr-defined]
            if file_dialog.exec_():
                selected_file = file_dialog.selectedFiles()[0]
                self.image_window.remove_image()
                self.image_window.add_image(image_path=selected_file)

        button = StyledButton("Add")
        button.clicked.connect(open_file_dialog)
        container.addWidget(button)

        button = StyledButton("Remove")
        button.clicked.connect(self.image_window.remove_image)
        container.addWidget(button)

        button = StyledButton("Restore")
        button.clicked.connect(self.image_window.restore_image)
        container.addWidget(button)

        def callback_button_rotate_image():
            if self.image_window.image is not None:
                self.image_window.image.rotate()

        button = StyledButton("Rotate")
        button.clicked.connect(callback_button_rotate_image)
        container.addWidget(button)

        def button_autoscale_callback():
            if self.image_window.image is not None:
                self.image_window.image.autoscale()

        button = StyledButton("Autoscale")
        button.clicked.connect(button_autoscale_callback)
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

        slider = StyledSlider(lower=0, upper=4 * slider_factor, default=slider_factor)
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

        screen_width_input = StyledLineEdit(max_length=4, placeholder="width")
        container.addWidget(screen_width_input)

        screen_height_input = StyledLineEdit(max_length=4, placeholder="height")
        container.addWidget(screen_height_input)

        try:
            self.screen_size_mm = get_from_storage(StorageKeys.screen_size_mm)
        except KeyError:
            pass
        else:
            assert self.screen_size_mm
            screen_width_input.setText(str(self.screen_size_mm[0]))
            screen_height_input.setText(str(self.screen_size_mm[1]))

        def set_screen_size_callback():
            width_str = screen_width_input.text()
            height_str = screen_height_input.text()
            if not width_str and not height_str:
                remove_from_storage(StorageKeys.screen_size_mm)
                self.screen_size_mm = None
                self.image_window.update_screen_size_mm(self.screen_size_mm)
                return

            try:
                width_mm = int(width_str)
                height_mm = int(height_str)
            except ValueError:
                pass
            else:
                self.screen_size_mm = (width_mm, height_mm)
                set_in_storage(StorageKeys.screen_size_mm, self.screen_size_mm)
                self.image_window.update_screen_size_mm(self.screen_size_mm)

        button = StyledButton("Set")
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

        slider = StyledSlider(lower=0, upper=slider_factor, default=int(0.7 * slider_factor))
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

        button = StyledButton("Toggle grid")
        button.clicked.connect(toggle_grid_callback)
        container.addWidget(button)

    def add_row_area_of_effect(self):
        container = self._create_container()

        color_selector = ColorSelectionWindow()
        container.addWidget(color_selector)

        def get_area_of_effect_callback(_shape: str, _button: StyledButton):
            def callback():
                if _button.isChecked():
                    self.image_window.add_area_of_effect(
                        shape=_shape,
                        color=color_selector.selected_color,
                        callback=lambda: _button.setChecked(False),
                    )
                    for i in range(grid.count()):
                        _other_button = grid.itemAt(i).widget()
                        if _other_button != _button:
                            _other_button.setChecked(False)  # type: ignore[attr-defined]
                else:
                    self.image_window.cancel_area_of_effect()

            return callback

        grid = FixedRowGridLayout(rows=2)
        container.addLayout(grid)

        for shape in area_of_effect_shapes_to_class.keys():
            button = StyledButton(shape.title(), checkable=True, padding_factor=0.7)
            button.clicked.connect(get_area_of_effect_callback(shape, button))
            grid.add_widget(button)

        button = StyledButton("Clear")
        button.clicked.connect(self.image_window.clear_area_of_effect)
        container.addWidget(button)

    def add_column_initiative(self):
        container = QVBoxLayout()
        container.setSpacing(20)
        self._superlayout.addLayout(container)

        text_area = StyledTextEdit()
        text_area.setPlaceholderText("Display initiative order")
        container.addWidget(text_area)

        def read_text_area():
            text = text_area.toPlainText().strip()
            self.image_window.add_initiative(text)

        text_area.connect_text_changed_callback_with_timer(read_text_area)

        increase_font_button = StyledButton("+")
        decrease_font_button = StyledButton("-")

        increase_font_button.clicked.connect(
            lambda: self.image_window.initiative_change_font_size(by=2)
        )
        decrease_font_button.clicked.connect(
            lambda: self.image_window.initiative_change_font_size(by=-2)
        )

        subcontainer = QHBoxLayout()
        subcontainer.setSpacing(20)
        container.addLayout(subcontainer)

        subcontainer.addWidget(increase_font_button)
        subcontainer.addWidget(decrease_font_button)
