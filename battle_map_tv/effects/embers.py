from random import randint, uniform, choices
from uuid import uuid4

import numpy as np
from pyglet.graphics import Batch
from pyglet.shapes import Circle

# https://www.youtube.com/watch?v=-Szcftzl-9Q

class Embers:
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        self.batch = Batch()
        self.intensity = self._calculate_intensity(window_width, window_height)
        self.particles = {}

    @staticmethod
    def _calculate_intensity(window_width: int, window_height: int) -> int:
        total_length = 2 * window_width + 2 * window_height
        intensity = int(total_length / 200)
        print('ember intensity', intensity)
        return intensity

    def draw(self):
        for _ in range(randint(0, self.intensity)):
            particle = EmberParticle(self.window_width, self.window_height, batch=self.batch)
            self.particles[particle.id] = particle
        for key, particle in list(self.particles.items()):
            particle.update()
            if not particle.alive:
                particle.delete()
                del self.particles[key]
        self.batch.draw()

    def delete(self):
        for particle in self.particles:
            particle.delete()

    def update_window_px(self, width, height):
        self.intensity = self._calculate_intensity(width, height)
        for particle in self.particles:
            particle.window_width = width
            particle.window_height = height


class EmberParticle:
    alpha_min = 5
    alpha_max = 255
    alpha: float
    d_alpha: float
    color_options = [
        (246, 246, 68),
        (231, 197, 2),
        (232, 166, 2),
        (247, 209, 116),
    ]

    def __init__(self, window_width: int, window_height: int, batch: Batch):
        self.id = uuid4()
        self.window_width = window_width
        self.window_height = window_height
        self.alive = True

        color = choices(self.color_options)[0]
        self.circle_glow = Circle(
            x=uniform(-20, 0),
            y=uniform(-20, 0),
            radius=6,
            color=color,
            batch=batch,
        )
        self.circle = Circle(
            x=self.circle_glow.x,
            y=self.circle_glow.y,
            radius=3,
            color=(255, 252, 197),
            batch=batch,
        )

        self.alpha = uniform(3 * self.alpha_max / 4, self.alpha_max)
        self.circle.opacity = int(self.alpha)
        self.circle_glow.opacity = self.alpha_max // 2

        self.wave_stepper = WaveStepper()

        self.d_alpha = uniform(0.05, 0.1)

    def update(self):
        factor_visibility = self.circle.opacity / self.alpha_max
        self.alpha += self.d_alpha * (1 - factor_visibility)
        if self.alpha <= self.alpha_min:
            self.alive = False
            return
        if (
            self.circle.x < 0 - 50
            or self.circle.x > self.window_width + 50
            or self.circle.y < 0 - 50
            or self.circle.y > self.window_height + 50
        ):
            self.alive = False
            return
        self.circle.opacity = int(self.alpha)

        dx, dy = self.wave_stepper.step()
        self.circle.x += dx
        self.circle.y += dy
        self.circle_glow.x = self.circle.x
        self.circle_glow.y = self.circle.y

    def delete(self):
        self.circle.delete()
        self.circle_glow.delete()


class WaveStepper:

    def __init__(self):
        self.scale = 30
        self.steps = randint(20, 25)
        length = 2 * np.pi
        self.x_wave = np.sin(np.arange(0, length, length / self.steps)) + 0.25
        self.y_wave = np.sin(np.arange(0, length, length / self.steps)) + 0.25
        roll = randint(0, self.steps)
        self.x_wave = np.roll(self.x_wave, roll)
        self.y_wave = np.roll(self.y_wave, roll + self.steps // 2)
        self.i = 0

    def step(self) -> tuple[float, float]:
        self.i += 1
        if self.i >= self.steps:
            self.i = 0
        return (
            self.x_wave[self.i] * self.scale,
            self.y_wave[self.i] * self.scale,
        )