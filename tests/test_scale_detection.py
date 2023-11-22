import os.path

import pytest

from battle_map_tv.scale_detection import merge_close_together_lines, find_image_scale


def test_merge_close_together_lines():
    lines = [1.0, 3.0, 4.0, 16, 32.0, 33, 36, 48, 60]
    result = merge_close_together_lines(lines, threshold_px=4)
    expected = [2.6667, 16, 33.6667, 48, 60]
    assert result == pytest.approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "image_filename, expected_px_per_inch",
    [
        ("19d33097089ed961c4660b3a0bf671e1.png", 45),
        ("27995b4c0d372367142ddf0ead558bac.png", 24),
        ("f46702b17442d0be4acc06cb7aa25ab8.jpg", 34),
        ("67ce2ff0f7dfbff87d767d2c3da67662.jpg", 35),
        ("6932a173690af4b593f8a6b52df3bd31.jpg", 72),
        ("675a18475269c17cfa20c980e7c05ea0.jpg", 100),
        ("58fed75f78a991251930918a5793051d.jpg", 70),
        ("7b1071f5cddcfa565d89dbdce45b9e39.jpg", 50),
        ("e586d099df4e4c0eb82726f6373d964f.jpg", 72),
    ],
)
def test_addition(image_filename, expected_px_per_inch):
    filepath = os.path.join("images", image_filename)
    assert os.path.exists(filepath)
    px_per_inch = find_image_scale(filepath)
    assert abs(px_per_inch - expected_px_per_inch) <= 1
