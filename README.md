[![PyPI - Version](https://img.shields.io/pypi/v/battle-map-tv)](https://pypi.org/project/battle-map-tv/)
[![Tests](https://github.com/Conengmo/battle-map-tv/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Conengmo/battle-map-tv/actions/workflows/pytest.yml)
[![Mypy](https://github.com/Conengmo/battle-map-tv/actions/workflows/mypy.yml/badge.svg)](https://github.com/Conengmo/battle-map-tv/actions/workflows/mypy.yml)
[![Ruff](https://github.com/Conengmo/battle-map-tv/actions/workflows/ruff.yml/badge.svg)](https://github.com/Conengmo/battle-map-tv/actions/workflows/ruff.yml)

# Battle Map TV

Display battle maps for TTRPGs on a tv that lies flat horizontal on your table.

This Python application aims to do one thing: quickly show an image on your secondary screen,
in the right size and with a 1-inch grid.

For GM's with little time or who improvise their sessions: much easier to use in-session than a full blown VTT.

![screenshot](https://github.com/Conengmo/battle-map-tv/assets/33519926/fe79eca8-0dfb-4986-99cd-a747a7603604)

  
## Features
- Works natively on Linux, macOS and Windows.
- Doesn't use a browser.
- Free and open source
- Works offline
- Simple UI
- Two windows:
  - one on the TV with your map and grid on it
  - one on your GM laptop with controls
- Import local image files to display on the tv.
- Scale, pan and rotate the image.
- Store the physical size of your screen to enable grid and autoscaling.
- Overlay a 1-inch grid.
- Automatically detect the grid in an image and scale to 1 inch.
- Save settings so images load like you had them last time.


## Quickstart

This assumes you have Python installed. Probably you also want to create a virtual environment.

```
python -m pip install battle-map-tv
python -m battle_map_tv
```

Drag the TV window to your TV and make it fullscreen with the 'fullscreen' button.

Then use the 'add' button to load an image.

There are two text boxes to enter the dimensions of your secondary screen in milimeters.
This is needed to display a grid overlay and autoscale the image to 1 inch.

You can drag the image to pan and zoom with your mouse scroll wheel, or use the slider in the GM window.

Close the application with the 'exit' button.


## Technical

- Uses [PySide6]([https://github.com/pyglet/pyglet](https://wiki.qt.io/Qt_for_Python)) for the graphical user interface.
- Uses [OpenCV](https://github.com/opencv/opencv-python) to detect the grid on battle maps.
- Uses [Hatch](https://hatch.pypa.io/latest/) to build and release the package.
