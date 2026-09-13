import svgwrite


def _rotate_lines_90(lines: list, blank_width: float) -> list:
    """Rotates each line 90 degrees clockwise: (x, y) -> (y, blank_width - x)."""
    rotated = []
    for (x1, y1, x2, y2) in lines:
        nx1, ny1 = y1, blank_width - x1
        nx2, ny2 = y2, blank_width - x2
        rotated.append((nx1, ny1, nx2, ny2))
    return rotated


def _draw_horizontal_dimension(dwg, segments: list, y: float, dx: float, dy: float, margin: float,
                                tick_size: float = 1.2):
    """Draws one box instance's segment-wise dimension line below it."""
    if not segments:
        return
    x_start = segments[0][0] + dx + margin
    x_end = segments[-1][1] + dx + margin
    y_line = y + dy + margin

    dwg.add(dwg.line(start=(x_start, y_line), end=(x_end, y_line),
                      stroke="black", stroke_width=0.12))

    boundary_xs = [segments[0][0]] + [seg[1] for seg in segments]
    for bx in boundary_xs:
        sx = bx + dx + margin
        dwg.add(dwg.line(start=(sx, y_line - tick_size / 2), end=(sx, y_line + tick_size / 2),
                          stroke="black", stroke_width=0.12))

    for (seg_x1, seg_x2, text) in segments:
        mid_x = (seg_x1 + seg_x2) / 2 + dx + margin
        dwg.add(dwg.text(text, insert=(mid_x, y_line + 3.2),
                          font_size="2.2px", fill="black", text_anchor="middle"))


def _draw_vertical_dimension(dwg, y_start: float, y_end: float, x: float, dx: float, dy: float,
                              margin: float, text: str, tick_size: float = 1.2):
    """Draws one box instance's height dimension line beside it."""
    sx = x + dx + margin
    sy1 = y_start + dy + margin
    sy2 = y_end + dy + margin

    dwg.add(dwg.line(start=(sx, sy1), end=(sx, sy2), stroke="black", stroke_width=0.12))
    for sy in (sy1, sy2):
        dwg.add(dwg.line(start=(sx - tick_size / 2, sy), end=(sx + tick_size / 2, sy),
                          stroke="black", stroke_width=0.12))

    mid_y = (sy1 + sy2) / 2
    text_el = dwg.text(text, insert=(0, 0), font_size="2.2px", fill="black", text_anchor="middle")
    text_el.rotate(-90, center=(sx - 3, mid_y))
    text_el.translate(sx - 3, mid_y)
    dwg.add(text_el)


def build_sheet_svg(
    sheet_width_mm: float,
    sheet_height_mm: float,
    cut_lines: list,
    crease_lines: list,
    blank_width: float,
    blank_height: float,
    positions: list,
    orientation: str,
    margin: float = 24,
    header_lines: list = None,
    dimensions: dict = None,
) -> str:
    """
    Tiles a single box's cut/crease lines across every grid position on
    the sheet, repeating each instance's dimension lines (segment widths
    and height) alongside it.
    """
    if orientation == "rotated":
        unit_cut = _rotate_lines_90(cut_lines, blank_width)
        unit_crease = _rotate_lines_90(crease_lines, blank_width)
        # Dimension lines are only drawn for the normal orientation - rotating
        # them correctly would need extra transform logic, skipped for now.
        unit_dimensions = None
    else:
        unit_cut = cut_lines
        unit_crease = crease_lines
        unit_dimensions = dimensions

    total_w = sheet_width_mm + 2 * margin
    total_h = sheet_height_mm + 2 * margin

    dwg = svgwrite.Drawing(
        size=(f"{total_w}mm", f"{total_h}mm"),
        viewBox=f"0 0 {total_w} {total_h}",
    )

    def shift(x, y, dx, dy):
        return (x + dx + margin, y + dy + margin)

    if header_lines:
        for i, line in enumerate(header_lines):
            color = "red" if i == len(header_lines) - 1 else "black"
            dwg.add(dwg.text(line, insert=(margin, margin - 9 + i * 3.2),
                              font_size="2.8px", fill=color))

    dwg.add(dwg.rect(
        insert=(margin, margin),
        size=(sheet_width_mm, sheet_height_mm),
        fill="none", stroke="gray", stroke_width=0.3, stroke_dasharray="3,2",
    ))

    for (dx, dy) in positions:
        for (x1, y1, x2, y2) in unit_cut:
            sx1, sy1 = shift(x1, y1, dx, dy)
            sx2, sy2 = shift(x2, y2, dx, dy)
            dwg.add(dwg.line(start=(sx1, sy1), end=(sx2, sy2),
                              stroke="red", stroke_width=0.2))

        for (x1, y1, x2, y2) in unit_crease:
            sx1, sy1 = shift(x1, y1, dx, dy)
            sx2, sy2 = shift(x2, y2, dx, dy)
            dwg.add(dwg.line(start=(sx1, sy1), end=(sx2, sy2),
                              stroke="green", stroke_width=0.2,
                              stroke_dasharray="1.2,0.7"))

        if unit_dimensions:
            segments = unit_dimensions.get("horizontal_segments")
            if segments:
                _draw_horizontal_dimension(dwg, segments, blank_height + 3, dx, dy, margin)

            y_start = unit_dimensions.get("height_y_start")
            y_end = unit_dimensions.get("height_y_end")
            total_height_text = unit_dimensions.get("total_height")
            if y_start is not None and total_height_text:
                _draw_vertical_dimension(dwg, y_start, y_end, -5, dx, dy, margin, total_height_text)

            flap_y_start = unit_dimensions.get("top_flap_y_start")
            flap_y_end = unit_dimensions.get("top_flap_y_end")
            flap_text = unit_dimensions.get("top_flap_height")
            flap_x = unit_dimensions.get("top_flap_x")
            if flap_y_start is not None and flap_text and flap_x is not None:
                _draw_vertical_dimension(dwg, flap_y_start, flap_y_end, flap_x - 3, dx, dy, margin, flap_text)

    return dwg.tostring()
