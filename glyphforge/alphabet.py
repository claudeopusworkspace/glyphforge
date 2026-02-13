"""Alphabet container — 26 Glyphs + Style."""

from __future__ import annotations

import string
from dataclasses import dataclass, field
from typing import Iterator

from .glyph import Glyph
from .style import AlphabetStyle

LABELS = list(string.ascii_uppercase)  # A-Z


@dataclass(slots=True)
class Alphabet:
    """Container for a complete 26-glyph alphabet with its style."""
    style: AlphabetStyle
    seed: int
    glyphs: list[Glyph] = field(default_factory=list)
    preset_name: str | None = None

    # -- Access -----------------------------------------------------------

    def __getitem__(self, key: int | str) -> Glyph:
        if isinstance(key, int):
            return self.glyphs[key]
        if isinstance(key, str) and len(key) == 1:
            idx = LABELS.index(key.upper())
            return self.glyphs[idx]
        raise KeyError(f"Invalid glyph key: {key!r}")

    def __len__(self) -> int:
        return len(self.glyphs)

    def __iter__(self) -> Iterator[Glyph]:
        return iter(self.glyphs)

    # -- Export (delegated to svg_export / preview modules) ----------------

    def to_svg(self, output_dir: str) -> list[str]:
        """Export individual SVG files for each glyph. Returns file paths."""
        from .svg_export import export_individual
        return export_individual(self, output_dir)

    def to_svg_sheet(self, path: str) -> str:
        """Export a specimen sheet with all 26 glyphs in a grid."""
        from .svg_export import export_sheet
        return export_sheet(self, path)

    def preview(self) -> str:
        """Generate HTML specimen page and open in browser. Returns path."""
        from .preview import preview_alphabet
        return preview_alphabet(self)
