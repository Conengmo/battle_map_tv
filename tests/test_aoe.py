import pytest
from unittest.mock import Mock, call
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, Qt
from battle_map_tv.aoe import AreaOfEffectManager, Circle, Square, Cone, Line
from battle_map_tv.utils import sign


@pytest.fixture
def mock_scene():
    return Mock()

@pytest.fixture
def aoe_manager(mock_scene):
    return AreaOfEffectManager(mock_scene)

def test_area_of_effect_manager_wait_for(aoe_manager):
    callback = Mock()
    aoe_manager.wait_for("circle", "red", callback)
    assert aoe_manager.waiting_for.func == Circle
    assert aoe_manager.waiting_for.keywords == {"color": "red"}
    assert aoe_manager.callback == callback

def test_area_of_effect_manager_cancel(aoe_manager):
    aoe_manager.wait_for("circle", "red", Mock())
    aoe_manager.cancel()
    assert aoe_manager.waiting_for is None
    assert aoe_manager.callback is None

def test_area_of_effect_manager_clear_all(aoe_manager):
    aoe_manager._store = [Mock(), Mock()]
    aoe_manager.clear_all()
    assert aoe_manager._store == []

def test_area_of_effect_manager_mouse_press_event(aoe_manager):
    aoe_manager.wait_for("circle", "red", Mock())
    event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 20), Qt.LeftButton, Qt.NoButton, Qt.NoModifier)
    assert aoe_manager.mouse_press_event(event) is True
    assert aoe_manager.waiting_for.keywords == {"color": "red", "x1": 10, "y1": 20}

def test_area_of_effect_manager_mouse_move_event(aoe_manager, mock_scene):
    aoe_manager.wait_for("circle", "red", Mock())
    aoe_manager.mouse_press_event(QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 20), Qt.LeftButton, Qt.NoButton, Qt.NoModifier))
    event = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(30, 40), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
    aoe_manager.mouse_move_event(event)
    assert mock_scene.addItem.call_count == 1

def test_area_of_effect_manager_mouse_release_event(aoe_manager, mock_scene):
    callback = Mock()
    aoe_manager.wait_for("circle", "red", callback)
    aoe_manager.mouse_press_event(QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 20), Qt.LeftButton, Qt.NoButton, Qt.NoModifier))
    event = QMouseEvent(QMouseEvent.Type.MouseButtonRelease, QPointF(30, 40), Qt.LeftButton, Qt.NoButton, Qt.NoModifier)
    assert aoe_manager.mouse_release_event(event) is True
    assert callback.call_count == 1
    assert mock_scene.addItem.call_count == 1
    assert aoe_manager.waiting_for is None
    assert aoe_manager.callback is None


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
    square = Square(x1, y1, x2, y2, "red")
    fixed_x2, fixed_y2 = square._fix_aspect_ratio(x1, y1, x2, y2)
    assert sign(fixed_x2) == sign(x2)
    assert sign(fixed_y2) == sign(y2)
    assert abs(fixed_x2 - x1) == abs(fixed_y2 - y1)
