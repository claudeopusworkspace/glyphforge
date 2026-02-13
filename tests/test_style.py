"""Tests for style generation and presets."""

from glyphforge.rng import SeededRNG
from glyphforge.style import (
    AlphabetStyle,
    CapStyle,
    apply_overrides,
    generate_style,
)
from glyphforge.presets import PRESETS, get_preset, list_presets


def test_generate_style_determinism():
    """Same seed produces same style."""
    s1 = generate_style(SeededRNG(42))
    s2 = generate_style(SeededRNG(42))
    assert s1 == s2


def test_generate_style_variation():
    """Different seeds produce different styles."""
    s1 = generate_style(SeededRNG(1))
    s2 = generate_style(SeededRNG(2))
    assert s1 != s2


def test_style_is_frozen():
    """AlphabetStyle should be immutable."""
    s = AlphabetStyle()
    try:
        s.stroke_width = 999  # type: ignore
        assert False, "Should raise"
    except AttributeError:
        pass


def test_apply_overrides():
    """Overrides should replace specific fields."""
    s = AlphabetStyle()
    s2 = apply_overrides(s, {"stroke_width": 0.5, "dot_frequency": 0.9})
    assert s2.stroke_width == 0.5
    assert s2.dot_frequency == 0.9
    assert s2.curvature_bias == s.curvature_bias  # unchanged


def test_apply_overrides_enum_string():
    """String values for enum fields should be auto-converted."""
    s = AlphabetStyle()
    s2 = apply_overrides(s, {"cap_style": "flat"})
    assert s2.cap_style == CapStyle.FLAT


def test_apply_overrides_unknown_field():
    """Unknown fields should raise ValueError."""
    s = AlphabetStyle()
    try:
        apply_overrides(s, {"nonexistent": 42})
        assert False, "Should raise"
    except ValueError:
        pass


def test_presets_exist():
    """At least 4 presets should be available."""
    names = list_presets()
    assert len(names) >= 4
    for name in names:
        style = get_preset(name)
        assert isinstance(style, AlphabetStyle)


def test_preset_unknown():
    """Unknown preset should raise ValueError."""
    try:
        get_preset("nonexistent_preset")
        assert False, "Should raise"
    except ValueError:
        pass
