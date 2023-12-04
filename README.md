# Battle Map TV

Python application to display battle maps for TTRPGs on a secondary tv.

For GM's with little time or who improvise their sessions. 
This application aims to do one thing only: quickly show an image on your secondary screen,
in the right size and with a 1-inch grid.


## Features

- Works natively on Linux, macOS and Windows.
- Doesn't use a browser.
- Works offline, no subscription or anything, fully open source.
- Import local image files to display on the tv.
- Scale, pan and rotate the image.
- Store the physical size of your screen to enable grid and autoscaling.
- Overlay a 1-inch grid.
- Automatically detect the grid in an image and scale to 1 inch.
- Save settings so images load like you had them last time.

## Screenshot

![Capture](https://github.com/Conengmo/battle_map_tv/assets/33519926/2f498b0b-b9f7-450f-ba83-c1293e0aed11)


## Quickstart

This assumes you have Python installed. Probably you also want to create a virtual environment.

```
pip install git+https://github.com/conengmo/battle_map_tv
python -m battle_map_tv
```

Then drag an image from a local folder into the GM window to display it.

There are two text boxes to enter the dimensions of your secondary screen in milimeters.
This is needed to display a grid overlay and autoscale the image to 1 inch.

You can drag the image to pan and zoom with your mouse scroll wheel or with the slider in the GM window.

Close the application by closing both windows.


## Technical

- Uses [Pyglet](https://github.com/pyglet/pyglet) for the graphical user interface.
- Uses [OpenCV](https://github.com/opencv/opencv-python) to detect the grid on battle maps.
- Uses [Hatch](https://hatch.pypa.io/latest/) to build and release the package.
- Icons by Prinbles https://prinbles.itch.io/analogue-buttons-pack-i
- Fire resource by DemontCode https://demontcode.itch.io/fireball
