import argparse

import pyglet
import pyglet.gui

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main(show_fps: bool = False):
    display = pyglet.canvas.get_display()
    screens = display.get_screens()

    image_window = ImageWindow(
        caption="TV window",
        resizable=True,
        screen=screens[-1],
        show_fps=show_fps,
    )

    gm_window = GuiWindow(
        image_window=image_window,
        width=730,
        height=510,
        caption="GM window",
    )

    pyglet.app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fps", action="store_true", help="Show frames per second counter")
    args = parser.parse_args()
    main(show_fps=args.fps)
