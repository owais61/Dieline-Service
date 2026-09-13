from fastapi import APIRouter
from fastapi.responses import Response

from app.models.schemas import DielineRequest, SheetLayoutRequest
from app.box_styles.reverse_tuck import ReverseTuckBox
from app.services.svg_generator import build_svg
from app.services.pdf_export import svg_to_pdf, svg_to_png
from app.services.nesting import calculate_nesting, to_mm
from app.services.sheet_svg_generator import build_sheet_svg

router = APIRouter(prefix="/api/dieline", tags=["Dieline"])


def _generate_svg_string(payload: DielineRequest) -> str:
    box = ReverseTuckBox()
    geometry = box.generate(
        length=payload.length,
        width=payload.width,
        depth=payload.depth,
        glue_flap=payload.glue_flap,
        tuck_flap_depth=payload.tuck_flap_depth,
        dust_flap_depth=payload.dust_flap_depth,
    )
    header_lines = [
        "Reverse Tuck Box - Dieline",
        f"Length {payload.length}(MM) X Width {payload.width}(MM) X Depth {payload.depth}(MM)",
    ]
    return build_svg(
        blank_width=geometry["blank_width"],
        blank_height=geometry["blank_height"],
        cut_lines=geometry["cut_lines"],
        crease_lines=geometry["crease_lines"],
        labels=geometry["labels"],
        dimensions=geometry.get("dimensions"),
        header_lines=header_lines,
    )


@router.post("/reverse-tuck/svg")
def reverse_tuck_svg(payload: DielineRequest):
    """Returns SVG for direct browser preview - embeddable in an <img> tag."""
    svg_string = _generate_svg_string(payload)
    return Response(content=svg_string, media_type="image/svg+xml")


@router.post("/reverse-tuck/pdf")
def reverse_tuck_pdf(payload: DielineRequest):
    """Returns a print-ready PDF."""
    svg_string = _generate_svg_string(payload)
    pdf_bytes = svg_to_pdf(svg_string)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reverse_tuck_dieline.pdf"},
    )


@router.post("/reverse-tuck/png")
def reverse_tuck_png(payload: DielineRequest):
    """Returns a PNG image, useful for thumbnails."""
    svg_string = _generate_svg_string(payload)
    png_bytes = svg_to_png(svg_string)
    return Response(content=png_bytes, media_type="image/png")


def _run_nesting(payload: SheetLayoutRequest):
    box = ReverseTuckBox()
    geometry = box.generate(
        length=payload.length,
        width=payload.width,
        depth=payload.depth,
        glue_flap=payload.glue_flap,
        tuck_flap_depth=payload.tuck_flap_depth,
        dust_flap_depth=payload.dust_flap_depth,
    )
    sheet_w_mm = to_mm(payload.sheet_width, payload.unit)
    sheet_h_mm = to_mm(payload.sheet_height, payload.unit)

    nesting = calculate_nesting(
        sheet_width_mm=sheet_w_mm,
        sheet_height_mm=sheet_h_mm,
        blank_width=geometry["blank_width"],
        blank_height=geometry["blank_height"],
        margin_mm=payload.margin,
    )
    return geometry, nesting


@router.post("/reverse-tuck/sheet-layout/info")
def reverse_tuck_sheet_info(payload: SheetLayoutRequest):
    """Returns nesting stats only (box count, waste %, orientation) - no drawing."""
    _, nesting = _run_nesting(payload)
    return {
        "orientation": nesting["orientation"],
        "columns": nesting["columns"],
        "rows": nesting["rows"],
        "total_boxes": nesting["total_boxes"],
        "waste_percent": nesting["waste_percent"],
        "sheet_width_mm": nesting["sheet_width_mm"],
        "sheet_height_mm": nesting["sheet_height_mm"],
    }


def _build_sheet_header(payload: SheetLayoutRequest, nesting: dict) -> list:
    return [
        "Created By Dieline Service",
        f"Length {payload.length}(MM) X Width {payload.width}(MM) X Depth {payload.depth}(MM)",
        f"SHEET: {nesting['sheet_width_mm']}(MM) X {nesting['sheet_height_mm']}(MM) || "
        f"UPS: {nesting['columns']}x{nesting['rows']} - {nesting['total_boxes']} ups || "
        f"Waste: {nesting['waste_percent']}%",
    ]


@router.post("/reverse-tuck/sheet-layout/svg")
def reverse_tuck_sheet_svg(payload: SheetLayoutRequest):
    """Returns the full sheet dieline - every box tiled in a grid with cut/crease lines."""
    geometry, nesting = _run_nesting(payload)
    svg_string = build_sheet_svg(
        sheet_width_mm=nesting["sheet_width_mm"],
        sheet_height_mm=nesting["sheet_height_mm"],
        cut_lines=geometry["cut_lines"],
        crease_lines=geometry["crease_lines"],
        blank_width=geometry["blank_width"],
        blank_height=geometry["blank_height"],
        positions=nesting["positions"],
        orientation=nesting["orientation"],
        header_lines=_build_sheet_header(payload, nesting),
        dimensions=geometry.get("dimensions"),
    )
    return Response(content=svg_string, media_type="image/svg+xml")


@router.post("/reverse-tuck/sheet-layout/pdf")
def reverse_tuck_sheet_pdf(payload: SheetLayoutRequest):
    """Returns the full sheet layout as a print-ready PDF."""
    geometry, nesting = _run_nesting(payload)
    svg_string = build_sheet_svg(
        sheet_width_mm=nesting["sheet_width_mm"],
        sheet_height_mm=nesting["sheet_height_mm"],
        cut_lines=geometry["cut_lines"],
        crease_lines=geometry["crease_lines"],
        blank_width=geometry["blank_width"],
        blank_height=geometry["blank_height"],
        positions=nesting["positions"],
        orientation=nesting["orientation"],
        header_lines=_build_sheet_header(payload, nesting),
        dimensions=geometry.get("dimensions"),
    )
    pdf_bytes = svg_to_pdf(svg_string)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sheet_layout.pdf"},
    )
