import argparse
import sys
from typing import Optional

from PySide6 import QtWidgets

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main(default_directory: Optional[str]):
    app = QtWidgets.QApplication([])

    screens = app.screens()

    image_window = ImageWindow()
    image_window.resize(800, 600)

    gui_window = GuiWindow(
        image_window=image_window,
        app=app,
        default_directory=default_directory,
    )

    image_window.show()
    gui_window.show()

    image_window.setScreen(screens[-1])
    gui_window.setScreen(screens[0])

    image_window.move(image_window.screen().geometry().center())
    gui_window.move(gui_window.screen().geometry().topLeft())

    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--default-directory",
        "--default-dir",
        "-d",
        dest="default_directory",
        type=str,
        required=False,
        help="Path to your maps",
    )
    args = parser.parse_args()

    main(default_directory=args.default_directory)
