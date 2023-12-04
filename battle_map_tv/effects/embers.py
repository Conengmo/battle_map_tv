from random import randint, uniform, choices

from pyglet.graphics import Batch
from pyglet.shapes import Circle


class Embers:
    def __init__(self, window_width: int, window_height: int):
        self.batch = Batch()
        intensity = self._calculate_intensity(window_width, window_height)
        self.particles = [
            EmberParticle(window_width, window_height, batch=self.batch) for _ in range(intensity)
        ]

    @staticmethod
    def _calculate_intensity(window_width: int, window_height: int) -> int:
        total_length = 2 * window_width + 2 * window_height
        intensity = int(total_length / 20)
        return intensity

    def draw(self):
        for particle in self.particles:
            particle.update()
        self.batch.draw()

    def delete(self):
        for particle in self.particles:
            particle.delete()

    def update_window_px(self, width, height):
        intensity = self._calculate_intensity(width, height)
        for _ in range(max(0, intensity - len(self.particles))):
            self.particles.append(EmberParticle(width, height, batch=self.batch))
        self.particles = self.particles[:intensity]
        for particle in self.particles:
            particle.window_width = width
            particle.window_height = height
            particle.reset()


class EmberParticle:
    alpha_min = 5
    alpha_max = 255
    alpha: float
    dx: float
    dy: float
    d_alpha: float
    color_options = [
        (246, 246, 68),
        (231, 197, 2),
        (232, 166, 2),
        (247, 209, 116),
    ]

    def __init__(self, window_width: int, window_height: int, batch: Batch):
        self.window_width = window_width
        self.window_height = window_height
        color = choices(self.color_options)[0]
        self.circle_glow = Circle(
            x=uniform(0, window_width),
            y=uniform(0, window_height),
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
        self.reset(skip_position=True)

    def reset(self, skip_position: bool = False):
        if not skip_position:
            side = choices(range(4), weights=2 * (self.window_width, self.window_height))[0]
            offset = 10
            if side == 0:  # bottom
                self.circle.x = randint(0, self.window_width)
                self.circle.y = 0 - offset
            elif side == 1:  # left
                self.circle.x = 0 - offset
                self.circle.y = randint(0, self.window_height)
            elif side == 2:  # top
                self.circle.x = randint(0, self.window_width)
                self.circle.y = self.window_height + offset
            elif side == 3:  # right
                self.circle.x = self.window_width + offset
                self.circle.y = randint(0, self.window_height)
            else:
                raise ValueError(f"undefined side {side}")

            self.circle_glow.x = self.circle.x
            self.circle_glow.y = self.circle.y

        self.alpha = uniform(3 * self.alpha_max / 4, self.alpha_max)
        self.circle.opacity = int(self.alpha)
        self.circle_glow.opacity = self.alpha_max // 2

        self.dx = uniform(0.4, 0.8) * choices([-1, 1])[0]
        self.dy = uniform(0.4, 0.8) * choices([-1, 1])[0]
        self.d_alpha = uniform(0.05, 0.1)

    def update(self):
        factor_visibility = self.circle.opacity / self.alpha_max
        self.alpha += self.d_alpha * (1 - factor_visibility)
        if self.alpha <= self.alpha_min:
            self.reset()
            return
        if (
            self.circle.x < 0 - 50
            or self.circle.x > self.window_width + 50
            or self.circle.y < 0 - 50
            or self.circle.y > self.window_height + 50
        ):
            self.reset()
            return
        self.circle.opacity = int(self.alpha)
        self.circle.x += self.dx
        self.circle.y += self.dy
        self.circle_glow.x = self.circle.x
        self.circle_glow.y = self.circle.y

    def delete(self):
        self.circle.delete()
        self.circle_glow.delete()
