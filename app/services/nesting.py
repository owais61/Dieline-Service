MM_PER_INCH = 25.4


def to_mm(value: float, unit: str) -> float:
    """Converts a sheet dimension to mm (all internal geometry is in mm)."""
    if unit.lower() in ("inch", "in", "inches"):
        return value * MM_PER_INCH
    return value


def calculate_nesting(
    sheet_width_mm: float,
    sheet_height_mm: float,
    blank_width: float,
    blank_height: float,
    margin_mm: float = 5.0,
) -> dict:
    """
    Simple grid-fitting nesting calculator.

    Tries two orientations - blank placed normally, and blank rotated 90
    degrees - and picks whichever fits more boxes on the sheet.

    This is a straightforward grid layout, not a full nesting optimizer
    (no mixed rotations or irregular packing). Sufficient for rectangular
    box blanks; a genetic-algorithm/OR-Tools based optimizer would be
    needed for irregular shapes or mixed orientations.
    """
    usable_w = sheet_width_mm - 2 * margin_mm
    usable_h = sheet_height_mm - 2 * margin_mm

    if usable_w <= 0 or usable_h <= 0:
        raise ValueError("Usable area is zero or negative after applying margin.")

    cols_a = int(usable_w // blank_width)
    rows_a = int(usable_h // blank_height)
    count_a = cols_a * rows_a

    cols_b = int(usable_w // blank_height)
    rows_b = int(usable_h // blank_width)
    count_b = cols_b * rows_b

    if count_a >= count_b:
        orientation = "normal"
        cols, rows, count = cols_a, rows_a, count_a
        cell_w, cell_h = blank_width, blank_height
    else:
        orientation = "rotated"
        cols, rows, count = cols_b, rows_b, count_b
        cell_w, cell_h = blank_height, blank_width

    if count == 0:
        raise ValueError("Box does not fit on the sheet at all.")

    used_area = count * blank_width * blank_height
    sheet_area = sheet_width_mm * sheet_height_mm
    waste_percent = round((1 - used_area / sheet_area) * 100, 2)

    positions = []
    for r in range(rows):
        for c in range(cols):
            x = margin_mm + c * cell_w
            y = margin_mm + r * cell_h
            positions.append((x, y))

    return {
        "orientation": orientation,
        "columns": cols,
        "rows": rows,
        "total_boxes": count,
        "cell_width": round(cell_w, 2),
        "cell_height": round(cell_h, 2),
        "waste_percent": waste_percent,
        "sheet_width_mm": round(sheet_width_mm, 2),
        "sheet_height_mm": round(sheet_height_mm, 2),
        "positions": positions,
    }
