# Battle Map TV

Python application to display battle maps for TTRPGs on a secondary tv.


## Features

- Works natively on Linux, macOS and Windows.
- Doesn't use a browser.
- Works offline, no subscription or anything, fully open source.
- Import images to display on the tv.
- Scale, pan and rotate the image.
- Overlay a 1-inch grid.
- Automatically detect the grid in an image and scale to 1 inch.
- Save settings so images load like you had them last time.

## Screenshot

![Capture](https://github.com/Conengmo/battle-map-tv/assets/33519926/2f498b0b-b9f7-450f-ba83-c1293e0aed11)


## Quickstart

```
pip install git+https://github.com/conengmo/battle-map-tv
python -m battle_map_tv
```

Then drag an image from a local folder into the GM window to display it.

Add the dimensions of your secondary screen in milimeters to display the grid overlay and autoscale the image.


## To-do

- Release on Pypi
- Investigate running it as executable


## Technical

- Uses [Pyglet](https://github.com/pyglet/pyglet) for the graphical user interface.
- Uses [OpenCV](https://github.com/opencv/opencv-python) to detect the grid on battle maps.
- Uses [Hatch](https://hatch.pypa.io/latest/) to build and release the package.
- Icons by Prinbles https://prinbles.itch.io/analogue-buttons-pack-i
