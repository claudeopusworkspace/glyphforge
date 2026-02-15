"""Skeleton → filled outlines via pyclipper polygon offset."""

from __future__ import annotations

import math

import pyclipper

from .bezier import evaluate, flatten, normal, tangent
from .geometry import Point
from .glyph import (
    CubicBezier,
    Decoration,
    Outline,
    Skeleton,
    Stroke,
)
from .style import AlphabetStyle, CapStyle, JoinStyle, SerifStyle


# pyclipper works with integer coordinates — we scale to this space
CLIPPER_SCALE = 1000.0


def _to_clipper(points: list[Point]) -> list[tuple[int, int]]:
    return [(int(p.x * CLIPPER_SCALE), int(p.y * CLIPPER_SCALE))
            for p in points]


def _from_clipper(path: list[tuple[int, int]]) -> list[Point]:
    return [Point(x / CLIPPER_SCALE, y / CLIPPER_SCALE) for x, y in path]


def _collect_polytree(node, result: list[list[Point]]) -> None:
    """Recursively collect all contours from a pyclipper PolyTree.

    Both outer contours and hole contours are collected as separate
    polygons. When rendered with SVG fill-rule="evenodd", the holes
    will correctly subtract from the outers.
    """
    if node.Contour:
        result.append(_from_clipper(node.Contour))
    for child in node.Childs:
        _collect_polytree(child, result)


def _pyclipper_join(style: JoinStyle) -> int:
    return {
        JoinStyle.ROUND: pyclipper.JT_ROUND,
        JoinStyle.MITER: pyclipper.JT_MITER,
        JoinStyle.BEVEL: pyclipper.JT_SQUARE,
    }[style]


def _pyclipper_end(style: CapStyle) -> int:
    return {
        CapStyle.ROUND: pyclipper.ET_OPENROUND,
        CapStyle.FLAT: pyclipper.ET_OPENBUTT,
        CapStyle.TAPERED: pyclipper.ET_OPENBUTT,  # taper handled separately
    }[style]


