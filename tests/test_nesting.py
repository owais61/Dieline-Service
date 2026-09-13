import pytest
from app.services.nesting import calculate_nesting, to_mm


def test_inch_to_mm_conversion():
    assert round(to_mm(1, "inch"), 2) == 25.4
    assert to_mm(100, "mm") == 100


def test_basic_nesting_fits_at_least_one_box():
    """A small box should always fit on a 25x36 inch sheet."""
    result = calculate_nesting(
        sheet_width_mm=to_mm(25, "inch"),
        sheet_height_mm=to_mm(36, "inch"),
        blank_width=234,
        blank_height=170,
        margin_mm=5,
    )
    assert result["total_boxes"] > 0
    assert result["orientation"] in ("normal", "rotated")


def test_nesting_picks_better_orientation():
    """A tall narrow box on a wide short sheet should fit better rotated."""
    result = calculate_nesting(
        sheet_width_mm=1000,
        sheet_height_mm=100,
        blank_width=90,
        blank_height=900,
        margin_mm=0,
    )
    # Rotated (90x900 -> 900x90) is the only way this fits at all
    assert result["orientation"] == "rotated"
    assert result["total_boxes"] > 0


def test_box_too_big_raises_error():
    """An oversized box should raise a clear error instead of crashing."""
    with pytest.raises(ValueError):
        calculate_nesting(
            sheet_width_mm=50,
            sheet_height_mm=50,
            blank_width=200,
            blank_height=200,
            margin_mm=5,
        )


def test_positions_count_matches_total_boxes():
    result = calculate_nesting(
        sheet_width_mm=to_mm(25, "inch"),
        sheet_height_mm=to_mm(36, "inch"),
        blank_width=234,
        blank_height=170,
        margin_mm=5,
    )
    assert len(result["positions"]) == result["total_boxes"]
