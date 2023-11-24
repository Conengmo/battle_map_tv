import pyglet
import pyglet.gui

from .windows import ImageWindow, GMWindow


def main():
    image_path = r"/Users/frank/Documents/battle maps/oie_WgD5GW1KV1FB.jpg"

    display = pyglet.canvas.get_display()
    screens = display.get_screens()

    image_window = ImageWindow(
        image_path=image_path,
        caption="TV window",
        resizable=True,
        screen=screens[-1],
        width=screens[-1].width,
        height=screens[-1].height,
    )

    GMWindow(
        image_window=image_window,
        width=700,
        height=500,
        caption="GM window",
        file_drops=True,
    )

    pyglet.app.run(interval=1 / 20)


if __name__ == "__main__":
    main()
