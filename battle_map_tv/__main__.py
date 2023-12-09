import argparse

import pyglet
import pyglet.gui
from pyglet.gl import Config

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main(show_fps: bool = False):
    display = pyglet.canvas.get_display()
    display.get_screens()

    config = Config(double_buffer=False)
    image_window = ImageWindow(
        caption="TV window", resizable=True, show_fps=show_fps, config=config
    )

    config = Config(double_buffer=False)
    GuiWindow(image_window=image_window, width=730, height=510, caption="GM window", config=config)

    pyglet.app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fps", action="store_true", help="Show frames per second counter")
    args = parser.parse_args()
    main(show_fps=args.fps)
