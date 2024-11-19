from typing import Tuple

from PySide6.QtCore import QSize


def size_to_tuple(size: QSize) -> Tuple[int, int]:
    return size.width(), size.height()
