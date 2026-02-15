"""SVG output — individual glyph files and specimen sheet grid."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import svgwrite

from .geometry import BoundingBox, Point
from .glyph import Glyph, Outline

if TYPE_CHECKING:
    from .alphabet import Alphabet


# -- Configuration --------------------------------------------------------

GLYPH_CELL_SIZE = 100       # px per glyph cell in specimen sheet
GLYPH_PADDING = 10          # px padding inside cell
SHEET_COLUMNS = 6           # glyphs per row in specimen sheet
LABEL_FONT_SIZE = 12
INDIVIDUAL_SIZE = 200        # px for individual glyph SVGs


# -- Coordinate mapping ---------------------------------------------------

def _map_outline_to_viewbox(outline: Outline, target_bbox: BoundingBox,
                              margin: float = 0.05) -> list[list[tuple[float, float]]]:
    """Map outline polygons into a target viewbox with margin."""
    src = outline.bounds
    if src.width < 1e-12 or src.height < 1e-12:
        return []

    # Fit outline into target box preserving aspect ratio
    tw = target_bbox.width * (1 - 2 * margin)
    th = target_bbox.height * (1 - 2 * margin)
    scale = min(tw / src.width, th / src.height)

    # Centre in target box
    ox = target_bbox.x_min + target_bbox.width * margin + (tw - src.width * scale) / 2
    oy = target_bbox.y_min + target_bbox.height * margin + (th - src.height * scale) / 2

    result: list[list[tuple[float, float]]] = []
    for poly in outline.polygons:
        mapped = [((p.x - src.x_min) * scale + ox,
                    (p.y - src.y_min) * scale + oy)
                   for p in poly]
        result.append(mapped)
    return result


def _compound_path_d(polygon_lists: list[list[tuple[float, float]]]) -> str:
    """Build an SVG path 'd' attribute from multiple polygons.

    Each polygon becomes a closed subpath. Used with fill-rule="evenodd"
    so that enclosed regions (holes inside loops/diamonds) are hollow.
    """
    parts: list[str] = []
    for poly in polygon_lists:
        if len(poly) < 3:
            continue
        x0, y0 = poly[0]
        segments = [f"M{x0:.2f},{y0:.2f}"]
        for x, y in poly[1:]:
            segments.append(f"L{x:.2f},{y:.2f}")
        segments.append("Z")
        parts.append("".join(segments))
    return "".join(parts)


def _add_glyph_to_drawing(dwg, polygon_lists: list[list[tuple[float, float]]]) -> None:
    """Add a glyph as a single compound path with nonzero fill rule.

    Winding directions are normalised during expansion (outers=CCW,
    holes=CW), so nonzero fill correctly renders overlapping strokes
    as solid while still cutting out interior holes.
    """
    d = _compound_path_d(polygon_lists)
    if d:
        dwg.add(dwg.path(d=d, fill="black", stroke="none",
                         fill_rule="nonzero"))


# -- Individual glyph SVG ------------------------------------------------

def glyph_to_svg(glyph: Glyph, size: int = INDIVIDUAL_SIZE) -> str:
    """Render a single glyph to an SVG string."""
    dwg = svgwrite.Drawing(size=(f"{size}px", f"{size}px"),
                            viewBox=f"0 0 {size} {size}")
    dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill="white"))

    target = BoundingBox(0, 0, size, size)
    paths = _map_outline_to_viewbox(glyph.outline, target, margin=0.1)
    _add_glyph_to_drawing(dwg, paths)

    return dwg.tostring()


def export_individual(alphabet: Alphabet, output_dir: str) -> list[str]:
    """Export individual SVG files for each glyph. Returns file paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    for glyph in alphabet:
        filename = f"glyph_{glyph.label.lower()}.svg"
        filepath = os.path.join(output_dir, filename)
        svg_content = glyph_to_svg(glyph)

        with open(filepath, "w") as f:
            f.write(svg_content)
        paths.append(filepath)

    return paths


# -- Specimen sheet -------------------------------------------------------

def export_sheet(alphabet: Alphabet, path: str) -> str:
    """Export a specimen sheet with all 26 glyphs in a grid."""
    cols = SHEET_COLUMNS
    rows = (len(alphabet) + cols - 1) // cols
    cell = GLYPH_CELL_SIZE
    pad = GLYPH_PADDING
    label_h = LABEL_FONT_SIZE + 4

    total_w = cols * cell
    total_h = rows * (cell + label_h) + 40  # 40 for title

    dwg = svgwrite.Drawing(path, size=(f"{total_w}px", f"{total_h}px"),
                            viewBox=f"0 0 {total_w} {total_h}")
    dwg.add(dwg.rect(insert=(0, 0), size=(total_w, total_h), fill="white"))

    # Title
    dwg.add(dwg.text(f"Seed: {alphabet.seed}", insert=(10, 20),
                      font_size="14px", font_family="monospace", fill="#666"))
    if alphabet.preset_name:
        dwg.add(dwg.text(f"Preset: {alphabet.preset_name}", insert=(10, 36),
                          font_size="12px", font_family="monospace", fill="#999"))

    y_offset = 40

    for i, glyph in enumerate(alphabet):
        col = i % cols
        row = i // cols
        x0 = col * cell
        y0 = y_offset + row * (cell + label_h)

        # Cell border
        dwg.add(dwg.rect(insert=(x0, y0), size=(cell, cell),
                          fill="none", stroke="#eee", stroke_width=0.5))

        # Glyph
        target = BoundingBox(x0 + pad, y0 + pad,
                              x0 + cell - pad, y0 + cell - pad)
        paths = _map_outline_to_viewbox(glyph.outline, target, margin=0.05)
        _add_glyph_to_drawing(dwg, paths)

        # Label
        dwg.add(dwg.text(glyph.label, insert=(x0 + cell / 2, y0 + cell + label_h - 2),
                          text_anchor="middle", font_size=f"{LABEL_FONT_SIZE}px",
                          font_family="monospace", fill="#888"))

    dwg.save()
    return path


def glyphs_to_inline_svgs(alphabet: Alphabet,
                            size: int = GLYPH_CELL_SIZE) -> list[str]:
    """Return list of inline SVG strings for each glyph."""
    return [glyph_to_svg(glyph, size) for glyph in alphabet]
