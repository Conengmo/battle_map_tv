import pytest

from battle_map_tv.aoe import Square
from battle_map_tv.utils import sign


@pytest.mark.parametrize(
    "x1, y1, x2, y2",
    [
        (10, 20, 30, 60),
        (-10, -20, -30, -60),
        (10, -20, 30, -60),
        (-10, 20, -30, 80),
    ],
)
def test_square_fix_aspect_ratio(x1, y1, x2, y2):
    square = Square(x1, y1, x2, y2, 0, None)
    fixed_x2, fixed_y2 = square._fix_aspect_ratio(x1, y1, x2, y2, None)
    assert sign(fixed_x2) == sign(x2)
    assert sign(fixed_y2) == sign(y2)
    assert abs(fixed_x2 - x1) == abs(fixed_y2 - y1)
