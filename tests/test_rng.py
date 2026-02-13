"""Tests for SeededRNG determinism and fork isolation."""

from glyphforge.rng import SeededRNG


def test_determinism():
    """Same seed produces same sequence."""
    r1 = SeededRNG(42)
    r2 = SeededRNG(42)
    for _ in range(100):
        assert r1.random() == r2.random()


def test_different_seeds():
    """Different seeds produce different sequences."""
    r1 = SeededRNG(1)
    r2 = SeededRNG(2)
    vals1 = [r1.random() for _ in range(10)]
    vals2 = [r2.random() for _ in range(10)]
    assert vals1 != vals2


def test_fork_determinism():
    """Same fork path produces same sequence."""
    f1 = SeededRNG(42).fork("a").fork("b")
    f2 = SeededRNG(42).fork("a").fork("b")
    for _ in range(50):
        assert f1.random() == f2.random()


def test_fork_isolation():
    """Different fork domains produce different sequences."""
    base = SeededRNG(42)
    fa = base.fork("a")
    fb = base.fork("b")
    va = [fa.random() for _ in range(10)]
    vb = [fb.random() for _ in range(10)]
    assert va != vb


def test_fork_independence():
    """Consuming values from one fork doesn't affect another."""
    r1 = SeededRNG(42)
    fa = r1.fork("a")
    # Consume some values from the base
    for _ in range(100):
        r1.random()
    # Fork from a fresh base with same seed
    r2 = SeededRNG(42)
    fb = r2.fork("a")
    # Should be identical despite base divergence
    for _ in range(20):
        assert fa.random() == fb.random()


def test_coin():
    """Coin should return bool and respect probability."""
    r = SeededRNG(42)
    results = [r.coin(0.5) for _ in range(1000)]
    assert all(isinstance(v, bool) for v in results)
    # Roughly 50% true (allow wide margin)
    ratio = sum(results) / len(results)
    assert 0.3 < ratio < 0.7
