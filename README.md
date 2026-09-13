# Dieline Generator Service

A Python/FastAPI microservice that generates print-ready **die line / key line** drawings for packaging boxes. Given a box's Length, Width, and Depth, it calculates the exact cut and crease geometry and returns it as SVG, PDF, or PNG.

Built to be consumed by a separate printing-press management system (originally a .NET application) over a simple HTTP API, so the packaging math and drawing logic stay decoupled from the main application.

## Features

- **Single box dieline generation** — Reverse Tuck box style, with cut lines (red) and crease lines (green) calculated from L/W/D input
- **Sheet nesting** — given a sheet size, calculates how many boxes fit (trying both normal and rotated orientations) and reports material waste %
- **Full sheet layout drawing** — tiles the box geometry across the sheet grid into a single print-ready file
- **Dimension annotations** — auto-generated measurement lines and a summary header block on every drawing
- **Configurable flap sizing** — glue flap / tuck flap / dust flap dimensions can be overridden per request to match a specific press's production specs

## Tech Stack

- **FastAPI** — REST API framework
- **Pydantic** — request validation
- **svgwrite** — SVG generation
- **cairosvg** — SVG → PDF/PNG conversion
- **pytest** — unit tests

## Project Structure

```
app/
  main.py                       FastAPI app entry point, CORS setup
  config.py                     Environment-based settings
  models/
    schemas.py                  Pydantic request models
  box_styles/
    base.py                     Abstract interface all box styles implement
    reverse_tuck.py             Reverse Tuck geometry + formulas
  services/
    geometry.py                 Shared geometry helpers
    svg_generator.py            Single-box SVG rendering
    sheet_svg_generator.py      Full-sheet layout rendering
    nesting.py                  Sheet nesting / fit calculation
    pdf_export.py               SVG → PDF/PNG conversion
  routers/
    dieline.py                  API endpoints
tests/
  test_reverse_tuck.py          Geometry/formula tests
  test_nesting.py               Nesting calculation tests
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running locally

```bash
uvicorn app.main:app --reload --port 8000
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## API Endpoints

### Single box

| Endpoint | Returns |
|---|---|
| `POST /api/dieline/reverse-tuck/svg` | SVG preview |
| `POST /api/dieline/reverse-tuck/pdf` | Print-ready PDF |
| `POST /api/dieline/reverse-tuck/png` | PNG image |

Request body:
```json
{
  "length": 70,
  "width": 40,
  "depth": 110
}
```

Optional overrides for production-specific flap sizing:
```json
{
  "length": 70,
  "width": 40,
  "depth": 110,
  "glue_flap": 15,
  "tuck_flap_depth": 30,
  "dust_flap_depth": 25
}
```

### Sheet layout / nesting

| Endpoint | Returns |
|---|---|
| `POST /api/dieline/reverse-tuck/sheet-layout/info` | JSON stats only (box count, waste %, orientation) |
| `POST /api/dieline/reverse-tuck/sheet-layout/svg` | Full sheet drawing, all boxes tiled |
| `POST /api/dieline/reverse-tuck/sheet-layout/pdf` | Full sheet layout as PDF |

Request body:
```json
{
  "length": 70,
  "width": 40,
  "depth": 110,
  "sheet_width": 25,
  "sheet_height": 36,
  "unit": "inch",
  "margin": 5
}
```

## Testing

```bash
pytest tests/ -v
```

## Quick test via curl

```bash
curl -X POST http://127.0.0.1:8000/api/dieline/reverse-tuck/svg \
  -H "Content-Type: application/json" \
  -d '{"length": 70, "width": 40, "depth": 110}' \
  --output test.svg
```

## Integration notes

Any HTTP client can call this service - the consuming application sends a POST request with box/sheet parameters and receives SVG/PDF/PNG bytes back in the response, which can be rendered directly or offered as a download.

## Known limitation: default flap sizing

The default `glue_flap`, `tuck_flap_depth`, and `dust_flap_depth` values in `reverse_tuck.py` are generic approximations, not measured from a real production sample. For production use, these should be replaced with actual values from the target printing press (measured from a physical sample box), either as fixed values or via the optional request fields shown above.

## Roadmap

- Additional box styles (Crush Lock, Snap Lock, Straight Tuck, etc.) following the same `box_styles/` pattern
- Nesting optimization beyond simple grid-fitting (mixed rotations, irregular packing)
- ML-assisted features: image-based box detection, design recommendations, defect detection
