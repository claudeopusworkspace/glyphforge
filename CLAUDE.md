# GlyphForge

Procedural glyph/font generator that creates randomized alphabets with internally consistent visual style. Designed as a standalone Python library/tool, with integration into Lingua Perdita (idle game) as a primary use case.

## Key Commands
- **Run**: `source .venv/bin/activate && python -m glyphforge`
- **Test**: `source .venv/bin/activate && pytest`
- **Install deps**: `source .venv/bin/activate && pip install -r requirements.txt`
- **Preview**: `source .venv/bin/activate && python -m glyphforge.preview`

## Architecture
- Skeleton + stroke expansion pipeline
- Seeded RNG with SHA-256 domain-forking for reproducibility
- 30+ structural templates for topological diversity
- Style parameters create visual coherence across all 26 glyphs

## Conventions
- Language: Python 3.12+
- Cross-platform (Linux, macOS, Windows)
- Virtual environment: `.venv/`
- Testing: pytest
- Dependencies: svgwrite, numpy, pyclipper
