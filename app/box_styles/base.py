from abc import ABC, abstractmethod


class BoxStyle(ABC):
    """
    Base interface for all box styles (Reverse Tuck, Crush Lock, Snap Lock, etc).
    Adding a new style means implementing this interface in a new class.
    """

    @abstractmethod
    def generate(self, length: float, width: float, depth: float, **kwargs) -> dict:
        """
        Returns:
            {
                "blank_width": float,
                "blank_height": float,
                "cut_lines": [(x1, y1, x2, y2), ...],
                "crease_lines": [(x1, y1, x2, y2), ...],
                "labels": [(x, y, text), ...],
                "dimensions": {...}
            }
        All units in mm.
        """
        raise NotImplementedError
