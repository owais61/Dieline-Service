import svgwrite


def _draw_horizontal_dimension_line(dwg, segments: list, y: float, margin: float, tick_size: float = 1.5):
    """Draws a continuous dimension line with tick marks at each segment
    boundary and the mm value centered under each segment."""
    if not segments:
        return
    x_start = segments[0][0] + margin
    x_end = segments[-1][1] + margin
    y_line = y + margin

    dwg.add(dwg.line(start=(x_start, y_line), end=(x_end, y_line),
                      stroke="black", stroke_width=0.15))

    boundary_xs = [segments[0][0]] + [seg[1] for seg in segments]
    for bx in boundary_xs:
        sx = bx + margin
        dwg.add(dwg.line(start=(sx, y_line - tick_size / 2), end=(sx, y_line + tick_size / 2),
                          stroke="black", stroke_width=0.15))

    for (seg_x1, seg_x2, text) in segments:
        mid_x = (seg_x1 + seg_x2) / 2 + margin
        dwg.add(dwg.text(text, insert=(mid_x, y_line + 4),
                          font_size="2.8px", fill="black", text_anchor="middle"))


def _draw_vertical_dimension_line(dwg, y_start: float, y_end: float, x: float, margin: float,
                                   text: str, tick_size: float = 1.5):
    """Draws a vertical dimension line with the label rotated 90 degrees."""
    sx = x + margin
    sy1 = y_start + margin
    sy2 = y_end + margin

    dwg.add(dwg.line(start=(sx, sy1), end=(sx, sy2), stroke="black", stroke_width=0.15))

    for sy in (sy1, sy2):
        dwg.add(dwg.line(start=(sx - tick_size / 2, sy), end=(sx + tick_size / 2, sy),
                          stroke="black", stroke_width=0.15))

    mid_y = (sy1 + sy2) / 2
    text_el = dwg.text(text, insert=(0, 0), font_size="2.8px", fill="black", text_anchor="middle")
    text_el.rotate(-90, center=(sx - 4, mid_y))
    text_el.translate(sx - 4, mid_y)
    dwg.add(text_el)


def _draw_header(dwg, header_lines: list, margin: float):
    """Draws the top-left info block (box specs, sheet info, etc)."""
    for i, line in enumerate(header_lines):
        color = "red" if i == len(header_lines) - 1 else "black"
        dwg.add(dwg.text(line, insert=(margin, 4 + i * 3.2),
                          font_size="2.6px", fill=color))


def build_svg(blank_width: float, blank_height: float, cut_lines: list,
               crease_lines: list, labels: list = None, margin: float = 22,
               dimensions: dict = None, header_lines: list = None) -> str:
    """
    Renders box geometry as an SVG string.

    - cut_lines: red solid lines (where the material is cut)
    - crease_lines: green dashed lines (where the material is folded)
    - labels: dimension text placed inside each panel
    - dimensions: segment-wise measurement lines with tick marks
    - header_lines: info block in the top-left corner

    Margin defaults to 22mm to leave room for dimension lines and header text.
    """
    total_w = blank_width + 2 * margin
    total_h = blank_height + 2 * margin

    dwg = svgwrite.Drawing(
        size=(f"{total_w}mm", f"{total_h}mm"),
        viewBox=f"0 0 {total_w} {total_h}",
    )

    def shift(x, y):
        return (x + margin, y + margin)

    if header_lines:
        _draw_header(dwg, header_lines, margin)

    for (x1, y1, x2, y2) in cut_lines:
        sx1, sy1 = shift(x1, y1)
        sx2, sy2 = shift(x2, y2)
        dwg.add(dwg.line(start=(sx1, sy1), end=(sx2, sy2),
                          stroke="red", stroke_width=0.3))

    for (x1, y1, x2, y2) in crease_lines:
        sx1, sy1 = shift(x1, y1)
        sx2, sy2 = shift(x2, y2)
        dwg.add(dwg.line(start=(sx1, sy1), end=(sx2, sy2),
                          stroke="green", stroke_width=0.3,
                          stroke_dasharray="2,1"))

    if labels:
        for (x, y, text) in labels:
            sx, sy = shift(x, y)
            lines = text.split("\n")
            for i, line in enumerate(lines):
                dwg.add(dwg.text(line, insert=(sx, sy + i * 3),
                                  font_size="3px", fill="black",
                                  text_anchor="middle"))

    if dimensions:
        segments = dimensions.get("horizontal_segments")
        if segments:
            _draw_horizontal_dimension_line(dwg, segments, blank_height + 4, margin)

        y_start = dimensions.get("height_y_start")
        y_end = dimensions.get("height_y_end")
        total_height_text = dimensions.get("total_height")
        if y_start is not None and y_end is not None and total_height_text:
            _draw_vertical_dimension_line(dwg, y_start, y_end, -6, margin, total_height_text)

    return dwg.tostring()
