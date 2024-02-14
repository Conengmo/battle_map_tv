from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from battle_map_tv.image import Image
from battle_map_tv.storage import get_from_storage, StorageKeys


class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            background-color: #262626;
            color: #FFFFFF;
            font-size: 18px;
        """
        )

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.image: Optional[Image] = None

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def add_image(self, image_path: str):
        self.image = Image(
            image_path=image_path,
            layout=self.layout,
            window_width_px=self.width(),
            window_height_px=self.height(),
        )

    def remove_image(self):
        if self.image is not None:
            self.image.delete()
            self.image = None

    def restore_image(self):
        try:
            previous_image = get_from_storage(StorageKeys.previous_image)
        except KeyError:
            pass
        else:
            self.remove_image()
            self.add_image(image_path=previous_image)