class StrokeExpander:
    """Convert center-line skeletons into filled polygon outlines."""

    def __init__(self, style: AlphabetStyle):
        self._style = style

    def expand_skeleton(self, skeleton: Skeleton) -> Outline:
        """Expand all strokes and decorations into a single Outline."""
        all_polygons: list[list[Point]] = []

        for stroke in skeleton.strokes:
            polys = self._expand_stroke(stroke)
            all_polygons.extend(polys)

        for dec in skeleton.decorations:
            polys = self._expand_decoration(dec)
            all_polygons.extend(polys)

        # Union all polygons using pyclipper boolean ops
        if len(all_polygons) > 1:
            all_polygons = self._union_polygons(all_polygons)

        return Outline(polygons=all_polygons)

    def _expand_stroke(self, stroke: Stroke) -> list[list[Point]]:
        """Expand a single stroke into polygons via offset."""
        s = self._style

        # Flatten all segments to polyline
        polyline: list[Point] = []
        for i, seg in enumerate(stroke.segments):
            # Adaptive tolerance based on stroke width
            tol = max(0.01, s.stroke_width * 0.15)
            pts = flatten(seg, tolerance=tol)
            if i == 0:
                polyline.extend(pts)
            else:
                # Skip first point (duplicate of previous segment's last)
                polyline.extend(pts[1:])

        if len(polyline) < 2:
            return []

        # Apply taper if requested
        if s.stroke_taper > 0.01 and s.cap_style == CapStyle.TAPERED:
            return [self._build_tapered_outline(polyline)]

        # Simple offset expansion
        return self._offset_polyline(polyline)

    def _offset_polyline(self, polyline: list[Point]) -> list[list[Point]]:
        """Offset a polyline by stroke_width using pyclipper."""
        s = self._style
        offset_dist = s.stroke_width * CLIPPER_SCALE / 2.0

        pco = pyclipper.PyclipperOffset()
        clipper_path = _to_clipper(polyline)
        join = _pyclipper_join(s.join_style)
        end = _pyclipper_end(s.cap_style)

        try:
            pco.AddPath(clipper_path, join, end)
            result = pco.Execute(offset_dist)
        except pyclipper.ClipperException:
            # Fallback: build a simple rectangle around the polyline
            return [self._fallback_outline(polyline)]

        return [_from_clipper(path) for path in result]

    def _build_tapered_outline(self, polyline: list[Point]) -> list[Point]:
        """Build a tapered stroke outline by varying width along the path."""
        s = self._style
        n = len(polyline)
        if n < 2:
            return polyline

        # Compute cumulative arc lengths for parameterisation
        lengths = [0.0]
        for i in range(1, n):
            lengths.append(lengths[-1] + polyline[i - 1].distance_to(polyline[i]))
        total_len = lengths[-1]
        if total_len < 1e-12:
            return polyline

        left_side: list[Point] = []
        right_side: list[Point] = []

        for i in range(n):
            t = lengths[i] / total_len  # [0, 1] along stroke

            # Taper envelope: thick in middle, thin at ends
            taper = s.stroke_taper
            envelope = 1.0 - taper * (2 * abs(t - 0.5))
            width = s.stroke_width * max(0.15, envelope) / 2.0

            # Compute local normal
            if i == 0:
                direction = polyline[1] - polyline[0]
            elif i == n - 1:
                direction = polyline[-1] - polyline[-2]
            else:
                direction = polyline[i + 1] - polyline[i - 1]

            norm = Point(-direction.y, direction.x).normalized()

            left_side.append(polyline[i] + norm * width)
            right_side.append(polyline[i] - norm * width)

        # Build closed polygon: left side forward + right side backward
        right_side.reverse()
        return left_side + right_side

    def _expand_decoration(self, dec: Decoration) -> list[list[Point]]:
        """Expand a decoration into polygons."""
        s = self._style

        if dec.kind == "dot":
            return [self._make_circle(dec.position, dec.size)]
        elif dec.kind == "bar":
            return self._make_bar(dec)
        elif dec.kind == "serif":
            return self._make_serif(dec)
        elif dec.kind == "flourish":
            return self._make_flourish(dec)
        return []

    def _make_circle(self, center: Point, radius: float,
                      segments: int = 12) -> list[Point]:
        """Generate a circle polygon."""
        points: list[Point] = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            points.append(Point(
                center.x + radius * math.cos(angle),
                center.y + radius * math.sin(angle),
            ))
        return points

    def _make_bar(self, dec: Decoration) -> list[list[Point]]:
        """Generate a crossbar polygon."""
        s = self._style
        half_len = dec.size / 2
        half_w = s.stroke_width / 2
        ca, sa = math.cos(dec.angle), math.sin(dec.angle)

        corners = [
            Point(-half_len, -half_w),
            Point(half_len, -half_w),
            Point(half_len, half_w),
            Point(-half_len, half_w),
        ]
        rotated = [Point(p.x * ca - p.y * sa + dec.position.x,
                         p.x * sa + p.y * ca + dec.position.y)
                   for p in corners]
        return [rotated]

    def _make_serif(self, dec: Decoration) -> list[list[Point]]:
        """Generate a serif polygon based on style."""
        s = self._style
        sz = dec.size

        if s.serif_style == SerifStyle.SLAB:
            return self._make_bar(Decoration(
                "bar", dec.position, sz * 2, dec.angle))
        elif s.serif_style == SerifStyle.WEDGE:
            # Triangle
            p = dec.position
            return [[
                Point(p.x, p.y - sz * 0.3),
                Point(p.x + sz, p.y),
                Point(p.x - sz, p.y),
            ]]
        elif s.serif_style == SerifStyle.FLARE:
            # Wider circle
            return [self._make_circle(dec.position, sz * 1.2, 8)]
        return []

    def _make_flourish(self, dec: Decoration) -> list[list[Point]]:
        """Generate a small flourish curve as an outline."""
        # A tiny arc rendered as a thin polygon
        s = self._style
        p = dec.position
        sz = dec.size
        ca, sa = math.cos(dec.angle), math.sin(dec.angle)

        points: list[Point] = []
        steps = 8
        for i in range(steps + 1):
            t = i / steps
            # Spiral-like curve
            r = sz * (1 - t * 0.5)
            a = dec.angle + t * math.pi * 0.7
            points.append(Point(p.x + r * math.cos(a),
                                p.y + r * math.sin(a)))

        # Make it into a thin polygon
        if len(points) < 2:
            return []
        return self._offset_polyline_thin(points, s.stroke_width * 0.6)

    def _offset_polyline_thin(self, polyline: list[Point],
                               width: float) -> list[list[Point]]:
        """Simple offset for thin strokes."""
        pco = pyclipper.PyclipperOffset()
        clipper_path = _to_clipper(polyline)
        try:
            pco.AddPath(clipper_path, pyclipper.JT_ROUND,
                        pyclipper.ET_OPENROUND)
            result = pco.Execute(width * CLIPPER_SCALE / 2.0)
        except pyclipper.ClipperException:
            return []
        return [_from_clipper(path) for path in result]

    def _union_polygons(self, polygons: list[list[Point]]) -> list[list[Point]]:
        """Union all polygons using pyclipper boolean operations.

        Uses Execute2 (PolyTree) to preserve hole topology — when expanded
        strokes form enclosed regions (loops, diamonds), the interior holes
        are returned as separate polygons for evenodd SVG rendering.
        """
        pc = pyclipper.Pyclipper()

        # Add all polygons as subjects so pyclipper sees them as one
        # combined shape. Using PFT_EVENODD means the pre-existing winding
        # from offset (outer=CCW, hole=CW) is respected during union.
        for poly in polygons:
            cp = _to_clipper(poly)
            if len(cp) < 3:
                continue
            try:
                pc.AddPath(cp, pyclipper.PT_SUBJECT, True)
            except pyclipper.ClipperException:
                continue

        try:
            tree = pc.Execute2(pyclipper.CT_UNION,
                               pyclipper.PFT_EVENODD,
                               pyclipper.PFT_EVENODD)
        except pyclipper.ClipperException:
            return polygons  # fallback: return un-unioned

        # Walk the PolyTree and collect all contours (outers + holes)
        result: list[list[Point]] = []
        _collect_polytree(tree, result)
        return result if result else polygons

    def _fallback_outline(self, polyline: list[Point]) -> list[Point]:
        """Simple fallback: build parallel curves on each side."""
        s = self._style
        w = s.stroke_width / 2
        n = len(polyline)
        if n < 2:
            return polyline

        left: list[Point] = []
        right: list[Point] = []

        for i in range(n):
            if i == 0:
                d = polyline[1] - polyline[0]
            elif i == n - 1:
                d = polyline[-1] - polyline[-2]
            else:
                d = polyline[i + 1] - polyline[i - 1]
            norm = Point(-d.y, d.x).normalized()
            left.append(polyline[i] + norm * w)
            right.append(polyline[i] - norm * w)

        right.reverse()
        return left + right
