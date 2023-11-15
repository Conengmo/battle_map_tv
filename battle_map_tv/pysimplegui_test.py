import io
import os
from typing import Tuple

import PySimpleGUI as sg
from PIL import Image


def main():
    layout_gm = [
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), key="input_filename"),
            sg.FileBrowse(file_types=[
                ("JPEG (*.jpg)", "*.jpg"),
                ("All files (*.*)", "*.*")
            ]),
            sg.Button("Load Image"),
        ],
        [
            sg.Text("zoom"),
            sg.Slider(key="input_zoom", range=(0.1, 4), default_value=1, resolution=0.1,
                      orientation='horizontal'),
        ],
        [
            sg.Text("pan X"),
            sg.Slider(key="input_pan_x", range=(0, 1920), default_value=0, resolution=1,
                      orientation='horizontal'),
        ],
    ]

    layout_tv = [
        [sg.Image(key="output_image")],
    ]

    window_gm = sg.Window("Admin window", layout_gm, finalize=True)
    window_gm['input_zoom'].bind('<ButtonRelease-1>', ' Release')
    window_gm['input_pan_x'].bind('<ButtonRelease-1>', ' Release')

    window_tv = sg.Window("Battle map window", layout_tv, no_titlebar=False, finalize=True)
    # window_tv.maximize()

    filename = r"C:\Users\frank\Downloads\Evrys Castle final.jpg"
    with Image.open(filename) as image:
        image.load()
        bytes_io = io.BytesIO()
        image.save(bytes_io, format="PNG")
    window_tv["output_image"].update(data=bytes_io.getvalue())

    while True:
        event, values = window_gm.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # if event == "Load Image":
        #     filename = values["input_filename"]
        #     if os.path.exists(filename):
        elif event == "Double size":
            print(image.size)
            width, height = image.size
            image = image.resize(size=(width * 2, height * 2))
            print(image.size)
            bytes_io = io.BytesIO()
            image.save(bytes_io, format="PNG")
            window_tv["output_image"].update(data=bytes_io.getvalue())
        elif event == 'input_zoom Release':
            zoom = values["input_zoom"]
            image = image.resize(size=calc_new_size(image=image, zoom=zoom))
            print("zoom", zoom, image.size)
            image.save(bytes_io, format="PNG")
            window_tv["output_image"].update(data=bytes_io.getvalue())
        elif event == 'input_pan_x Release':
            window_tv["output_image"]

    window_tv.close()
    window_gm.close()


def calc_new_size(image: Image, zoom: float) -> Tuple[float, float]:
    width, height = image.size
    return round(width * zoom), round(height * zoom)


if __name__ == "__main__":
    main()
