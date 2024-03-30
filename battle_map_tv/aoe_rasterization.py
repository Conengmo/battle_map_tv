import math
from typing import List, Tuple

from battle_map_tv.grid import Grid


def circle_to_polygon(
    x_center: int, y_center: int, radius: int, grid: Grid
) -> List[Tuple[int, int]]:
    delta = grid.pixels_per_inch_mean
    radius = radius - radius % delta
    if radius < delta:
        return []
    elif radius < 2 * delta:
        return [
            (x_center + radius, y_center + radius),
            (x_center + radius, y_center - radius),
            (x_center - radius, y_center - radius),
            (x_center - radius, y_center + radius),
        ]

    edges = CircleEdges()
    start_point = (0, 0 + radius)
    edges.add_point(*start_point)
    x_prev, y_prev = start_point

    while True:
        x = x_prev + delta
        y_star = y_prev - delta

        y_circle_prev = math.sqrt(radius**2 - x_prev**2)
        y_circle = math.sqrt(radius**2 - x**2)

        surface = (x - x_prev) * (y_circle - y_star) + 0.5 * (x - x_prev) * (
            y_circle_prev - y_circle
        )

        if surface < 0.5 * delta**2:
            edges.add_point(x_prev, y_star)
            y = y_star
        else:
            y = y_prev

        if x > y:
            break
        edges.add_point(x, y)
        x_prev = x
        y_prev = y

    points = [(x + x_center, y + y_center) for x, y in edges.get_circle_line()]
    return points


class CircleEdges:
    def __init__(self):
        self._edges: List[List[Tuple[int, int]]] = [[] for _ in range(8)]

    def add_point(self, x: int, y: int):
        points_for_all_octants = [
            (x, y),
            (y, x),
            (y, -x),
            (x, -y),
            (-x, -y),
            (-y, -x),
            (-y, x),
            (-x, y),
        ]
        for i, point in enumerate(points_for_all_octants):
            self._edges[i].append(point)

    def get_circle_line(self) -> List[Tuple[int, int]]:
        final_points = []
        flip = False
        for edge in self._edges:
            if flip:
                edge = edge[::-1][1:]
            final_points.extend(edge)
            flip = False if flip else True
        return final_points


def cone_to_polygon(size: int, theta, grid):
    delta = 1  # grid.pixels_per_inch_mean  # noqa

    edges = []
    start_point = (0, 0)
    edges.append(start_point)
    x_prev, y_prev = start_point

    # angle between center line and edge
    phi = math.atan(0.5)
    # angle between x-axis and top/bottom edge
    gamma_t = theta + phi
    gamma_b = theta - phi  # noqa
    # angle between y-axis and far edge
    gamma_z = math.radians(180) - phi + gamma_t

    # angle between center line and edge
    phi = math.atan(0.5)
    # size of top edge
    a_t = size / math.cos(phi)
    # coordinate of top point
    x_t_final = a_t * math.cos(gamma_t)
    y_t_final = a_t * math.sin(gamma_t)
    edges, x_prev, y_prev = thing(
        gamma=gamma_t,
        gamma_next=gamma_z,
        edges=edges,
        p_prev=(x_prev, y_prev),
        p_final=(x_t_final, y_t_final),
    )

    return edges


def thing(gamma, gamma_next, edges, p_prev, p_final):
    delta = 1
    x_prev, y_prev = p_prev
    x_t_final, y_t_final = p_final

    while True:
        x = x_prev + delta

        y_t_prev = x_prev * math.tan(gamma)
        y_t = min(y_t_final, x * math.tan(gamma))

        area = area_under_line(x_prev=x_prev, x=x, y_prev=y_t_prev, y=y_t, y_rast_prev=y_prev)

        if x > x_t_final:
            # 'go around the corner' on to the next edge
            x_star_next = x_t_final + (y_t_final - y_prev) * math.tan(gamma_next)
            _area = area_under_line(
                x_prev=y_t,
                x=y_prev,
                y_prev=x_t_final,
                y=x_star_next,
                y_rast_prev=x_t_final,
            )
            area += _area

        if area >= 0.5 * delta**2:
            y = y_prev + delta
            edges.append((x_prev, y))
        elif x > x_t_final:
            break
        else:
            y = y_prev

        edges.append((x, y))
        x_prev = x
        y_prev = y

        if x > x_t_final:
            break

    return edges, x_prev, y_prev


def area_under_line(x_prev, x, y_prev, y, y_rast_prev) -> float:
    dx = abs(x - x_prev)
    area = dx * y_prev + 0.5 * dx * (y - y_prev) - dx * y_rast_prev
    return area


def main():
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots()
    size = 4
    a = size
    # angle between x-axis and center line
    theta = math.radians(0)
    # angle between center line and edge
    phi = math.atan(0.5)
    # angle between x-axis and top edge
    gamma_t = theta + phi
    # size of top edge
    a_t = a / math.cos(phi)
    # coordinates of top point
    x_t = a_t * math.cos(gamma_t)
    y_t = a_t * math.sin(gamma_t)
    # coordinates of end of the center line
    x_star = a * math.cos(theta)
    y_star = a * math.sin(theta)
    # size of bottom edge
    a_b = a_t
    # angle between x-axis and bottom edge
    gamma_b = theta - phi
    # coordinates of bottom point
    x_b = a_b * math.cos(gamma_b)
    y_b = a_b * math.sin(gamma_b)

    ax.plot([0, x_t], [0, y_t], "r-")
    ax.plot([0, x_b], [0, y_b], "b-")
    ax.plot([x_b, x_t], [y_b, y_t], "g--")
    ax.plot([0, x_star], [0, y_star], "k--")

    print("size top to bottom:", math.sqrt((y_t - y_b) ** 2 + (x_t - x_b) ** 2))

    edges = cone_to_polygon(size, theta, grid=None)
    ax.plot(*zip(*edges), "y-")

    ax.xaxis.set_ticks(np.arange(0, size + 1, 1.0))
    ax.yaxis.set_ticks(np.arange(-size / 2, size / 2 + 1, 1.0))
    ax.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main()
