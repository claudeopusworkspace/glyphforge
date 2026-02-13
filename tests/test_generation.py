"""End-to-end generation tests."""

import os
import tempfile

import glyphforge
from glyphforge.presets import list_presets
from glyphforge.templates import TEMPLATES
from glyphforge.validation import (
    check_distinctiveness,
    estimate_ink_coverage,
    glyph_feature_vector,
    validate_glyph,
)
from glyphforge.geometry import BoundingBox


def test_generate_26_glyphs():
    """Basic generation produces 26 glyphs."""
    alphabet = glyphforge.generate(seed=42)
    assert len(alphabet) == 26


def test_glyph_labels():
    """All 26 labels A-Z are present."""
    alphabet = glyphforge.generate(seed=42)
    labels = [g.label for g in alphabet]
    assert labels == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_all_glyphs_have_outlines():
    """Every glyph should have at least one outline polygon."""
    alphabet = glyphforge.generate(seed=42)
    for g in alphabet:
        assert len(g.outline.polygons) > 0, f"Glyph {g.label} has no outlines"


def test_reproducibility():
    """Same seed produces identical output."""
    a1 = glyphforge.generate(seed=12345)
    a2 = glyphforge.generate(seed=12345)
    for i in range(26):
        g1, g2 = a1[i], a2[i]
        assert g1.template_name == g2.template_name
        assert len(g1.outline.polygons) == len(g2.outline.polygons)
        for p1, p2 in zip(g1.outline.polygons, g2.outline.polygons):
            assert len(p1) == len(p2)
            for pt1, pt2 in zip(p1, p2):
                assert abs(pt1.x - pt2.x) < 1e-10
                assert abs(pt1.y - pt2.y) < 1e-10


def test_different_seeds_different_output():
    """Different seeds produce different alphabets."""
    a1 = glyphforge.generate(seed=1)
    a2 = glyphforge.generate(seed=2)
    # At least some templates should differ
    diffs = sum(1 for i in range(26)
                if a1[i].template_name != a2[i].template_name)
    assert diffs > 0


def test_presets_generate():
    """All presets should produce valid alphabets."""
    for name in list_presets():
        alphabet = glyphforge.generate(seed=42, preset=name)
        assert len(alphabet) == 26
        for g in alphabet:
            assert len(g.outline.polygons) > 0, \
                f"Preset {name}, glyph {g.label} empty"


def test_overrides():
    """Overrides should modify the style."""
    a = glyphforge.generate(seed=42, overrides={"stroke_width": 0.2})
    assert a.style.stroke_width == 0.2


def test_template_coverage():
    """We should have at least 30 templates."""
    assert len(TEMPLATES) >= 30


def test_svg_sheet_export():
    """SVG sheet export should create a file."""
    alphabet = glyphforge.generate(seed=42)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sheet.svg")
        result = alphabet.to_svg_sheet(path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "<svg" in content
        assert "polygon" in content


def test_svg_individual_export():
    """Individual SVG export should create 26 files."""
    alphabet = glyphforge.generate(seed=42)
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = alphabet.to_svg(tmpdir)
        assert len(paths) == 26
        for p in paths:
            assert os.path.exists(p)


def test_html_preview():
    """HTML preview generation should produce valid HTML."""
    from glyphforge.preview import generate_html
    alphabet = glyphforge.generate(seed=42)
    html = generate_html(alphabet)
    assert "<!DOCTYPE html>" in html
    assert "GlyphForge Specimen" in html
    assert "Seed: 42" in html
    # Should contain inline SVGs for all 26 glyphs
    for label in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        assert f">{label}<" in html


def test_validation_basic():
    """Validation should run without errors."""
    alphabet = glyphforge.generate(seed=42)
    ref_bbox = BoundingBox(0, 0, alphabet.style.glyph_width,
                            alphabet.style.cap_height + alphabet.style.descender_depth)
    for g in alphabet:
        result = validate_glyph(g, ref_bbox)
        # At minimum, all should have outlines
        assert "no outline" not in " ".join(result.issues).lower()


def test_feature_vectors():
    """Feature vectors should be numeric and non-degenerate."""
    alphabet = glyphforge.generate(seed=42)
    for g in alphabet:
        fv = glyph_feature_vector(g)
        assert len(fv) == 8
        assert all(isinstance(v, float) for v in fv)


def test_multiple_seeds():
    """Generate with several seeds to ensure robustness."""
    for seed in [1, 42, 100, 999, 12345]:
        alphabet = glyphforge.generate(seed=seed)
        assert len(alphabet) == 26
        for g in alphabet:
            assert len(g.outline.polygons) > 0
