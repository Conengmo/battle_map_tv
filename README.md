# battle-map-tv

Python application to display battle maps for TTRPGs on a secondary tv.


## Features

- Works natively on Linux, macOS and Windows.
- Doesn't use a browser.
- Works offline, no subscription or anything, fully open source.
- Import images to display on the tv.
- Scale and pan the image.
- Overlay a 1-inch grid.
- Automatically detect the grid in an image and scale to 1 inch.
- Save settings so images load like you had them last time.


## To-do

- Better GUI
- Release on Pypi
- Investigate running it as executable


## Technical

- Uses [Pyglet](https://github.com/pyglet/pyglet) for the graphical user interface.
- Uses [OpenCV](https://github.com/opencv/opencv-python) to detect the grid on battle maps.
- Uses [Platformdirs](https://github.com/platformdirs/platformdirs) to store settings in a local folder.
