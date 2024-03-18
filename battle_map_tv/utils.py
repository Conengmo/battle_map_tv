from PySide6.QtCore import QSize


def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def size_to_tuple(size: QSize) -> tuple[int, int]:
    return size.width(), size.height()
