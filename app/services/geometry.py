"""
Shared geometry helpers for future box styles (Crush Lock, Snap Lock, etc).

Reverse Tuck currently keeps all its geometry in reverse_tuck.py. As more
box styles are added, common patterns (trapezoid points, rounding helpers)
should move here to avoid duplication.
"""


def round_point(x: float, y: float, precision: int = 2):
    return round(x, precision), round(y, precision)
