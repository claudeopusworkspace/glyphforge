"""30+ structural templates — topological blueprints for glyphs.

Each template is a function that returns abstract stroke descriptions
(anchor points in normalised [0,1]² space) which the skeleton generator
fills with bezier curves shaped by the current style.

A template function signature:
    def template_name(rng, style) -> list[StrokeSpec]

StrokeSpec = list of (x, y, bulge) tuples describing a path through
anchor points. bulge controls curvature between consecutive points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .rng import SeededRNG
from .style import AlphabetStyle


@dataclass
class AnchorPoint:
    """A point in normalised glyph space with curvature hint."""
    x: float
    y: float
    bulge: float = 0.0  # curvature to *next* point


@dataclass
class StrokeSpec:
    """Abstract stroke specification — ordered anchor points."""
    anchors: list[AnchorPoint] = field(default_factory=list)
    closed: bool = False  # loop back to start?


@dataclass
class DecorationSpec:
    """Abstract decoration to add."""
    kind: str     # "dot", "bar", "serif"
    x: float
    y: float
    size: float = 1.0  # relative to style's default
    angle: float = 0.0


@dataclass
class TemplateSpec:
    """Complete template output."""
    strokes: list[StrokeSpec] = field(default_factory=list)
    decorations: list[DecorationSpec] = field(default_factory=list)


TemplateFunc = Callable[[SeededRNG, AlphabetStyle], TemplateSpec]


# =====================================================================
# 1-stroke templates
# =====================================================================

def _vertical(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.5, 0.0),
        AnchorPoint(0.5, 1.0),
    ])])


def _horizontal(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.0, 0.5),
        AnchorPoint(1.0, 0.5),
    ])])


def _diagonal_down(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.1, 0.0),
        AnchorPoint(0.9, 1.0),
    ])])


def _diagonal_up(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.1, 1.0),
        AnchorPoint(0.9, 0.0),
    ])])


def _arc_left(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.8, 0.0),
        AnchorPoint(0.2, 0.5, bulge=0.4),
        AnchorPoint(0.8, 1.0),
    ])])


def _arc_right(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.2, 0.0),
        AnchorPoint(0.8, 0.5, bulge=-0.4),
        AnchorPoint(0.2, 1.0),
    ])])


def _s_curve(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.3, 0.0),
        AnchorPoint(0.7, 0.33, bulge=0.3),
        AnchorPoint(0.3, 0.67, bulge=-0.3),
        AnchorPoint(0.7, 1.0),
    ])])


def _loop(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.5, 0.1),
        AnchorPoint(0.85, 0.35, bulge=0.4),
        AnchorPoint(0.5, 0.65, bulge=0.4),
        AnchorPoint(0.15, 0.35, bulge=0.4),
        AnchorPoint(0.5, 0.1, bulge=0.4),
    ])])


def _spiral(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.5, 0.0),
        AnchorPoint(0.85, 0.3, bulge=0.35),
        AnchorPoint(0.5, 0.6, bulge=0.35),
        AnchorPoint(0.25, 0.4, bulge=0.35),
        AnchorPoint(0.4, 0.3, bulge=0.25),
        AnchorPoint(0.5, 0.35),
    ])])


def _hook_down(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.5, 0.0),
        AnchorPoint(0.5, 0.7),
        AnchorPoint(0.7, 0.9, bulge=0.3),
        AnchorPoint(0.9, 0.75),
    ])])


def _hook_up(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.5, 1.0),
        AnchorPoint(0.5, 0.3),
        AnchorPoint(0.3, 0.1, bulge=-0.3),
        AnchorPoint(0.1, 0.25),
    ])])


# =====================================================================
# 2-stroke templates
# =====================================================================

def _cross(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.0), AnchorPoint(0.5, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.45), AnchorPoint(0.9, 0.45)]),
    ])


def _t_junction(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.0), AnchorPoint(0.9, 0.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.0), AnchorPoint(0.5, 1.0)]),
    ])


def _parallel_vert(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.3, 0.0), AnchorPoint(0.3, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.7, 0.0), AnchorPoint(0.7, 1.0)]),
    ])


def _v_shape(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.0), AnchorPoint(0.5, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.9, 0.0), AnchorPoint(0.5, 1.0)]),
    ])


def _angle_shape(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.0), AnchorPoint(0.2, 0.7)]),
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.7), AnchorPoint(0.8, 0.7)]),
    ])


def _hook_bar(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.3, 0.0),
            AnchorPoint(0.3, 0.6),
            AnchorPoint(0.6, 0.85, bulge=0.3),
            AnchorPoint(0.8, 0.65),
        ]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.35), AnchorPoint(0.6, 0.35)]),
    ])


def _loop_tail(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.5, 0.1),
            AnchorPoint(0.8, 0.25, bulge=0.35),
            AnchorPoint(0.5, 0.5, bulge=0.35),
            AnchorPoint(0.2, 0.25, bulge=0.35),
            AnchorPoint(0.5, 0.1, bulge=0.35),
        ]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.5), AnchorPoint(0.5, 1.0)]),
    ])


def _arc_dot(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(
        strokes=[StrokeSpec(anchors=[
            AnchorPoint(0.2, 0.2),
            AnchorPoint(0.8, 0.5, bulge=-0.35),
            AnchorPoint(0.2, 0.8),
        ])],
        decorations=[DecorationSpec("dot", 0.5, 0.15)],
    )


def _parallel_horiz(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.3), AnchorPoint(0.9, 0.3)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.7), AnchorPoint(0.9, 0.7)]),
    ])


def _y_shape(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.15, 0.0), AnchorPoint(0.5, 0.45)]),
        StrokeSpec(anchors=[AnchorPoint(0.85, 0.0), AnchorPoint(0.5, 0.45),
                            AnchorPoint(0.5, 1.0)]),
    ])


# =====================================================================
# 3-stroke templates
# =====================================================================

def _triple_parallel(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.0), AnchorPoint(0.2, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.0), AnchorPoint(0.5, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.8, 0.0), AnchorPoint(0.8, 1.0)]),
    ])


def _open_box(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.1), AnchorPoint(0.2, 0.9)]),
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.9), AnchorPoint(0.8, 0.9)]),
        StrokeSpec(anchors=[AnchorPoint(0.8, 0.9), AnchorPoint(0.8, 0.1)]),
    ])


def _zigzag(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.0), AnchorPoint(0.5, 0.35)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.35), AnchorPoint(0.1, 0.65)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.65), AnchorPoint(0.5, 1.0)]),
    ])


def _trident(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.0), AnchorPoint(0.2, 0.6)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.0), AnchorPoint(0.5, 0.6)]),
        StrokeSpec(anchors=[AnchorPoint(0.8, 0.0), AnchorPoint(0.8, 0.6)]),
    ], decorations=[DecorationSpec("bar", 0.5, 0.6)])


def _enclosed_dot(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(
        strokes=[
            StrokeSpec(anchors=[AnchorPoint(0.2, 0.15), AnchorPoint(0.8, 0.15)]),
            StrokeSpec(anchors=[
                AnchorPoint(0.2, 0.15), AnchorPoint(0.2, 0.85),
                AnchorPoint(0.8, 0.85), AnchorPoint(0.8, 0.15),
            ]),
        ],
        decorations=[DecorationSpec("dot", 0.5, 0.5)],
    )


def _stacked_arcs(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.2, 0.15),
            AnchorPoint(0.5, 0.0, bulge=-0.3),
            AnchorPoint(0.8, 0.15),
        ]),
        StrokeSpec(anchors=[
            AnchorPoint(0.2, 0.5),
            AnchorPoint(0.5, 0.35, bulge=-0.3),
            AnchorPoint(0.8, 0.5),
        ]),
        StrokeSpec(anchors=[
            AnchorPoint(0.2, 0.85),
            AnchorPoint(0.5, 0.7, bulge=-0.3),
            AnchorPoint(0.8, 0.85),
        ]),
    ])


def _fork_shape(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.5, 1.0), AnchorPoint(0.5, 0.4)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.4), AnchorPoint(0.2, 0.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.4), AnchorPoint(0.8, 0.0)]),
    ])


def _bridge(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.15, 0.9), AnchorPoint(0.15, 0.2)]),
        StrokeSpec(anchors=[
            AnchorPoint(0.15, 0.2),
            AnchorPoint(0.5, 0.0, bulge=-0.3),
            AnchorPoint(0.85, 0.2),
        ]),
        StrokeSpec(anchors=[AnchorPoint(0.85, 0.2), AnchorPoint(0.85, 0.9)]),
    ])


# =====================================================================
# 4-stroke templates
# =====================================================================

def _grid(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.3, 0.1), AnchorPoint(0.3, 0.9)]),
        StrokeSpec(anchors=[AnchorPoint(0.7, 0.1), AnchorPoint(0.7, 0.9)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.35), AnchorPoint(0.9, 0.35)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.65), AnchorPoint(0.9, 0.65)]),
    ])


def _diamond(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.0), AnchorPoint(0.9, 0.5)]),
        StrokeSpec(anchors=[AnchorPoint(0.9, 0.5), AnchorPoint(0.5, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 1.0), AnchorPoint(0.1, 0.5)]),
        StrokeSpec(anchors=[AnchorPoint(0.1, 0.5), AnchorPoint(0.5, 0.0)]),
    ])


def _double_loop(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.5, 0.05),
            AnchorPoint(0.8, 0.15, bulge=0.35),
            AnchorPoint(0.5, 0.35, bulge=0.35),
            AnchorPoint(0.2, 0.15, bulge=0.35),
            AnchorPoint(0.5, 0.05, bulge=0.35),
        ]),
        StrokeSpec(anchors=[
            AnchorPoint(0.5, 0.5),
            AnchorPoint(0.8, 0.6, bulge=0.35),
            AnchorPoint(0.5, 0.8, bulge=0.35),
            AnchorPoint(0.2, 0.6, bulge=0.35),
            AnchorPoint(0.5, 0.5, bulge=0.35),
        ]),
        StrokeSpec(anchors=[AnchorPoint(0.5, 0.35), AnchorPoint(0.5, 0.5)]),
    ])


def _nested_arcs(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.15, 0.2),
            AnchorPoint(0.5, 0.0, bulge=-0.4),
            AnchorPoint(0.85, 0.2),
        ]),
        StrokeSpec(anchors=[
            AnchorPoint(0.25, 0.3),
            AnchorPoint(0.5, 0.15, bulge=-0.3),
            AnchorPoint(0.75, 0.3),
        ]),
        StrokeSpec(anchors=[AnchorPoint(0.15, 0.2), AnchorPoint(0.15, 0.9)]),
        StrokeSpec(anchors=[AnchorPoint(0.85, 0.2), AnchorPoint(0.85, 0.9)]),
    ])


def _cross_dots(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(
        strokes=[
            StrokeSpec(anchors=[AnchorPoint(0.5, 0.1), AnchorPoint(0.5, 0.9)]),
            StrokeSpec(anchors=[AnchorPoint(0.15, 0.5), AnchorPoint(0.85, 0.5)]),
        ],
        decorations=[
            DecorationSpec("dot", 0.25, 0.25),
            DecorationSpec("dot", 0.75, 0.25),
            DecorationSpec("dot", 0.25, 0.75),
            DecorationSpec("dot", 0.75, 0.75),
        ],
    )


def _arrow_up(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.5, 1.0), AnchorPoint(0.5, 0.15)]),
        StrokeSpec(anchors=[AnchorPoint(0.2, 0.35), AnchorPoint(0.5, 0.15)]),
        StrokeSpec(anchors=[AnchorPoint(0.8, 0.35), AnchorPoint(0.5, 0.15)]),
    ])


def _ladder(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[AnchorPoint(0.25, 0.0), AnchorPoint(0.25, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.75, 0.0), AnchorPoint(0.75, 1.0)]),
        StrokeSpec(anchors=[AnchorPoint(0.25, 0.35), AnchorPoint(0.75, 0.35)]),
        StrokeSpec(anchors=[AnchorPoint(0.25, 0.65), AnchorPoint(0.75, 0.65)]),
    ])


def _wave(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[StrokeSpec(anchors=[
        AnchorPoint(0.0, 0.5),
        AnchorPoint(0.25, 0.2, bulge=0.3),
        AnchorPoint(0.5, 0.5, bulge=-0.3),
        AnchorPoint(0.75, 0.8, bulge=0.3),
        AnchorPoint(1.0, 0.5),
    ])])


def _crescent(rng: SeededRNG, style: AlphabetStyle) -> TemplateSpec:
    return TemplateSpec(strokes=[
        StrokeSpec(anchors=[
            AnchorPoint(0.7, 0.1),
            AnchorPoint(0.2, 0.5, bulge=0.45),
            AnchorPoint(0.7, 0.9),
        ]),
        StrokeSpec(anchors=[
            AnchorPoint(0.7, 0.1),
            AnchorPoint(0.4, 0.5, bulge=0.25),
            AnchorPoint(0.7, 0.9),
        ]),
    ])


# =====================================================================
# Template registry
# =====================================================================

TEMPLATES: dict[str, TemplateFunc] = {
    # 1-stroke
    "vertical": _vertical,
    "horizontal": _horizontal,
    "diagonal_down": _diagonal_down,
    "diagonal_up": _diagonal_up,
    "arc_left": _arc_left,
    "arc_right": _arc_right,
    "s_curve": _s_curve,
    "loop": _loop,
    "spiral": _spiral,
    "hook_down": _hook_down,
    "hook_up": _hook_up,
    "wave": _wave,
    # 2-stroke
    "cross": _cross,
    "t_junction": _t_junction,
    "parallel_vert": _parallel_vert,
    "parallel_horiz": _parallel_horiz,
    "v_shape": _v_shape,
    "angle_shape": _angle_shape,
    "hook_bar": _hook_bar,
    "loop_tail": _loop_tail,
    "arc_dot": _arc_dot,
    "y_shape": _y_shape,
    "crescent": _crescent,
    # 3-stroke
    "triple_parallel": _triple_parallel,
    "open_box": _open_box,
    "zigzag": _zigzag,
    "trident": _trident,
    "enclosed_dot": _enclosed_dot,
    "stacked_arcs": _stacked_arcs,
    "fork_shape": _fork_shape,
    "bridge": _bridge,
    "arrow_up": _arrow_up,
    # 4-stroke
    "grid": _grid,
    "diamond": _diamond,
    "double_loop": _double_loop,
    "nested_arcs": _nested_arcs,
    "cross_dots": _cross_dots,
    "ladder": _ladder,
}


def select_templates(rng: SeededRNG, count: int = 26) -> list[str]:
    """Select *count* unique templates from the registry.

    If fewer than *count* templates exist, some are reused with a suffix.
    """
    names = list(TEMPLATES.keys())
    rng_sel = rng.fork("template_selection")
    rng_sel.shuffle(names)

    if len(names) >= count:
        return names[:count]

    # Reuse templates with variant suffixes
    selected = list(names)
    i = 0
    while len(selected) < count:
        selected.append(f"{names[i % len(names)]}_v{i // len(names) + 2}")
        i += 1
    return selected
