"""Top-level orchestrator — ties style → skeleton → expansion → export."""

from __future__ import annotations

import string

from .alphabet import Alphabet
from .components import ComponentLibrary
from .expansion import StrokeExpander
from .geometry import BoundingBox
from .glyph import Glyph
from .presets import get_preset
from .rng import SeededRNG
from .skeleton import SkeletonGenerator
from .style import AlphabetStyle, apply_overrides, generate_style
from .validation import check_distinctiveness, validate_glyph

LABELS = list(string.ascii_uppercase)


class AlphabetGenerator:
    """Generate a complete alphabet from a seed."""

    def __init__(self, seed: int, preset: str | None = None,
                 overrides: dict | None = None):
        self._seed = seed
        self._rng = SeededRNG(seed)
        self._preset = preset
        self._overrides = overrides or {}

    def generate(self) -> Alphabet:
        """Generate a complete 26-glyph alphabet."""
        # 1. Build style
        style = self._build_style()

        # 2. Build component library
        comp_rng = self._rng.fork("components")
        components = ComponentLibrary(comp_rng, style)

        # 3. Generate skeletons
        skel_gen = SkeletonGenerator(self._rng, style, components)
        skeletons = skel_gen.generate_all()

        # 4. Expand strokes
        expander = StrokeExpander(style)
        glyphs: list[Glyph] = []

        # Reference bbox for validation
        total_h = style.cap_height + style.descender_depth
        ref_bbox = BoundingBox(0, 0, style.glyph_width, total_h)

        for i, skeleton in enumerate(skeletons):
            outline = expander.expand_skeleton(skeleton)
            glyph = Glyph(
                label=LABELS[i],
                index=i,
                skeleton=skeleton,
                outline=outline,
                template_name=skeleton.template_name,
            )

            # Validate (soft — log issues but don't reject)
            result = validate_glyph(glyph, ref_bbox)
            # In future: could regenerate on validation failure

            glyphs.append(glyph)

        return Alphabet(
            style=style,
            seed=self._seed,
            glyphs=glyphs,
            preset_name=self._preset,
        )

    def _build_style(self) -> AlphabetStyle:
        """Build style from preset/random + overrides."""
        if self._preset:
            style = get_preset(self._preset)
        else:
            style = generate_style(self._rng)

        if self._overrides:
            style = apply_overrides(style, self._overrides)

        return style
