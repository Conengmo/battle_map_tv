import math
from random import randint, choices, uniform
from typing import Tuple

import pyglet
from pyglet.graphics import Batch


class Fire:
    def __init__(self, window_width: int, window_height: int):
        self.batch = pyglet.graphics.Batch()
        intensity = self._calculate_intensity(window_width, window_height)
        self.particles = [
            FireParticle(window_width, window_height, batch=self.batch) for _ in range(intensity)
        ]

    @staticmethod
    def _calculate_intensity(window_width: int, window_height: int) -> int:
        total_length = 2 * window_width + 2 * window_height
        intensity = int(total_length / 10)
        return intensity

    def draw(self):
        for particle in self.particles:
            particle.update()
        self.batch.draw()

    def delete(self):
        for particle in self.particles:
            particle.sprite.delete()

    def update_window_px(self, width, height):
        intensity = self._calculate_intensity(width, height)
        for _ in range(max(0, intensity - len(self.particles))):
            self.particles.append(FireParticle(width, height, batch=self.batch))
        self.particles = self.particles[:intensity]
        for particle in self.particles:
            particle.window_width = width
            particle.window_height = height
            particle.reset()


class FireParticle:
    texture = pyglet.resource.image("fire.png").get_texture()
    texture.anchor_x = texture.width // 2
    texture.anchor_y = texture.height // 2
    alpha_min: int = 10
    alpha_max: int = 150
    d_alpha_range: Tuple[int, int] = (5, 10)
    d_rotation_range: Tuple[float, float] = (-0.1, 0.1)
    alpha: float
    d_alpha: float
    d_rotation: float
    x: int
    y: int
    dx: float
    dy: float
    scale_range: Tuple[float, float] = (0.05, 0.1)
    rotation_range: Tuple[int, int]
    distance_attribute: str
    distance_limit: int

    def __init__(self, window_width: int, window_height: int, batch: Batch):
        self.window_width = window_width
        self.window_height = window_height
        self.sprite = pyglet.sprite.Sprite(img=self.texture, batch=batch)
        self.reset()

    def update(self):
        distance = abs(
            getattr(self.sprite, self.distance_attribute) - getattr(self, self.distance_attribute)
        )
        factor_distance = distance / self.distance_limit
        factor_visibility = self.alpha / self.alpha_max
        factor_combined = math.sqrt(factor_distance) + factor_visibility
        self.alpha += self.d_alpha * (1 - factor_combined)
        if self.alpha <= self.alpha_min:
            self.reset()
            return
        self.sprite.opacity = int(self.alpha)
        self.sprite.x += self.dx
        self.sprite.y += self.dy
        self.sprite.rotation += self.d_rotation
        if (
            self.sprite.rotation < self.rotation_range[0]
            or self.sprite.rotation > self.rotation_range[1]
        ):
            self.d_rotation *= -1

    def reset(self):
        self.distance_limit = int(0.025 * (self.window_height + self.window_width))

        side = choices(range(4), weights=2 * (self.window_width, self.window_height))[0]
        offset = 20
        if side == 0:  # bottom
            self.x = randint(0, self.window_width)
            self.y = 0 - offset
            rise = ((-20, 20), (5, 20))
            self.rotation_range = (-45, 45)
            self.distance_attribute = "y"
        elif side == 1:  # left
            self.x = 0 - offset
            self.y = randint(0, self.window_height)
            rise = ((5, 20), (-20, 20))
            self.rotation_range = (45, 135)
            self.distance_attribute = "x"
        elif side == 2:  # top
            self.x = randint(0, self.window_width)
            self.y = self.window_height + offset
            rise = ((-20, 20), (-20, -5))
            self.rotation_range = (135, 225)
            self.distance_attribute = "y"
        elif side == 3:  # right
            self.x = self.window_width + offset
            self.y = randint(0, self.window_height)
            rise = ((-20, -5), (-20, 20))
            self.rotation_range = (225, 315)
            self.distance_attribute = "x"
        else:
            raise ValueError(f"undefined side {side}")

        self.sprite.x = self.x
        self.sprite.y = self.y

        self.dx = randint(rise[0][0], rise[0][1]) / 30
        self.dy = randint(rise[1][0], rise[1][1]) / 30

        self.alpha = self.alpha_min
        self.sprite.opacity = int(self.alpha)
        self.d_alpha = uniform(*self.d_alpha_range)

        self.sprite.scale = uniform(*self.scale_range)

        self.sprite.rotation = uniform(*self.rotation_range)
        self.d_rotation = uniform(*self.d_rotation_range)
