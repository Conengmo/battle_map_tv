from PySide6.QtCore import QSize


def size_to_tuple(size: QSize) -> tuple[int, int]:
    return size.width(), size.height()
