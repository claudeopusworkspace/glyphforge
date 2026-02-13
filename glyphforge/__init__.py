"""GlyphForge — Procedural Alphabet Generator.

Generate unique writing systems from a seed, with shared visual style
parameters creating coherence across all 26 glyphs.

Usage:
    import glyphforge
    alphabet = glyphforge.generate(seed=42)
    alphabet = glyphforge.generate(seed=42, preset="flowing")
    alphabet.to_svg("output/")
    alphabet.to_svg_sheet("specimen.svg")
    alphabet.preview()
"""

from .alphabet import Alphabet
from .generator import AlphabetGenerator
from .presets import list_presets
from .style import AlphabetStyle

__version__ = "0.1.0"


def generate(seed: int = 42, preset: str | None = None,
             overrides: dict | None = None) -> Alphabet:
    """Generate a complete 26-glyph alphabet.

    Args:
        seed: Random seed for reproducibility.
        preset: Optional named style preset (angular, flowing, geometric,
                blocky, ornate, runic).
        overrides: Optional dict of style parameter overrides.

    Returns:
        An Alphabet containing 26 Glyphs with matching style.
    """
    gen = AlphabetGenerator(seed=seed, preset=preset, overrides=overrides)
    return gen.generate()
