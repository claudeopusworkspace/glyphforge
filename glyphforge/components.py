"""Shared stroke primitives library (radicals).

Generates a set of reusable sub-stroke components from the style,
which can be mixed into glyphs to create visual coherence — like how
CJK scripts share radicals across characters.
"""

from __future__ import annotations

from dataclasses import dataclass

from .bezier import make_arc, make_line, make_s_curve
from .geometry import Point
from .glyph import CubicBezier, Stroke
from .rng import SeededRNG
from .style import AlphabetStyle


@dataclass
class Component:
    """A named reusable stroke primitive."""
    name: str
    stroke: Stroke


class ComponentLibrary:
    """Generate and cache shared stroke primitives from a style."""

    def __init__(self, rng: SeededRNG, style: AlphabetStyle):
        self._rng = rng.fork("components")
        self._style = style
        self._components: list[Component] = []
        self._build()

    def _build(self) -> None:
        r = self._rng
        s = self._style

        # Number of components scales with component_reuse
        count = max(6, int(8 + s.component_reuse * 10))

        builders = [
            self._make_tick,
            self._make_hook,
            self._make_arc_segment,
            self._make_crossbar,
            self._make_descender,
            self._make_ascender,
            self._make_curve_connector,
            self._make_dot_stroke,
        ]

        for i in range(count):
            cr = r.fork(f"comp_{i}")
            builder = builders[i % len(builders)]
            comp = builder(cr)
            self._components.append(Component(f"comp_{i}", comp))

    def get(self, index: int) -> Component:
        return self._components[index % len(self._components)]

    def random_component(self, rng: SeededRNG) -> Component:
        return rng.choice(self._components)

    @property
    def components(self) -> list[Component]:
        return list(self._components)

    # -- Builders ---------------------------------------------------------

    def _make_tick(self, rng: SeededRNG) -> Stroke:
        length = rng.uniform(0.1, 0.25)
        angle = rng.uniform(-0.5, 0.5)
        p0 = Point(0, 0)
        p1 = Point(length * 0.3 + angle * 0.1, length)
        return Stroke([make_line(p0, p1)])

    def _make_hook(self, rng: SeededRNG) -> Stroke:
        bulge = rng.uniform(0.15, 0.4) * (1 if rng.coin() else -1)
        p0 = Point(0, 0)
        p1 = Point(0, 0.3)
        p2 = Point(0.15, 0.4)
        return Stroke([make_arc(p0, p1, bulge * 0.3), make_arc(p1, p2, bulge)])

    def _make_arc_segment(self, rng: SeededRNG) -> Stroke:
        bulge = rng.uniform(0.2, 0.5) * (1 if rng.coin() else -1)
        p0 = Point(0, 0)
        p1 = Point(rng.uniform(0.15, 0.3), rng.uniform(0.2, 0.4))
        return Stroke([make_arc(p0, p1, bulge)])

    def _make_crossbar(self, rng: SeededRNG) -> Stroke:
        w = rng.uniform(0.2, 0.5)
        slight_curve = rng.uniform(-0.05, 0.05)
        p0 = Point(0, 0)
        p1 = Point(w, slight_curve)
        return Stroke([make_arc(p0, p1, slight_curve)])

    def _make_descender(self, rng: SeededRNG) -> Stroke:
        depth = rng.uniform(0.15, 0.3)
        bulge = rng.uniform(-0.2, 0.2)
        p0 = Point(0, 0)
        p1 = Point(rng.uniform(-0.05, 0.1), depth)
        return Stroke([make_arc(p0, p1, bulge)])

    def _make_ascender(self, rng: SeededRNG) -> Stroke:
        height = rng.uniform(0.15, 0.3)
        bulge = rng.uniform(-0.2, 0.2)
        p0 = Point(0, 0)
        p1 = Point(rng.uniform(-0.05, 0.1), -height)
        return Stroke([make_arc(p0, p1, bulge)])

    def _make_curve_connector(self, rng: SeededRNG) -> Stroke:
        amp = rng.uniform(0.05, 0.15)
        p0 = Point(0, 0)
        p1 = Point(0.25, 0.25)
        return Stroke([make_s_curve(p0, p1, amp)])

    def _make_dot_stroke(self, rng: SeededRNG) -> Stroke:
        """A tiny stroke that reads as a dot at normal scale."""
        size = rng.uniform(0.02, 0.05)
        p0 = Point(0, 0)
        p1 = Point(size, size * 0.5)
        return Stroke([make_arc(p0, p1, 0.3)])
