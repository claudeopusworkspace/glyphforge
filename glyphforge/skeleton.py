"""Skeleton generation — fill templates with bezier curves shaped by style."""

from __future__ import annotations

import math

from .bezier import make_arc, make_line, make_s_curve
from .components import ComponentLibrary
from .geometry import Point
from .glyph import CubicBezier, Decoration, Skeleton, Stroke
from .rng import SeededRNG
from .style import AlphabetStyle
from .templates import (
    TEMPLATES,
    AnchorPoint,
    DecorationSpec,
    StrokeSpec,
    TemplateSpec,
    select_templates,
)


class SkeletonGenerator:
    """Generate 26 glyph skeletons from templates + style."""

    def __init__(self, rng: SeededRNG, style: AlphabetStyle,
                 components: ComponentLibrary):
        self._rng = rng.fork("skeleton")
        self._style = style
        self._components = components

    def generate_all(self) -> list[Skeleton]:
        """Generate 26 skeletons, one per glyph."""
        template_names = select_templates(self._rng)
        skeletons: list[Skeleton] = []

        for i, tname in enumerate(template_names):
            glyph_rng = self._rng.fork(f"glyph_{i:02d}")
            skeleton = self._generate_one(tname, glyph_rng)
            skeleton.template_name = tname.split("_v")[0]  # strip variant suffix
            skeletons.append(skeleton)

        return skeletons

    def _generate_one(self, template_name: str, rng: SeededRNG) -> Skeleton:
        """Generate a single glyph skeleton from a template."""
        # Resolve template (strip variant suffix for lookup)
        base_name = template_name.split("_v")[0]
        if base_name not in TEMPLATES:
            base_name = template_name
        template_func = TEMPLATES[base_name]

        # Generate template spec
        spec: TemplateSpec = template_func(rng, self._style)

        # Convert to skeleton
        strokes = [self._spec_to_stroke(ss, rng) for ss in spec.strokes]
        decorations = [self._spec_to_decoration(ds, rng) for ds in spec.decorations]

        # Maybe add style-driven decorations
        self._add_style_decorations(strokes, decorations, rng)

        # Optionally inject a shared component
        if rng.coin(self._style.component_reuse) and strokes:
            comp = self._components.random_component(rng)
            comp_stroke = self._place_component(comp.stroke, strokes, rng)
            strokes.append(comp_stroke)

        return Skeleton(strokes=strokes, decorations=decorations)

    def _spec_to_stroke(self, spec: StrokeSpec, rng: SeededRNG) -> Stroke:
        """Convert a StrokeSpec (anchor points) to a Stroke (bezier curves)."""
        s = self._style
        anchors = spec.anchors

        # Apply jitter to anchor positions
        jittered: list[Point] = []
        for ap in anchors:
            jx = ap.x + rng.gauss(0, s.anchor_jitter)
            jy = ap.y + rng.gauss(0, s.anchor_jitter)
            # Clamp to [0, 1]
            jx = max(0.0, min(1.0, jx))
            jy = max(0.0, min(1.0, jy))
            jittered.append(Point(jx, jy))

        # Scale to glyph metrics
        scaled = self._scale_to_metrics(jittered)

        # Build bezier segments between consecutive anchor points
        segments: list[CubicBezier] = []
        for j in range(len(scaled) - 1):
            p0 = scaled[j]
            p1 = scaled[j + 1]
            bulge = anchors[j].bulge

            # Modulate bulge by curvature_bias
            effective_bulge = bulge * (0.3 + 0.7 * s.curvature_bias)

            # Add control point jitter
            cp_jitter = s.control_point_jitter

            if abs(effective_bulge) < 0.01:
                # Nearly straight — add slight curvature based on style
                slight = rng.gauss(0, cp_jitter * 0.5) * s.curvature_bias
                seg = make_arc(p0, p1, slight)
            elif s.curvature_bias > 0.5 and rng.coin(s.inflection_frequency * 0.3):
                # S-curve variant
                seg = make_s_curve(p0, p1, effective_bulge * 0.7)
            else:
                seg = make_arc(p0, p1, effective_bulge)

            # Apply control point jitter
            seg = self._jitter_control_points(seg, cp_jitter, rng)
            segments.append(seg)

        return Stroke(segments=segments)

    def _scale_to_metrics(self, points: list[Point]) -> list[Point]:
        """Scale normalised [0,1]² points to glyph metric space."""
        s = self._style
        w = s.glyph_width
        # Total height = cap_height + descender_depth
        h = s.cap_height + s.descender_depth
        # Baseline is at descender_depth from bottom
        y_offset = s.descender_depth

        scaled: list[Point] = []
        for p in points:
            sx = p.x * w
            sy = p.y * h  # 0 = top of cap, 1 = bottom of descender
            scaled.append(Point(sx, sy))
        return scaled

    def _jitter_control_points(self, seg: CubicBezier, amount: float,
                                rng: SeededRNG) -> CubicBezier:
        """Add random noise to control points (not endpoints)."""
        jx1 = rng.gauss(0, amount)
        jy1 = rng.gauss(0, amount)
        jx2 = rng.gauss(0, amount)
        jy2 = rng.gauss(0, amount)
        return CubicBezier(
            seg.p0,
            Point(seg.p1.x + jx1, seg.p1.y + jy1),
            Point(seg.p2.x + jx2, seg.p2.y + jy2),
            seg.p3,
        )

    def _spec_to_decoration(self, ds: DecorationSpec,
                             rng: SeededRNG) -> Decoration:
        """Convert a DecorationSpec to a Decoration."""
        s = self._style
        # Scale position
        pos = Point(ds.x * s.glyph_width,
                     ds.y * (s.cap_height + s.descender_depth))
        size = s.stroke_width * ds.size * 1.5
        return Decoration(
            kind=ds.kind,
            position=pos,
            size=size,
            angle=ds.angle + rng.gauss(0, 0.1),
        )

    def _add_style_decorations(self, strokes: list[Stroke],
                                decorations: list[Decoration],
                                rng: SeededRNG) -> None:
        """Add decorative elements based on style probabilities."""
        s = self._style

        if not strokes:
            return

        # Dots
        if rng.coin(s.dot_frequency):
            # Place dot near a random stroke endpoint
            stroke = rng.choice(strokes)
            ref = rng.choice([stroke.start, stroke.end])
            offset = Point(rng.gauss(0, 0.03), rng.gauss(0, 0.03))
            decorations.append(Decoration(
                kind="dot",
                position=ref + offset + Point(0, -s.stroke_width * 2),
                size=s.stroke_width * 1.2,
            ))

        # Bars (crossbars)
        if rng.coin(s.bar_frequency):
            stroke = rng.choice(strokes)
            mid = stroke.start.lerp(stroke.end, 0.5)
            bar_width = s.glyph_width * rng.uniform(0.15, 0.35)
            decorations.append(Decoration(
                kind="bar",
                position=mid,
                size=bar_width,
                angle=s.stroke_angle,
            ))

        # Serifs
        if s.serif_style.value != "none":
            for stroke in strokes:
                for endpoint in [stroke.start, stroke.end]:
                    if rng.coin(0.6):  # not every endpoint
                        decorations.append(Decoration(
                            kind="serif",
                            position=endpoint,
                            size=s.serif_size,
                            angle=rng.uniform(-0.2, 0.2),
                        ))

        # Flourishes
        if rng.coin(s.flourish_probability):
            stroke = rng.choice(strokes)
            decorations.append(Decoration(
                kind="flourish",
                position=stroke.end,
                size=s.stroke_width * 3,
                angle=rng.uniform(0, math.pi),
            ))

    def _place_component(self, comp_stroke: Stroke,
                          existing: list[Stroke],
                          rng: SeededRNG) -> Stroke:
        """Place a component relative to an existing stroke."""
        ref = rng.choice(existing)
        anchor = rng.choice([ref.start, ref.end])

        # Translate component to anchor point
        comp_origin = comp_stroke.start
        dx = anchor.x - comp_origin.x
        dy = anchor.y - comp_origin.y

        new_segments: list[CubicBezier] = []
        for seg in comp_stroke.segments:
            new_segments.append(CubicBezier(
                Point(seg.p0.x + dx, seg.p0.y + dy),
                Point(seg.p1.x + dx, seg.p1.y + dy),
                Point(seg.p2.x + dx, seg.p2.y + dy),
                Point(seg.p3.x + dx, seg.p3.y + dy),
            ))
        return Stroke(segments=new_segments)
