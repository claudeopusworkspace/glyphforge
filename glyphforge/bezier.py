"""Cubic bezier math — evaluate, split, tangent, normal, flatten."""

from __future__ import annotations

import math

from .geometry import Point
from .glyph import CubicBezier


def evaluate(bez: CubicBezier, t: float) -> Point:
    """Evaluate cubic bezier at parameter t ∈ [0, 1]."""
    u = 1.0 - t
    return (u * u * u * bez.p0 +
            3 * u * u * t * bez.p1 +
            3 * u * t * t * bez.p2 +
            t * t * t * bez.p3)


def tangent(bez: CubicBezier, t: float) -> Point:
    """First derivative at parameter t (unnormalised tangent vector)."""
    u = 1.0 - t
    return (3 * u * u * (bez.p1 - bez.p0) +
            6 * u * t * (bez.p2 - bez.p1) +
            3 * t * t * (bez.p3 - bez.p2))


def normal(bez: CubicBezier, t: float) -> Point:
    """Unit normal (perpendicular to tangent, left-hand side)."""
    tan = tangent(bez, t)
    perp = Point(-tan.y, tan.x)
    ln = perp.length()
    if ln < 1e-12:
        return Point(0.0, 1.0)
    return Point(perp.x / ln, perp.y / ln)


def split(bez: CubicBezier, t: float) -> tuple[CubicBezier, CubicBezier]:
    """Split bezier at t using De Casteljau's algorithm."""
    p01 = bez.p0.lerp(bez.p1, t)
    p12 = bez.p1.lerp(bez.p2, t)
    p23 = bez.p2.lerp(bez.p3, t)
    p012 = p01.lerp(p12, t)
    p123 = p12.lerp(p23, t)
    p0123 = p012.lerp(p123, t)

    left = CubicBezier(bez.p0, p01, p012, p0123)
    right = CubicBezier(p0123, p123, p23, bez.p3)
    return left, right


def flatten(bez: CubicBezier, tolerance: float = 0.5) -> list[Point]:
    """Approximate bezier as a polyline within pixel tolerance.

    Uses recursive subdivision — flatness test based on max deviation
    of control points from the chord.
    """
    result: list[Point] = [bez.p0]
    _flatten_recursive(bez, tolerance, result)
    return result


def _flatness(bez: CubicBezier) -> float:
    """Max distance of control points from the chord P0→P3."""
    chord = bez.p3 - bez.p0
    chord_len = chord.length()
    if chord_len < 1e-12:
        return max((bez.p1 - bez.p0).length(), (bez.p2 - bez.p0).length())
    nx, ny = -chord.y / chord_len, chord.x / chord_len
    d1 = abs((bez.p1.x - bez.p0.x) * nx + (bez.p1.y - bez.p0.y) * ny)
    d2 = abs((bez.p2.x - bez.p0.x) * nx + (bez.p2.y - bez.p0.y) * ny)
    return max(d1, d2)


def _flatten_recursive(bez: CubicBezier, tolerance: float,
                        result: list[Point]) -> None:
    if _flatness(bez) <= tolerance:
        result.append(bez.p3)
        return
    left, right = split(bez, 0.5)
    _flatten_recursive(left, tolerance, result)
    _flatten_recursive(right, tolerance, result)


def arc_length(bez: CubicBezier, steps: int = 32) -> float:
    """Approximate arc length by evaluating at uniform t steps."""
    total = 0.0
    prev = bez.p0
    for i in range(1, steps + 1):
        t = i / steps
        cur = evaluate(bez, t)
        total += prev.distance_to(cur)
        prev = cur
    return total


def make_line(p0: Point, p1: Point) -> CubicBezier:
    """Create a straight-line bezier from p0 to p1."""
    return CubicBezier(p0, p0.lerp(p1, 1 / 3), p0.lerp(p1, 2 / 3), p1)


def make_arc(start: Point, end: Point, bulge: float) -> CubicBezier:
    """Create an arc-like bezier from start to end.

    bulge > 0: curve bows left (relative to start→end direction)
    bulge < 0: curve bows right
    bulge = 0: straight line
    """
    mid = start.lerp(end, 0.5)
    chord = end - start
    perp = Point(-chord.y, chord.x)
    offset = perp * bulge

    # Control points at roughly 1/3 and 2/3 along the chord,
    # offset perpendicular to the chord
    cp1 = start.lerp(end, 1 / 3) + offset * 0.8
    cp2 = start.lerp(end, 2 / 3) + offset * 0.8
    return CubicBezier(start, cp1, cp2, end)


def make_s_curve(start: Point, end: Point, amplitude: float) -> CubicBezier:
    """S-curve: control points offset in opposite directions."""
    chord = end - start
    perp = Point(-chord.y, chord.x)
    cp1 = start.lerp(end, 1 / 3) + perp * amplitude
    cp2 = start.lerp(end, 2 / 3) - perp * amplitude
    return CubicBezier(start, cp1, cp2, end)
