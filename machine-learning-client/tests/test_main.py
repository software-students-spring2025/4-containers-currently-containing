import numpy as np
from main import calculate_angle, extract_hand_angles
from collections import namedtuple

# Simulated landmark object
Landmark = namedtuple('Landmark', ['x', 'y', 'z'])

def test_calculate_angle_straight_line():
    # Points in a straight line (should return ~180 degrees)
    a = Landmark(0, 0, 0)
    b = Landmark(1, 0, 0)
    c = Landmark(2, 0, 0)
    angle = calculate_angle(a, b, c)
    assert np.isclose(angle, 180.0, atol=1.0)

def test_extract_hand_angles_returns_10():
    landmarks = [Landmark(x, 0, 0) for x in range(21)]
    angles = extract_hand_angles(landmarks)
    assert len(angles) == 10
