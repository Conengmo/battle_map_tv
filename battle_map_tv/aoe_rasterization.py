import math
from collections import defaultdict
from typing import List, Tuple

import numpy as np

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


def rasterize_cone(size: int, angle: float, grid: Grid) -> List[Tuple[int, int]]:
    if size == 0:
        return []
    delta = grid.pixels_per_inch_mean
    point_1, point_2 = calculate_cone_points_from_size(size=size, angle=angle)
    x_points, y_points = rasterize_cone_by_pixels([(0, 0), point_1, point_2], delta=delta)
    if len(x_points) == 0:
        return []
    line = cone_points_to_line(x_points, y_points, delta=delta)
    return line


def calculate_cone_points_from_size(
    size: int, angle: float
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    # angle between center line and edge
    phi = math.atan(0.5)
    # angle between x-axis and top edge
    gamma_t = angle + phi
    # size of top edge (equal to size of bottom edge)
    size_top_edge = size / math.cos(phi)
    # coordinates of top point
    x_t = size_top_edge * math.cos(gamma_t)
    y_t = size_top_edge * math.sin(gamma_t)
    # angle between x-axis and bottom edge
    gamma_b = angle - phi
    # coordinates of bottom point
    x_b = size_top_edge * math.cos(gamma_b)
    y_b = size_top_edge * math.sin(gamma_b)
    return (x_t, y_t), (x_b, y_b)


def rasterize_cone_by_pixels(
    three_points: List[Tuple[float, float]], delta: int
) -> Tuple[np.ndarray, np.ndarray]:
    delta_half = delta / 2
    (x1, y1), (x2, y2), (x3, y3) = three_points

    x_min = delta * math.floor(min(x1, x2, x3) / delta)
    x_max = delta * math.ceil(max(x1, x2, x3) / delta)
    y_min = delta * math.floor(min(y1, y2, y3) / delta)
    y_max = delta * math.ceil(max(y1, y2, y3) / delta)

    x_linspace = np.arange(x_min - delta_half, x_max + delta_half, delta)
    y_linspace = np.arange(y_min - delta_half, y_max + delta_half, delta)

    x_points, y_points = np.meshgrid(x_linspace, y_linspace)
    x_points = x_points.ravel()
    y_points = y_points.ravel()

    out = []
    for x_a, y_a, x_b, y_b in [
        (x1, y1, x2, y2),
        (x2, y2, x3, y3),
        (x3, y3, x1, y1),
    ]:
        det = (y_b - y_a) * (x_points - x_a) - (x_b - x_a) * (y_points - y_a)
        out.append(np.sign(det).astype(int))
    out_array = np.array(out).transpose()

    in_or_out = np.all(out_array >= 0, axis=1)

    return x_points[in_or_out], y_points[in_or_out]


def cone_points_to_line(x_points, y_points, delta: int) -> List[Tuple[int, int]]:
    delta_half = delta / 2

    lines = set()

    for i in np.arange(min(x_points), max(x_points) + delta, delta):
        p = max(y_points[np.isclose(x_points, i)]) + delta_half
        lines.add(((i - delta_half, p), (i + delta_half, p)))
    for i in np.arange(max(y_points), min(y_points) - delta, -delta):
        p = max(x_points[np.isclose(y_points, i)]) + delta_half
        lines.add(((p, i - delta_half), (p, i + delta_half)))
    for i in np.arange(max(x_points), min(x_points) - delta, -delta):
        p = min(y_points[np.isclose(x_points, i)]) - delta_half
        lines.add(((i - delta_half, p), (i + delta_half, p)))
    for i in np.arange(min(y_points), max(y_points) + delta, delta):
        p = min(x_points[np.isclose(y_points, i)]) - delta_half
        lines.add(((p, i - delta_half), (p, i + delta_half)))

    lines = {((round(x1), round(y1)), (round(x2), round(y2))) for (x1, y1), (x2, y2) in lines}

    lines_lookup = defaultdict(list)
    for point_a, point_b in lines:
        lines_lookup[point_a].append(point_b)
        lines_lookup[point_b].append(point_a)

    arbitrary_start = next(iter(lines))[0]
    line = [arbitrary_start]
    while lines_lookup:
        candidates = lines_lookup[line[-1]]
        if len(candidates) == 1:
            next_coord = candidates[0]
            del lines_lookup[line[-1]]
        else:
            for candidate in candidates:
                if len(line) == 1 or candidate != line[-2]:
                    next_coord = candidate
                    candidates.remove(candidate)
                    break
            else:
                raise ValueError("No candidate found")
        line.append(next_coord)
        if next_coord == arbitrary_start:
            break

    return line


def round_to_delta(value: float, delta: int) -> int:
    return delta * round(value / delta)


def main():
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots()
    size = 30
    angle = math.radians(80)
    delta = 5

    point_1, point_2 = calculate_cone_points_from_size(size=size, angle=angle)

    ax.plot([0, point_1[0]], [0, point_1[1]], "r-")
    ax.plot([0, point_2[0]], [0, point_2[1]], "b-")
    ax.plot([point_1[0], point_2[0]], [point_1[1], point_2[1]], "g--")

    x_points, y_points = rasterize_cone_by_pixels([(0, 0), point_1, point_2], delta)
    ax.scatter(x_points, y_points, linewidth=3)

    lines = cone_points_to_line(x_points, y_points, delta)
    ax.plot(*zip(*lines), "y-")

    ax.xaxis.set_ticks(
        np.arange(
            round_to_delta(min([0, point_1[0], point_2[0]]), delta),
            round_to_delta(max([0, point_1[0], point_2[0]]), delta) + delta,
            delta,
        )
    )
    ax.yaxis.set_ticks(
        np.arange(
            round_to_delta(min([0, point_1[1], point_2[1]]), delta),
            round_to_delta(max([0, point_1[1], point_2[1]]), delta) + delta,
            delta,
        )
    )
    ax.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main()
