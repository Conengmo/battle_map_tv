import pytest

from battle_map_tv.test_line_detection import merge_close_together_lines


def test_merge_close_together_lines():
    lines = [1.0, 3.0, 4.0, 16, 32.0, 33, 36, 48, 60]
    result = merge_close_together_lines(lines, threshold_px=4)
    expected = [2.6667, 16, 33.6667, 48, 60]
    assert result == pytest.approx(expected, abs=0.001)
