"""Seeded RNG with SHA-256 domain-forking for reproducibility."""

from __future__ import annotations

import hashlib
import random
from typing import Sequence


class SeededRNG:
    """Deterministic RNG that supports domain-forking.

    Each fork produces an independent stream — changes to one glyph's
    generation never cascade to others.  Same seed + domain → same
    sequence across runs and platforms (Mersenne Twister).
    """

    def __init__(self, seed: int, domain: str = "root"):
        self._base_seed = seed
        self._domain = domain
        # Derive a deterministic 32-bit seed from (seed, domain) via SHA-256
        h = hashlib.sha256(f"{seed}:{domain}".encode()).digest()
        derived = int.from_bytes(h[:8], "little")
        self._rng = random.Random(derived)

    # -- Forking ----------------------------------------------------------

    def fork(self, subdomain: str) -> SeededRNG:
        """Create a child RNG with an independent stream."""
        return SeededRNG(self._base_seed, f"{self._domain}/{subdomain}")

    # -- Primitives -------------------------------------------------------

    def uniform(self, lo: float = 0.0, hi: float = 1.0) -> float:
        return self._rng.uniform(lo, hi)

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        return self._rng.gauss(mu, sigma)

    def randint(self, lo: int, hi: int) -> int:
        """Inclusive on both ends."""
        return self._rng.randint(lo, hi)

    def random(self) -> float:
        """Uniform in [0, 1)."""
        return self._rng.random()

    def choice(self, seq: Sequence):
        return self._rng.choice(seq)

    def sample(self, population: Sequence, k: int) -> list:
        return self._rng.sample(population, k)

    def shuffle(self, lst: list) -> None:
        self._rng.shuffle(lst)

    def coin(self, p: float = 0.5) -> bool:
        """Return True with probability *p*."""
        return self._rng.random() < p

    @property
    def seed(self) -> int:
        return self._base_seed

    @property
    def domain(self) -> str:
        return self._domain
