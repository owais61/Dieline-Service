from app.box_styles.reverse_tuck import ReverseTuckBox


def test_blank_width_formula():
    """Formula: Blank Width = Glue Flap + 2W + 2L"""
    box = ReverseTuckBox()
    result = box.generate(length=70, width=40, depth=110, glue_flap=15)
    expected_width = 15 + 2 * 40 + 2 * 70
    assert result["blank_width"] == expected_width


def test_blank_height_greater_than_depth():
    """Blank height must always exceed the box depth, due to top/bottom flaps."""
    box = ReverseTuckBox()
    result = box.generate(length=70, width=40, depth=110)
    assert result["blank_height"] > 110


def test_lines_are_generated():
    box = ReverseTuckBox()
    result = box.generate(length=70, width=40, depth=110)
    assert len(result["cut_lines"]) > 0
    assert len(result["crease_lines"]) > 0
