import argparse
import sys

from PySide6 import QtWidgets

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main():
    app = QtWidgets.QApplication([])

    image_window = ImageWindow()
    image_window.setFixedSize(800, 600)
    image_window.show()

    gui_window = GuiWindow(image_window=image_window, app=app)
    gui_window.resize(800, 600)
    gui_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
