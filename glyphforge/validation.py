"""Glyph validation — ink coverage, complexity bounds, distinctiveness."""

from __future__ import annotations

import math

from .geometry import BoundingBox, Point
from .glyph import Glyph, Outline


# -- Ink coverage estimation ------------------------------------------------

def estimate_ink_coverage(outline: Outline, bbox: BoundingBox) -> float:
    """Estimate fraction of bounding box filled with ink.

    Uses polygon area (shoelace formula) divided by bbox area.
    """
    if bbox.area < 1e-12:
        return 0.0

    total_area = 0.0
    for poly in outline.polygons:
        total_area += abs(_polygon_area(poly))

    return min(1.0, total_area / bbox.area)


def _polygon_area(points: list[Point]) -> float:
    """Signed area via shoelace formula."""
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    return area / 2.0


# -- Feature vector for distinctiveness ------------------------------------

def glyph_feature_vector(glyph: Glyph) -> list[float]:
    """Extract a feature vector for comparing glyph similarity.

    Features:
    - Bounding box aspect ratio
    - Number of polygons (proxy for connected components)
    - Ink coverage
    - Centroid position (normalised)
    - Stroke count from skeleton
    - Horizontal/vertical extent ratios
    """
    outline = glyph.outline
    bb = outline.bounds

    if bb.area < 1e-12:
        return [0.0] * 8

    ink = estimate_ink_coverage(outline, bb)
    aspect = bb.width / max(bb.height, 1e-12)
    n_polys = len(outline.polygons)

    # Centroid of all polygon points
    all_pts = [p for poly in outline.polygons for p in poly]
    if all_pts:
        cx = sum(p.x for p in all_pts) / len(all_pts)
        cy = sum(p.y for p in all_pts) / len(all_pts)
        # Normalise to [0, 1] within bbox
        cx_norm = (cx - bb.x_min) / max(bb.width, 1e-12)
        cy_norm = (cy - bb.y_min) / max(bb.height, 1e-12)
    else:
        cx_norm = cy_norm = 0.5

    n_strokes = len(glyph.skeleton.strokes)
    n_decorations = len(glyph.skeleton.decorations)

    return [ink, aspect, float(n_polys), cx_norm, cy_norm,
            float(n_strokes), float(n_decorations),
            float(len(glyph.skeleton.strokes))]


def feature_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between feature vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# -- Validation checks -----------------------------------------------------

MIN_INK_COVERAGE = 0.05
MAX_INK_COVERAGE = 0.85
MAX_CONNECTED_COMPONENTS = 8
MIN_DISTINCTIVENESS = 0.15


class ValidationResult:
    def __init__(self):
        self.passed = True
        self.issues: list[str] = []

    def fail(self, msg: str):
        self.passed = False
        self.issues.append(msg)


def validate_glyph(glyph: Glyph, reference_bbox: BoundingBox) -> ValidationResult:
    """Validate a single glyph against quality constraints."""
    result = ValidationResult()
    outline = glyph.outline

    # Ink coverage
    ink = estimate_ink_coverage(outline, reference_bbox)
    if ink < MIN_INK_COVERAGE:
        result.fail(f"Ink coverage too low: {ink:.2%} < {MIN_INK_COVERAGE:.0%}")
    if ink > MAX_INK_COVERAGE:
        result.fail(f"Ink coverage too high: {ink:.2%} > {MAX_INK_COVERAGE:.0%}")

    # Connected components
    n_components = len(outline.polygons)
    if n_components > MAX_CONNECTED_COMPONENTS:
        result.fail(f"Too many components: {n_components} > {MAX_CONNECTED_COMPONENTS}")

    # Non-empty
    if not outline.polygons:
        result.fail("Glyph has no outline polygons")

    return result


def check_distinctiveness(glyphs: list[Glyph]) -> list[tuple[int, int, float]]:
    """Find pairs of glyphs that are too similar.

    Returns list of (index_a, index_b, distance) for similar pairs.
    """
    vectors = [glyph_feature_vector(g) for g in glyphs]
    similar: list[tuple[int, int, float]] = []

    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            d = feature_distance(vectors[i], vectors[j])
            if d < MIN_DISTINCTIVENESS:
                similar.append((i, j, d))

    return similar
