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
        width=screens[-1].width,
        height=screens[-1].height,
    )

    gm_window = GMWindow(
        width=850,
        height=500,
        caption="GM window",
    )
    gm_window.switch_to()
    gm_window.add_gui(image_window=image_window)

    pyglet.app.run()


if __name__ == "__main__":
    main()
