from app.box_styles.base import BoxStyle


class ReverseTuckBox(BoxStyle):
    """
    Generates cut and crease geometry for a Reverse Tuck box.

    Panel layout (left to right): Glue Flap | W | L | W | L
      - W panels (sides) get trapezoidal dust flaps
      - L panels (front/back) get rectangular tuck flaps

    Blank Width  = Glue Flap + 2W + 2L
    Blank Height = Depth + Top Flap + Bottom Flap
    """

    def generate(
        self,
        length: float,
        width: float,
        depth: float,
        glue_flap: float = None,
        tuck_flap_depth: float = None,
        dust_flap_depth: float = None,
        **kwargs,
    ) -> dict:

        # Flap ratios below are generic industry defaults, not measured
        # from a real press. Replace with actual production values once
        # available (see README for how to calibrate these).
        GF = glue_flap if glue_flap else round(width * 0.35, 2)
        TF = tuck_flap_depth if tuck_flap_depth else round(width * 0.75, 2)
        DF = dust_flap_depth if dust_flap_depth else round(TF * 0.85, 2)
        taper = round(width * 0.15, 2)

        x0 = 0
        x1 = round(x0 + GF, 2)
        x2 = round(x1 + width, 2)
        x3 = round(x2 + length, 2)
        x4 = round(x3 + width, 2)
        x5 = round(x4 + length, 2)
        blank_width = x5

        top_margin = max(TF, DF)
        bottom_margin = top_margin

        y0 = 0
        y1 = round(top_margin, 2)
        y2 = round(y1 + depth, 2)
        y3 = round(y2 + bottom_margin, 2)
        blank_height = y3

        top_tip_y = round(y1 - DF, 2)
        bot_tip_y = round(y2 + DF, 2)
        tuck_top_y = round(y1 - TF, 2)
        tuck_bot_y = round(y2 + TF, 2)

        cut_lines = []
        crease_lines = []
        labels = []

        # Glue flap
        cut_lines.append((x0, y1, x0, y2))
        cut_lines.append((x0, y1, x1, y1))
        cut_lines.append((x0, y2, x1, y2))
        crease_lines.append((x1, y1, x1, y2))

        # Panel 1: side (W) - dust flaps
        cut_lines.append((x1, y1, x1 + taper, top_tip_y))
        cut_lines.append((x1 + taper, top_tip_y, x2 - taper, top_tip_y))
        cut_lines.append((x2 - taper, top_tip_y, x2, y1))
        crease_lines.append((x1, y1, x2, y1))

        cut_lines.append((x1, y2, x1 + taper, bot_tip_y))
        cut_lines.append((x1 + taper, bot_tip_y, x2 - taper, bot_tip_y))
        cut_lines.append((x2 - taper, bot_tip_y, x2, y2))
        crease_lines.append((x1, y2, x2, y2))

        crease_lines.append((x2, y1, x2, y2))
        labels.append(((x1 + x2) / 2, (y1 + y2) / 2, f"W\n{width}mm"))

        # Panel 2: front (L) - tuck flap
        cut_lines.append((x2, y1, x2, tuck_top_y))
        cut_lines.append((x2, tuck_top_y, x3, tuck_top_y))
        cut_lines.append((x3, y1, x3, tuck_top_y))
        crease_lines.append((x2, y1, x3, y1))

        cut_lines.append((x2, y2, x2, tuck_bot_y))
        cut_lines.append((x2, tuck_bot_y, x3, tuck_bot_y))
        cut_lines.append((x3, y2, x3, tuck_bot_y))
        crease_lines.append((x2, y2, x3, y2))

        crease_lines.append((x3, y1, x3, y2))
        labels.append(((x2 + x3) / 2, (y1 + y2) / 2, f"L\n{length}mm"))

        # Panel 3: side (W) - dust flaps
        cut_lines.append((x3, y1, x3 + taper, top_tip_y))
        cut_lines.append((x3 + taper, top_tip_y, x4 - taper, top_tip_y))
        cut_lines.append((x4 - taper, top_tip_y, x4, y1))
        crease_lines.append((x3, y1, x4, y1))

        cut_lines.append((x3, y2, x3 + taper, bot_tip_y))
        cut_lines.append((x3 + taper, bot_tip_y, x4 - taper, bot_tip_y))
        cut_lines.append((x4 - taper, bot_tip_y, x4, y2))
        crease_lines.append((x3, y2, x4, y2))

        crease_lines.append((x4, y1, x4, y2))
        labels.append(((x3 + x4) / 2, (y1 + y2) / 2, f"W\n{width}mm"))

        # Panel 4: back (L) - tuck flap, free edge
        cut_lines.append((x4, y1, x4, tuck_top_y))
        cut_lines.append((x4, tuck_top_y, x5, tuck_top_y))
        cut_lines.append((x5, y1, x5, tuck_top_y))
        crease_lines.append((x4, y1, x5, y1))

        cut_lines.append((x4, y2, x4, tuck_bot_y))
        cut_lines.append((x4, tuck_bot_y, x5, tuck_bot_y))
        cut_lines.append((x5, y2, x5, tuck_bot_y))
        crease_lines.append((x4, y2, x5, y2))

        cut_lines.append((x5, y1, x5, y2))
        labels.append(((x4 + x5) / 2, (y1 + y2) / 2, f"L\n{length}mm"))

        dimensions = {
            "horizontal_segments": [
                (x0, x1, f"{GF}mm"),
                (x1, x2, f"{width}mm"),
                (x2, x3, f"{length}mm"),
                (x3, x4, f"{width}mm"),
                (x4, x5, f"{length}mm"),
            ],
            "total_height": f"{depth}mm",
            "height_y_start": y1,
            "height_y_end": y2,
            "top_flap_height": f"{round(y1 - top_tip_y, 2)}mm",
            "top_flap_y_start": top_tip_y,
            "top_flap_y_end": y1,
            "top_flap_x": x1,
        }

        return {
            "blank_width": blank_width,
            "blank_height": blank_height,
            "cut_lines": cut_lines,
            "crease_lines": crease_lines,
            "labels": labels,
            "dimensions": dimensions,
        }
