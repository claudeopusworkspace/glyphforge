"""AlphabetStyle dataclass + style generation from seed."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from enum import Enum
from typing import Any

from .rng import SeededRNG


class CapStyle(Enum):
    ROUND = "round"
    FLAT = "flat"
    TAPERED = "tapered"


class JoinStyle(Enum):
    ROUND = "round"
    MITER = "miter"
    BEVEL = "bevel"


class SerifStyle(Enum):
    NONE = "none"
    SLAB = "slab"
    WEDGE = "wedge"
    FLARE = "flare"


@dataclass(frozen=True, slots=True)
class AlphabetStyle:
    """All parameters that define a writing system's visual identity.

    Values are normalised: probabilities in [0,1], dimensions relative to
    a 1.0-unit em-square (except stroke_width which is absolute within
    that square).
    """

    # -- Metrics ----------------------------------------------------------
    x_height: float = 0.55          # main body height
    cap_height: float = 0.75        # tall strokes
    descender_depth: float = 0.25   # below baseline
    glyph_width: float = 0.6        # average width

    # -- Stroke -----------------------------------------------------------
    stroke_width: float = 0.08      # base stroke width
    stroke_width_variance: float = 0.02  # random variation in width
    stroke_angle: float = 0.0       # pen angle in radians
    stroke_taper: float = 0.0       # taper at stroke ends [0,1]
    cap_style: CapStyle = CapStyle.ROUND
    join_style: JoinStyle = JoinStyle.ROUND

    # -- Curvature --------------------------------------------------------
    curvature_bias: float = 0.5     # 0=angular, 1=fully curved
    loop_probability: float = 0.1   # chance of loops in strokes
    inflection_frequency: float = 0.3  # s-curves and direction changes

    # -- Structure --------------------------------------------------------
    stroke_count_mean: float = 2.5  # avg strokes per glyph
    stroke_count_sigma: float = 0.8
    component_reuse: float = 0.3    # probability of reusing shared radicals
    connectivity: float = 0.5       # 0=disconnected strokes, 1=fully connected
    symmetry_bias: float = 0.2      # 0=asymmetric, 1=mostly symmetric

    # -- Decorative -------------------------------------------------------
    serif_style: SerifStyle = SerifStyle.NONE
    serif_size: float = 0.04
    dot_frequency: float = 0.1      # prob of adding dots
    bar_frequency: float = 0.05     # prob of adding crossbars
    flourish_probability: float = 0.05  # prob of decorative flourishes

    # -- Direction/rhythm -------------------------------------------------
    entry_zone: float = 0.3         # vertical position where strokes start [0,1]
    exit_zone: float = 0.7          # vertical position where strokes end [0,1]
    horizontal_bias: float = 0.0    # -1=left-leaning, +1=right-leaning

    # -- Global modifiers -------------------------------------------------
    baseline_jitter: float = 0.02   # random baseline offset
    scale_jitter: float = 0.03      # random size variation
    rotation_jitter: float = 0.02   # random rotation (radians)
    aspect_ratio_variance: float = 0.05  # width variation

    # -- Control points ---------------------------------------------------
    control_point_jitter: float = 0.05  # bezier handle randomness
    anchor_jitter: float = 0.03     # anchor point positional noise


def generate_style(rng: SeededRNG) -> AlphabetStyle:
    """Generate a random AlphabetStyle from an RNG."""
    r = rng.fork("style")

    cap = r.choice(list(CapStyle))
    join = r.choice(list(JoinStyle))
    serif = r.choice(list(SerifStyle))

    return AlphabetStyle(
        # Metrics
        x_height=r.uniform(0.45, 0.65),
        cap_height=r.uniform(0.65, 0.85),
        descender_depth=r.uniform(0.15, 0.35),
        glyph_width=r.uniform(0.45, 0.75),

        # Stroke
        stroke_width=r.uniform(0.04, 0.14),
        stroke_width_variance=r.uniform(0.0, 0.04),
        stroke_angle=r.uniform(-0.6, 0.6),
        stroke_taper=r.uniform(0.0, 0.5),
        cap_style=cap,
        join_style=join,

        # Curvature
        curvature_bias=r.uniform(0.0, 1.0),
        loop_probability=r.uniform(0.0, 0.3),
        inflection_frequency=r.uniform(0.0, 0.6),

        # Structure
        stroke_count_mean=r.uniform(1.5, 3.5),
        stroke_count_sigma=r.uniform(0.3, 1.2),
        component_reuse=r.uniform(0.0, 0.6),
        connectivity=r.uniform(0.1, 0.9),
        symmetry_bias=r.uniform(0.0, 0.5),

        # Decorative
        serif_style=serif,
        serif_size=r.uniform(0.02, 0.08),
        dot_frequency=r.uniform(0.0, 0.3),
        bar_frequency=r.uniform(0.0, 0.2),
        flourish_probability=r.uniform(0.0, 0.15),

        # Direction
        entry_zone=r.uniform(0.1, 0.5),
        exit_zone=r.uniform(0.5, 0.9),
        horizontal_bias=r.uniform(-0.5, 0.5),

        # Global modifiers
        baseline_jitter=r.uniform(0.0, 0.04),
        scale_jitter=r.uniform(0.0, 0.06),
        rotation_jitter=r.uniform(0.0, 0.04),
        aspect_ratio_variance=r.uniform(0.0, 0.1),

        # Control points
        control_point_jitter=r.uniform(0.02, 0.10),
        anchor_jitter=r.uniform(0.01, 0.06),
    )


def apply_overrides(style: AlphabetStyle, overrides: dict[str, Any]) -> AlphabetStyle:
    """Return a new style with overrides applied.

    Enum fields accept string values (e.g. 'round' → CapStyle.ROUND).
    """
    field_names = {f.name for f in fields(AlphabetStyle)}
    converted: dict[str, Any] = {}

    for key, value in overrides.items():
        if key not in field_names:
            raise ValueError(f"Unknown style parameter: {key!r}")
        # Auto-convert strings to enums
        if key == "cap_style" and isinstance(value, str):
            value = CapStyle(value)
        elif key == "join_style" and isinstance(value, str):
            value = JoinStyle(value)
        elif key == "serif_style" and isinstance(value, str):
            value = SerifStyle(value)
        converted[key] = value

    return replace(style, **converted)
