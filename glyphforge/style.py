"""AlphabetStyle dataclass + style generation from seed."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from enum import Enum
from typing import Any

from .rng import SeededRNG
from . import settings


class StrokeWidthMode(Enum):
    STATIC = "static"      # uniform width throughout every stroke
    GRADIENT = "gradient"  # calligraphic: thick at start, thin at end


class CapStyle(Enum):
    ROUND = "round"
    FLAT = "flat"


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
    stroke_width: float = 0.08      # stroke width (max width in gradient mode)
    stroke_width_mode: StrokeWidthMode = StrokeWidthMode.STATIC
    stroke_taper_ratio: float = 0.3   # gradient mode: end width as fraction of start
    stroke_angle: float = 0.0       # pen angle in radians
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


def _rng_range(r: SeededRNG, param: str) -> float:
    """Sample a value from the range defined in settings.json."""
    lo, hi = settings.get_range(param)
    return r.uniform(lo, hi)


def _rng_enum(r: SeededRNG, param: str, enum_cls: type) -> Any:
    """Pick a random allowed enum value from settings.json."""
    allowed = settings.get_allowed(param)
    value = r.choice(allowed)
    return enum_cls(value)


def generate_style(rng: SeededRNG) -> AlphabetStyle:
    """Generate a random AlphabetStyle from an RNG.

    All ranges and allowed values are read from settings.json.
    """
    r = rng.fork("style")

    return AlphabetStyle(
        # Metrics
        x_height=_rng_range(r, "x_height"),
        cap_height=_rng_range(r, "cap_height"),
        descender_depth=_rng_range(r, "descender_depth"),
        glyph_width=_rng_range(r, "glyph_width"),

        # Stroke
        stroke_width=_rng_range(r, "stroke_width"),
        stroke_width_mode=_rng_enum(r, "stroke_width_mode", StrokeWidthMode),
        stroke_taper_ratio=_rng_range(r, "stroke_taper_ratio"),
        stroke_angle=_rng_range(r, "stroke_angle"),
        cap_style=_rng_enum(r, "cap_style", CapStyle),
        join_style=_rng_enum(r, "join_style", JoinStyle),

        # Curvature
        curvature_bias=_rng_range(r, "curvature_bias"),
        loop_probability=_rng_range(r, "loop_probability"),
        inflection_frequency=_rng_range(r, "inflection_frequency"),

        # Structure
        stroke_count_mean=_rng_range(r, "stroke_count_mean"),
        stroke_count_sigma=_rng_range(r, "stroke_count_sigma"),
        component_reuse=_rng_range(r, "component_reuse"),
        connectivity=_rng_range(r, "connectivity"),
        symmetry_bias=_rng_range(r, "symmetry_bias"),

        # Decorative
        serif_style=_rng_enum(r, "serif_style", SerifStyle),
        serif_size=_rng_range(r, "serif_size"),
        dot_frequency=_rng_range(r, "dot_frequency"),
        bar_frequency=_rng_range(r, "bar_frequency"),
        flourish_probability=_rng_range(r, "flourish_probability"),

        # Direction
        entry_zone=_rng_range(r, "entry_zone"),
        exit_zone=_rng_range(r, "exit_zone"),
        horizontal_bias=_rng_range(r, "horizontal_bias"),

        # Global modifiers
        baseline_jitter=_rng_range(r, "baseline_jitter"),
        scale_jitter=_rng_range(r, "scale_jitter"),
        rotation_jitter=_rng_range(r, "rotation_jitter"),
        aspect_ratio_variance=_rng_range(r, "aspect_ratio_variance"),

        # Control points
        control_point_jitter=_rng_range(r, "control_point_jitter"),
        anchor_jitter=_rng_range(r, "anchor_jitter"),
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
        if key == "stroke_width_mode" and isinstance(value, str):
            value = StrokeWidthMode(value)
        elif key == "cap_style" and isinstance(value, str):
            value = CapStyle(value)
        elif key == "join_style" and isinstance(value, str):
            value = JoinStyle(value)
        elif key == "serif_style" and isinstance(value, str):
            value = SerifStyle(value)
        converted[key] = value

    return replace(style, **converted)
