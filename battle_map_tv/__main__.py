import pyglet
import pyglet.gui

from battle_map_tv.window_gui import GuiWindow
from battle_map_tv.window_image import ImageWindow


def main():
    display = pyglet.canvas.get_display()
    screens = display.get_screens()

    image_window = ImageWindow(
        caption="TV window",
        resizable=True,
        screen=screens[-1],
    )

    gm_window = GuiWindow(
        image_window=image_window,
        width=730,
        height=460,
        caption="GM window",
    )

    pyglet.app.run()


if __name__ == "__main__":
    main()
