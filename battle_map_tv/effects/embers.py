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
        self.intensity = 1
        self.wind = Wind()
        self.particles = {}

    def draw(self):
        self.batch.draw()

    def update(self, dt: float):
        self.wind.update(dt)
        for _ in range(randint(0, self.intensity)):
            particle = EmberParticle(
                self.window_width,
                self.window_height,
                batch=self.batch,
                wind=self.wind,
            )
            self.particles[particle.id] = particle
        for key, particle in list(self.particles.items()):
            particle.update(dt)
            if not particle.alive:
                particle.delete()
                del self.particles[key]

    def delete(self):
        for particle in self.particles:
            particle.delete()

    def update_window_px(self, width, height):
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

    def __init__(self, window_width: int, window_height: int, batch: Batch, wind: 'Wind'):
        self.id = uuid4()
        self.window_width = window_width
        self.window_height = window_height
        self.wind = wind
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

        self.d_alpha = uniform(0.05, 0.1)

    def update(self, dt: float):
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

        # all in (x, y) coordinates
        mass = 0.001
        force_gravity = np.array((0, -9.81 * mass))
        force_wind = self.wind.force
        force_gusts = np.random.uniform(size=(2, ))
        force = np.sum((force_gravity, force_wind, force_gusts), axis=0)
        acceleration = force / mass
        displacement = (acceleration[0] * dt ** 2, acceleration[1] * dt ** 2)
        dx, dy = displacement

        self.circle.x += dx
        self.circle.y += dy
        self.circle_glow.x = self.circle.x
        self.circle_glow.y = self.circle.y

    def delete(self):
        self.circle.delete()
        self.circle_glow.delete()


class Wind:

    def __init__(self):
        self.force = np.array((0.5, 0.5))

    def update(self, dt: float):
        self.force += np.random.uniform(-0.05, 0.05, size=(2, ))
        self.force += 0.001 * (np.array((0.5, 0.5)) - self.force)
