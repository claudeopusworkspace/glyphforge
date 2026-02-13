"""Named style presets — curated starting points for common script aesthetics."""

from __future__ import annotations

from .style import AlphabetStyle, CapStyle, JoinStyle, SerifStyle

PRESETS: dict[str, AlphabetStyle] = {
    "angular": AlphabetStyle(
        curvature_bias=0.1,
        loop_probability=0.02,
        inflection_frequency=0.1,
        stroke_width=0.07,
        stroke_taper=0.1,
        cap_style=CapStyle.FLAT,
        join_style=JoinStyle.MITER,
        serif_style=SerifStyle.SLAB,
        serif_size=0.04,
        symmetry_bias=0.3,
        dot_frequency=0.05,
        bar_frequency=0.15,
        connectivity=0.3,
        control_point_jitter=0.02,
    ),
    "flowing": AlphabetStyle(
        curvature_bias=0.9,
        loop_probability=0.25,
        inflection_frequency=0.5,
        stroke_width=0.06,
        stroke_width_variance=0.03,
        stroke_taper=0.35,
        cap_style=CapStyle.TAPERED,
        join_style=JoinStyle.ROUND,
        serif_style=SerifStyle.NONE,
        connectivity=0.8,
        symmetry_bias=0.1,
        dot_frequency=0.15,
        flourish_probability=0.12,
        control_point_jitter=0.08,
    ),
    "geometric": AlphabetStyle(
        curvature_bias=0.4,
        loop_probability=0.15,
        inflection_frequency=0.2,
        stroke_width=0.08,
        stroke_width_variance=0.0,
        stroke_taper=0.0,
        cap_style=CapStyle.FLAT,
        join_style=JoinStyle.MITER,
        serif_style=SerifStyle.NONE,
        symmetry_bias=0.45,
        connectivity=0.5,
        dot_frequency=0.1,
        bar_frequency=0.1,
        control_point_jitter=0.02,
        anchor_jitter=0.01,
    ),
    "blocky": AlphabetStyle(
        curvature_bias=0.05,
        loop_probability=0.0,
        inflection_frequency=0.05,
        stroke_width=0.12,
        stroke_width_variance=0.01,
        stroke_taper=0.0,
        cap_style=CapStyle.FLAT,
        join_style=JoinStyle.MITER,
        serif_style=SerifStyle.SLAB,
        serif_size=0.06,
        symmetry_bias=0.4,
        connectivity=0.2,
        dot_frequency=0.0,
        bar_frequency=0.1,
        control_point_jitter=0.01,
        anchor_jitter=0.01,
    ),
    "ornate": AlphabetStyle(
        curvature_bias=0.7,
        loop_probability=0.2,
        inflection_frequency=0.4,
        stroke_width=0.05,
        stroke_width_variance=0.03,
        stroke_taper=0.3,
        cap_style=CapStyle.TAPERED,
        join_style=JoinStyle.ROUND,
        serif_style=SerifStyle.FLARE,
        serif_size=0.05,
        symmetry_bias=0.15,
        dot_frequency=0.2,
        bar_frequency=0.1,
        flourish_probability=0.15,
        connectivity=0.6,
        control_point_jitter=0.07,
    ),
    "runic": AlphabetStyle(
        curvature_bias=0.0,
        loop_probability=0.0,
        inflection_frequency=0.0,
        stroke_width=0.07,
        stroke_width_variance=0.01,
        stroke_taper=0.05,
        cap_style=CapStyle.FLAT,
        join_style=JoinStyle.MITER,
        serif_style=SerifStyle.WEDGE,
        serif_size=0.03,
        symmetry_bias=0.35,
        connectivity=0.4,
        dot_frequency=0.0,
        bar_frequency=0.0,
        flourish_probability=0.0,
        stroke_count_mean=2.0,
        stroke_count_sigma=0.5,
        control_point_jitter=0.01,
        anchor_jitter=0.01,
    ),
}


def get_preset(name: str) -> AlphabetStyle:
    """Return a preset by name. Raises ValueError if unknown."""
    key = name.lower()
    if key not in PRESETS:
        available = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {name!r}. Available: {available}")
    return PRESETS[key]


def list_presets() -> list[str]:
    """Return sorted list of preset names."""
    return sorted(PRESETS)
