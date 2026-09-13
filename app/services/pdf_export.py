import cairosvg


def svg_to_pdf(svg_string: str) -> bytes:
    """Converts an SVG string to print-ready PDF bytes."""
    return cairosvg.svg2pdf(bytestring=svg_string.encode("utf-8"))


def svg_to_png(svg_string: str, scale: float = 4.0) -> bytes:
    """Converts an SVG string to PNG bytes."""
    return cairosvg.svg2png(bytestring=svg_string.encode("utf-8"), scale=scale)
