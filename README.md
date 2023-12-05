[![PyPI - Version](https://img.shields.io/pypi/v/battle-map-tv)](https://pypi.org/project/battle-map-tv/)
[![Tests](https://github.com/Conengmo/battle-map-tv/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Conengmo/battle-map-tv/actions/workflows/pytest.yml)
[![Mypy](https://github.com/Conengmo/battle-map-tv/actions/workflows/mypy.yml/badge.svg)](https://github.com/Conengmo/battle-map-tv/actions/workflows/mypy.yml)
[![Black](https://github.com/Conengmo/battle-map-tv/actions/workflows/black.yml/badge.svg)](https://github.com/Conengmo/battle-map-tv/actions/workflows/black.yml)

# Battle Map TV

Display battle maps for TTRPGs on a secondary tv.

For GM's with little time or who improvise their sessions.

This Python application aims to do one thing: quickly show an image on your secondary screen,
in the right size and with a 1-inch grid.

![screenshot](https://github.com/Conengmo/battle-map-tv/assets/33519926/393cd1a1-fc98-4c62-834e-4d6b9b266872)


## Features

- Works natively on Linux, macOS and Windows.
- Doesn't use a browser.
- Works offline, no subscription or anything, fully open source.
- Two windows:
  - one on the TV with your map and grid on it
  - one on your GM laptop with controls
- Import local image files to display on the tv.
- Scale, pan and rotate the image.
- Store the physical size of your screen to enable grid and autoscaling.
- Overlay a 1-inch grid.
- Automatically detect the grid in an image and scale to 1 inch.
- Save settings so images load like you had them last time.
- Overlay a fire effect on your map.


## Quickstart

This assumes you have Python installed. Probably you also want to create a virtual environment.

```
python -m pip install battle-map-tv
python -m battle_map_tv
```

Drag the TV window to your TV and make it fullscreen.

Then drag an image from a local folder and drop it in the GM window.

There are two text boxes to enter the dimensions of your secondary screen in milimeters.
This is needed to display a grid overlay and autoscale the image to 1 inch.

You can drag the image to pan and zoom with your mouse scroll wheel, or use the slider in the GM window.

Close the application by closing both windows.


## Technical

- Uses [Pyglet](https://github.com/pyglet/pyglet) for the graphical user interface.
- Uses [OpenCV](https://github.com/opencv/opencv-python) to detect the grid on battle maps.
- Uses [Hatch](https://hatch.pypa.io/latest/) to build and release the package.
- Icons by Prinbles https://prinbles.itch.io/analogue-buttons-pack-i
- Fire resource by DemontCode https://demontcode.itch.io/fireball
