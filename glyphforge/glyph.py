"""Glyph, Skeleton, Stroke, CubicBezier data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .geometry import BoundingBox, Point


@dataclass(frozen=True, slots=True)
class CubicBezier:
    """A single cubic bezier segment: P0 → P1 → P2 → P3."""
    p0: Point
    p1: Point
    p2: Point
    p3: Point


@dataclass(slots=True)
class Stroke:
    """A sequence of connected cubic bezier segments forming one pen-stroke."""
    segments: list[CubicBezier] = field(default_factory=list)

    @property
    def start(self) -> Point:
        return self.segments[0].p0

    @property
    def end(self) -> Point:
        return self.segments[-1].p3

    @property
    def points(self) -> list[Point]:
        """All unique endpoints and control points."""
        pts: list[Point] = []
        for seg in self.segments:
            pts.extend([seg.p0, seg.p1, seg.p2, seg.p3])
        return pts


@dataclass(slots=True)
class Decoration:
    """An additional decorative element (dot, bar, flourish)."""
    kind: str          # "dot", "bar", "serif", "flourish"
    position: Point    # centre position
    size: float = 0.04
    angle: float = 0.0  # rotation in radians
    points: list[Point] = field(default_factory=list)  # optional shape


@dataclass(slots=True)
class Skeleton:
    """Centre-line representation of a glyph before stroke expansion."""
    strokes: list[Stroke] = field(default_factory=list)
    decorations: list[Decoration] = field(default_factory=list)
    template_name: str = ""

    @property
    def bounds(self) -> BoundingBox:
        all_pts: list[Point] = []
        for stroke in self.strokes:
            all_pts.extend(stroke.points)
        for dec in self.decorations:
            all_pts.append(dec.position)
        if not all_pts:
            return BoundingBox(0, 0, 0, 0)
        return BoundingBox.from_points(all_pts)


@dataclass(slots=True)
class Outline:
    """Filled outline of a glyph — polygons ready for SVG rendering."""
    # Each polygon is a list of points (closed path, CW=filled, CCW=hole)
    polygons: list[list[Point]] = field(default_factory=list)

    @property
    def bounds(self) -> BoundingBox:
        all_pts = [p for poly in self.polygons for p in poly]
        if not all_pts:
            return BoundingBox(0, 0, 0, 0)
        return BoundingBox.from_points(all_pts)


@dataclass(slots=True)
class Glyph:
    """A single glyph: label + skeleton + expanded outline."""
    label: str            # A-Z
    index: int            # 0-25
    skeleton: Skeleton
    outline: Outline
    template_name: str = ""

    @property
    def bounds(self) -> BoundingBox:
        return self.outline.bounds
