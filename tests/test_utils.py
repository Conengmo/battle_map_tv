import pytest
from battle_map_tv.utils import sign


@pytest.mark.parametrize(
    "value, expected",
    [
        (10, 1),  # positive number
        (-10, -1),  # negative number
        (0, 0),  # zero
        (0.1, 1),  # positive float
        (-0.1, -1),  # negative float
    ],
)
def test_sign(value, expected):
    assert sign(value) == expected
