import math
from random import randint
from typing import Tuple, List

import pyglet
from pyglet.window import Window


class Fire:
    # @staticmethod
    # def create_gradient(colors, width, height):
    #     gradient = pyglet.image.ImageData(width, height, 'RGBA', b'')
    #     for y in range(height):
    #         for x in range(width):
    #             color = colors[int(y / height * len(colors))]
    #             gradient.set_data(x, y, color)
    #     return gradient
    #
    # @staticmethod
    # def init():
    #     Fire.shade = Fire.create_gradient(
    #         [(247, 179, 32, i * 255 // 15) for i in range(16)], 30, 30
    #     )
    #     Fire.smoke = Fire.create_gradient(
    #         [(75, 75, 75, i * 255 // 15) for i in range(16)], 30, 30
    #     )

    def __init__(
        self,
        window: Window,
        intensity=10,
    ):
        self.batch = pyglet.graphics.Batch()
        x_range = (-0.3 * window.width, 1.3 * window.width)
        y_range = (-0.2 * window.height, 0.2 * window.height)
        self.particles: List[FireParticle] = []
        for i in range(intensity):
            self.particles.append(FireParticle(x_range=x_range, y_range=y_range, batch=self.batch))

    def draw(self):
        for particle in self.particles:
            particle.update()
        self.batch.draw()


class FireParticle:
    texture = pyglet.resource.image("fire.png").get_texture()
    texture.anchor_x = texture.width // 2
    texture.anchor_y = texture.height // 2
    alpha: int
    d_alpha: int
    d_rotation: float
    dx: float
    dy: float

    def __init__(
        self,
        x_range: Tuple[int, int],
        y_range: Tuple[int, int],
        batch,
        rise=((-20, 20), (5, 20)),
        d_alpha_range=(5, 10),
        d_rotation_range=(-5, 5),
        psize=(10, 20),
        alpha_max=150,
    ):
        self.sprite = pyglet.sprite.Sprite(img=self.texture, batch=batch)
        self.x_range = x_range
        self.y_range = y_range
        self.rise = rise
        self.d_alpha_range = d_alpha_range
        self.alpha_max = alpha_max
        self.rotation_range = (-45, 45)
        self.d_rotation_range = d_rotation_range
        self.psize = psize
        self.reset()

    def update(self):
        factor_height = max(0, self.sprite.y / (1.2 * self.y_range[1]))
        factor_visibility = self.alpha / self.alpha_max
        assert factor_visibility >= 0
        factor_combined = math.sqrt(factor_height) + factor_visibility
        self.alpha += self.d_alpha * (1 - factor_combined)
        if self.alpha <= 10:
            self.reset()
            return
        assert self.alpha >= 0, (self.alpha, self.d_alpha)
        assert self.alpha <= 255, (self.alpha, self.d_alpha)
        self.sprite.x += self.dx
        self.sprite.y += self.dy
        self.sprite.opacity = self.alpha
        self.sprite.rotation += self.d_rotation
        if (
            self.sprite.rotation < self.rotation_range[0]
            or self.sprite.rotation > self.rotation_range[1]
        ):
            self.d_rotation *= -1

    def reset(self):
        self.sprite.x = randint(*self.x_range)
        self.sprite.y = randint(*self.y_range)

        self.dx = randint(self.rise[0][0], self.rise[0][1]) / 50
        self.dy = randint(self.rise[1][0], self.rise[1][1]) / 50

        self.alpha = randint(20, 50)
        self.sprite.opacity = self.alpha
        self.d_alpha = randint(self.d_alpha_range[0], self.d_alpha_range[1])

        self.sprite.scale = randint(*self.psize) / 200

        self.sprite.rotation = randint(*self.rotation_range)
        self.d_rotation = randint(*self.d_rotation_range) / 100
