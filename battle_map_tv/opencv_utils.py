from io import BytesIO

import cv2
import pyglet


def change_brightness(img, value: int):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    if value > 0:
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
    elif value < 0:
        lim = 0 - value
        v[v < lim] = 0
        v[v >= lim] = v[v >= lim] + value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def opencv_to_pyglet_texture(opencv_image) -> pyglet.image.Texture:
    as_bytes = cv2.imencode(".png", opencv_image)[1].tobytes()
    image = pyglet.image.load(filename=".png", file=BytesIO(as_bytes))
    return image.get_texture()
