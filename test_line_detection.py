import itertools
import math
from typing import Tuple

import cv2
import numpy as np


# TODO: ask for number of lines. Start with high threshold on HoughLines, then
#  lower until roughly the right number is found


def main():
    # image_path = r"/Users/frank/Documents/battle maps/oie_WgD5GW1KV1FB.jpg"
    image_path = r"/Users/frank/Documents/battle maps/BustlingBazaarPublic.jpg"

    # Loads an image
    image = cv2.imread(image_path)

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # determine upper threshold for Canny (https://stackoverflow.com/a/16047590)
    upper_threshold, _ = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # detect edges, result is black and white image
    # lower edge should be low enough to get low contract lines
    edges = cv2.Canny(grey, upper_threshold / 10, upper_threshold, apertureSize=3)

    cv2.imwrite("canny.jpg", edges)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 300)
    lines = [tuple(line[0]) for line in lines]

    # wanted_theta = np.pi / 2
    wanted_theta = 0

    # keep only the rho values
    lines_horizontal = [line[0] for line in lines if abs(line[1] - wanted_theta) < 0.01]
    lines_horizontal = sorted(lines_horizontal)

    # merge lines that are very close together
    threshold_merge_lines = 4  # pixel
    lines_combined = [lines_horizontal[0]]
    # only add the second line if it's not too close to the first
    for rho2 in lines_horizontal:
        rho1 = lines_combined[-1]
        if abs(rho1 - rho2) <= threshold_merge_lines:
            new_rho = int((rho1 + rho2) / 2)
            lines_combined.pop()
            lines_combined.append(new_rho)
        else:
            lines_combined.append(rho2)

    for rho in sorted(lines_combined):
        point1, point2 = polar_to_cartesian(rho, theta = wanted_theta)
        cv2.line(image, point1, point2, (0, 0, 255), 2)
        print(rho)

    diffs = sorted(np.diff(lines_combined))
    print('diffs', diffs)
    avg = np.median(diffs)
    print('avg', avg)

    cv2.imshow('Detected Lines', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def polar_to_cartesian(rho: float, theta: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 2000 * (-b))
    y1 = int(y0 + 2000 * a)
    x2 = int(x0 - 2000 * (-b))
    y2 = int(y0 - 2000 * a)
    return (x1, y1), (x2, y2)


if __name__ == "__main__":
    main()
