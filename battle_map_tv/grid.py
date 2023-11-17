import math

import pyglet

mm_to_inch = 0.03937007874


class Grid:
    # width_mm = 590
    # height_mm = 335

    def __init__(self, width_px, height_px, width_mm, height_mm, batch):
        self.lines = []
        self.width_px = width_px
        self.height_px = height_px
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.batch = batch
        self.draw()

    def update_screen_px(self, width_px, height_px):
        self.width_px = width_px
        self.height_px = height_px
        self.draw()

    def update_screen_mm(self, width_mm, height_mm):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.draw()

    def delete(self):
        for line in self.lines:
            line.delete()

    def draw(self):
        self.delete()
        pixels_per_inch_x = self.width_px / self.width_mm / mm_to_inch
        pixels_per_inch_y = self.height_px / self.height_mm / mm_to_inch
        n_lines_vertical = math.ceil(self.width_px / pixels_per_inch_x)
        n_lines_horizontal = math.ceil(self.height_px / pixels_per_inch_y)
        offset_x = (self.width_px - ((n_lines_vertical - 1) * pixels_per_inch_x)) / 2
        offset_y = (self.height_px - ((n_lines_horizontal - 1) * pixels_per_inch_x)) / 2
        self.lines = [
            *[
                pyglet.shapes.Line(
                    x=int(i * pixels_per_inch_x + offset_x),
                    y=0,
                    x2=int(i * pixels_per_inch_x + offset_x),
                    y2=self.height_px,
                    batch=self.batch
                )
                for i in range(n_lines_vertical)
            ],
            *[
                pyglet.shapes.Line(
                    x=0,
                    y=int(i * pixels_per_inch_y + offset_y),
                    x2=self.width_px,
                    y2=int(i * pixels_per_inch_y + offset_y),
                    batch=self.batch
                )
                for i in range(n_lines_horizontal)
            ]
        ]
