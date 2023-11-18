import math

import cv2
import numpy as np


def main():
    image_path = r"/Users/frank/Documents/battle maps/oie_WgD5GW1KV1FB.jpg"

    # Loads an image
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # lines = cv2.HoughLines(edges, 1, np.pi / 180, 700)
    # lines_cleaned = []
    # for line in lines:
    #     rho, theta = line[0]
    #     if abs(theta - np.pi / 2) > 0.01:
    #         print('skipping line', rho, theta)
    #         continue
    #     lines_cleaned.append((rho, theta))
    #     a = np.cos(theta)
    #     b = np.sin(theta)
    #     x0 = a * rho
    #     y0 = b * rho
    #     x1 = int(x0 + 2000 * (-b))
    #     y1 = int(y0 + 2000 * (a))
    #     x2 = int(x0 - 2000 * (-b))
    #     y2 = int(y0 - 2000 * (a))
    #
    #     cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=500, minLineLength=300, maxLineGap=5)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        print(x1, y1, x2, y2)

    # for line in sorted(lines_cleaned, key=lambda x: x[0]):
    #     print(line)

    cv2.imshow('Detected Lines', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
