import math
from typing import List

from pyglet.graphics import Batch
from pyglet.shapes import Line

mm_to_inch = 0.03937007874


class Grid:
    # width_mm = 590
    # height_mm = 335

    def __init__(
        self,
        screen_size_px: tuple[int, int],
        screen_size_mm: tuple[int, int],
        window_size_px: tuple[int, int],
    ):
        self.lines: List[Line] = []
        self.screen_size_px = screen_size_px
        self.screen_size_mm = screen_size_mm
        self.window_size_px = window_size_px
        self.batch = Batch()
        self.reset()

    def draw(self):
        self.batch.draw()

    def update_window_px(self, width_px: int, height_px: int):
        self.window_size_px = (width_px, height_px)
        self.reset()

    def update_screen_mm(self, width_mm: int, height_mm: int):
        self.screen_size_mm = (width_mm, height_mm)
        self.reset()

    def update_opacity(self, opacity: int):
        for line in self.lines:
            line.opacity = opacity

    def delete(self):
        for line in self.lines:
            line.delete()

    def reset(self):
        self.delete()
        pixels_per_inch_x = self.screen_size_px[0] / self.screen_size_mm[0] / mm_to_inch
        pixels_per_inch_y = self.screen_size_px[1] / self.screen_size_mm[1] / mm_to_inch
        n_lines_vertical = math.ceil(self.window_size_px[0] / pixels_per_inch_x)
        n_lines_horizontal = math.ceil(self.window_size_px[1] / pixels_per_inch_y)
        offset_x = (self.window_size_px[0] - ((n_lines_vertical - 1) * pixels_per_inch_x)) / 2
        offset_y = (self.window_size_px[1] - ((n_lines_horizontal - 1) * pixels_per_inch_x)) / 2
        self.lines = [
            *[
                Line(
                    x=int(i * pixels_per_inch_x + offset_x),
                    y=0,
                    x2=int(i * pixels_per_inch_x + offset_x),
                    y2=self.window_size_px[1],
                    batch=self.batch,
                )
                for i in range(n_lines_vertical)
            ],
            *[
                Line(
                    x=0,
                    y=int(i * pixels_per_inch_y + offset_y),
                    x2=self.window_size_px[0],
                    y2=int(i * pixels_per_inch_y + offset_y),
                    batch=self.batch,
                )
                for i in range(n_lines_horizontal)
            ],
        ]
