import pyglet
import pyglet.gui

from .windows import ImageWindow, GMWindow


def main():
    display = pyglet.canvas.get_display()
    screens = display.get_screens()

    image_window = ImageWindow(
        caption="TV window",
        resizable=True,
        screen=screens[-1],
    )

    gm_window = GMWindow(
        width=730,
        height=460,
        caption="GM window",
    )
    gm_window.switch_to()
    gm_window.add_gui(image_window=image_window)

    pyglet.app.run()


if __name__ == "__main__":
    main()
