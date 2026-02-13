"""Tests for bezier curve math."""

from glyphforge.bezier import (
    evaluate,
    flatten,
    make_arc,
    make_line,
    make_s_curve,
    normal,
    split,
    tangent,
)
from glyphforge.geometry import Point
from glyphforge.glyph import CubicBezier


def _approx(a: Point, b: Point, tol: float = 1e-6) -> bool:
    return abs(a.x - b.x) < tol and abs(a.y - b.y) < tol


def test_evaluate_endpoints():
    """Evaluating at t=0 and t=1 should return start and end."""
    bez = CubicBezier(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    assert _approx(evaluate(bez, 0.0), bez.p0)
    assert _approx(evaluate(bez, 1.0), bez.p3)


def test_evaluate_midpoint_line():
    """Midpoint of a straight-line bezier should be geometric midpoint."""
    bez = make_line(Point(0, 0), Point(4, 0))
    mid = evaluate(bez, 0.5)
    assert _approx(mid, Point(2, 0), tol=1e-4)


def test_split_continuity():
    """Split should produce two curves that connect at split point."""
    bez = CubicBezier(Point(0, 0), Point(1, 3), Point(3, 3), Point(4, 0))
    left, right = split(bez, 0.5)
    # Left end == split point == right start
    assert _approx(left.p3, right.p0)
    # Left start == original start
    assert _approx(left.p0, bez.p0)
    # Right end == original end
    assert _approx(right.p3, bez.p3)


def test_split_preserves_curve():
    """Evaluating the two halves should match the original curve."""
    bez = CubicBezier(Point(0, 0), Point(1, 3), Point(3, 3), Point(4, 0))
    left, right = split(bez, 0.3)

    # Points on left half (t in [0, 0.3] of original)
    for t in [0.0, 0.1, 0.2, 0.3]:
        orig = evaluate(bez, t)
        remapped = evaluate(left, t / 0.3)
        assert _approx(orig, remapped, tol=1e-4)


def test_tangent_direction():
    """Tangent of horizontal line should point right."""
    bez = make_line(Point(0, 0), Point(4, 0))
    tan = tangent(bez, 0.5)
    assert tan.x > 0
    assert abs(tan.y) < 1e-6


def test_normal_perpendicular():
    """Normal should be perpendicular to tangent."""
    bez = CubicBezier(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    for t in [0.2, 0.5, 0.8]:
        tan = tangent(bez, t)
        norm = normal(bez, t)
        dot = tan.x * norm.x + tan.y * norm.y
        assert abs(dot) < 0.01  # approximately perpendicular


def test_flatten_includes_endpoints():
    """Flattened polyline should start and end at bezier endpoints."""
    bez = CubicBezier(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    pts = flatten(bez, tolerance=0.1)
    assert len(pts) >= 2
    assert _approx(pts[0], bez.p0)
    assert _approx(pts[-1], bez.p3)


def test_flatten_straight_line():
    """Flattening a straight line should produce few points."""
    bez = make_line(Point(0, 0), Point(10, 0))
    pts = flatten(bez, tolerance=0.5)
    # A straight line needs only 2 points
    assert len(pts) == 2


def test_make_arc():
    """Arc with positive bulge should deviate from chord."""
    arc = make_arc(Point(0, 0), Point(4, 0), 0.5)
    mid = evaluate(arc, 0.5)
    # Should be above the chord (negative y in screen coords or positive
    # depending on direction — just check it deviates)
    assert abs(mid.y) > 0.1


def test_make_s_curve():
    """S-curve midpoint should be near chord midpoint (inflection)."""
    sc = make_s_curve(Point(0, 0), Point(4, 0), 0.5)
    mid = evaluate(sc, 0.5)
    # Near the chord midpoint
    assert abs(mid.x - 2.0) < 0.5
