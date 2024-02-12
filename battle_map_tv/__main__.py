import argparse
import sys

from PySide6 import QtWidgets

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main():
    app = QtWidgets.QApplication([])

    screens = app.screens()

    image_window = ImageWindow()
    image_window.resize(800, 600)

    gui_window = GuiWindow(image_window=image_window, app=app)
    gui_window.resize(800, 600)

    image_window.show()
    gui_window.show()

    image_window.setScreen(screens[-1])
    gui_window.setScreen(screens[0])

    gui_window.move(gui_window.screen().geometry().topLeft())

    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
