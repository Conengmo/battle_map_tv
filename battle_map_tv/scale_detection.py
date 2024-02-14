from typing import Tuple, List, Optional

import cv2
import numpy as np


def find_image_scale(image_path: str, show_result: bool = False) -> float:
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    edges = image_to_edges(image)

    theta_horizontal = np.pi / 2
    theta_vertical = 0

    print("--- horizontal ---")
    px_per_inch_horizontal, confidence_horizontal, lines_horizontal = optimization(
        edges=edges,
        wanted_theta=theta_horizontal,
        image_length=width,
    )
    print()
    print("--- vertical ---")
    px_per_inch_vertical, confidence_vertical, lines_vertical = optimization(
        edges=edges,
        wanted_theta=theta_vertical,
        image_length=height,
    )

    print()
    print(
        f"horizontal: {int(px_per_inch_horizontal)} px/inch (confidence {confidence_horizontal}, "
        f"vertical: {int(px_per_inch_vertical)} px/inch (confidence {confidence_vertical}"
    )

    if show_result:
        add_lines_to_image(
            image=image, rhos=lines_horizontal, wanted_theta=theta_horizontal, image_length=width
        )
        add_lines_to_image(
            image=image, rhos=lines_vertical, wanted_theta=theta_vertical, image_length=height
        )
        cv2.imshow("Detected Lines", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return (
        px_per_inch_horizontal
        if confidence_horizontal > confidence_vertical
        else px_per_inch_vertical
    )


def optimization(edges, wanted_theta: float, image_length: int) -> Tuple[float, float, List[float]]:
    hough_lines_threshold = 1500
    i = 0
    n_hits = 0
    results: List[Tuple[Optional[float], float, List[float]]] = []

    def do_step(_i, _threshold):
        _i += 1
        results.append(
            px_per_inch_detection(
                edges=edges,
                hough_lines_threshold=_threshold,
                wanted_theta=wanted_theta,
                image_length=image_length,
            )
        )
        print(
            f"Step {i}: {len(results[-1][2])} lines, threshold {_threshold}, confidence {results[-1][1]}"
        )
        return _i

    while True:
        i = do_step(i, hough_lines_threshold)
        confidence = results[-1][1]
        n_lines = len(results[-1][2])
        if n_lines == 0:
            hough_lines_threshold -= 200
        else:
            n_hits += 1
            if n_hits == 1 and i > 1:
                i = do_step(i, hough_lines_threshold + 100)
                i = do_step(i, hough_lines_threshold + 50)
                i = do_step(i, hough_lines_threshold + 25)
            if n_hits < 5:
                hough_lines_threshold -= 25
            else:
                hough_lines_threshold -= 100

        last_confidences = [result[1] for result in results[-5:]]
        last_confidences_equal = np.all(
            np.abs(np.median(last_confidences) - last_confidences) < 0.01  # type: ignore
        )
        if len(results) > 5 and confidence > 0 and last_confidences_equal:
            break
        if n_lines > 100 or i > 50:
            break
        if hough_lines_threshold <= 0:
            break
        if n_lines > 20 and confidence > 0.9:
            break

    best_result = max(results, key=lambda x: x[1])
    px_per_inch, confidence, rhos = best_result
    print(f"px per inch {px_per_inch}, {len(rhos)} lines, confidence {confidence}")
    return px_per_inch or 10.0, confidence, rhos


def px_per_inch_detection(
    edges,
    hough_lines_threshold: int,
    wanted_theta: float,
    image_length: int,
) -> Tuple[Optional[float], float, List[float]]:
    lines = edges_to_lines(edges, threshold=hough_lines_threshold)

    rhos = keep_only_lines_with_certain_orientation(lines=lines, wanted_theta=wanted_theta)

    if not rhos:
        return None, 0.0, []

    rhos = merge_close_together_lines(lines=rhos, threshold_px=image_length / 250)

    if len(rhos) <= 1:
        return None, 0.0, []

    diffs = sorted(np.diff(rhos))
    avg = float(np.median(diffs))
    n_lines_with_average_value = float(np.sum(np.abs(np.array(diffs) - avg) < image_length / 500))
    ratio_lines_with_average_value = n_lines_with_average_value / len(rhos)

    reasonable_number_of_lines = 8 < len(rhos) < 100
    # assume at least 120 lines
    reasonable_px_per_inch = avg > image_length / 120

    overall_reasonable_result = all([reasonable_number_of_lines, reasonable_px_per_inch])

    return avg, ratio_lines_with_average_value if overall_reasonable_result else 0.0, rhos


def image_to_edges(image):
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # determine upper threshold for Canny (https://stackoverflow.com/a/16047590)
    upper_threshold, _ = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # detect edges, result is black and white image
    # lower edge should be low enough to get low contract lines
    edges = cv2.Canny(grey, upper_threshold / 10, upper_threshold, apertureSize=3)

    return edges


def edges_to_lines(edges, threshold: float) -> List[Tuple[float, float]]:
    lines = cv2.HoughLines(image=edges, rho=1, theta=np.pi / 180, threshold=threshold)  # type: ignore
    if lines is None:
        return []
    lines = [tuple(line[0]) for line in lines]
    return lines


def keep_only_lines_with_certain_orientation(
    lines: List[Tuple[float, float]],
    wanted_theta: float,
) -> List[float]:
    lines_selected = [line[0] for line in lines if abs(line[1] - wanted_theta) < 0.01]
    lines_selected = sorted(lines_selected)
    return lines_selected


def merge_close_together_lines(lines: List[float], threshold_px: float) -> List[float]:
    lines_combined = []
    current_line = [lines[0]]
    for rho2 in lines[1:]:
        rho1 = current_line[-1]
        if abs(rho1 - rho2) <= threshold_px:
            current_line.append(rho2)
        else:
            lines_combined.append(float(np.mean(current_line)))
            current_line = [rho2]
    lines_combined.append(float(np.mean(current_line)))
    return lines_combined


def add_lines_to_image(image, rhos, wanted_theta, image_length):
    for rho in sorted(rhos):
        point1, point2 = polar_to_cartesian(rho=rho, theta=wanted_theta, image_length=image_length)
        cv2.line(image, point1, point2, (0, 0, 255), 2)  # type: ignore[arg-type]


def polar_to_cartesian(
    rho: float,
    theta: float,
    image_length: int,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + image_length * (-b))
    y1 = int(y0 + image_length * a)
    x2 = int(x0 - image_length * (-b))
    y2 = int(y0 - image_length * a)
    return (x1, y1), (x2, y2)


if __name__ == "__main__":
    find_image_scale(
        image_path=r"C:\Users\frank\Documents\Battle maps\f079483060cc8abafba9ea72f8bb5722.jpg",
        show_result=True,
    )
