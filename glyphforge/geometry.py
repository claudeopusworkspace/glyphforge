"""Point, BoundingBox, and affine transform utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    # -- Arithmetic -------------------------------------------------------

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Point:
        return self.__mul__(scalar)

    def __neg__(self) -> Point:
        return Point(-self.x, -self.y)

    # -- Geometry ---------------------------------------------------------

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> Point:
        ln = self.length()
        if ln < 1e-12:
            return Point(0.0, 0.0)
        return Point(self.x / ln, self.y / ln)

    def dot(self, other: Point) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Point) -> float:
        """2D cross product (z-component)."""
        return self.x * other.y - self.y * other.x

    def distance_to(self, other: Point) -> float:
        return (other - self).length()

    def lerp(self, other: Point, t: float) -> Point:
        return Point(self.x + (other.x - self.x) * t,
                     self.y + (other.y - self.y) * t)

    def rotate(self, angle_rad: float) -> Point:
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return Point(self.x * c - self.y * s, self.x * s + self.y * c)

    def rotate_around(self, center: Point, angle_rad: float) -> Point:
        return (self - center).rotate(angle_rad) + center

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def perpendicular(self) -> Point:
        """90-degree CCW rotation."""
        return Point(-self.y, self.x)


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @staticmethod
    def from_points(points: Sequence[Point]) -> BoundingBox:
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return BoundingBox(min(xs), min(ys), max(xs), max(ys))

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> Point:
        return Point((self.x_min + self.x_max) / 2,
                     (self.y_min + self.y_max) / 2)

    @property
    def area(self) -> float:
        return self.width * self.height

    def contains(self, p: Point) -> bool:
        return (self.x_min <= p.x <= self.x_max and
                self.y_min <= p.y <= self.y_max)

    def expanded(self, margin: float) -> BoundingBox:
        return BoundingBox(self.x_min - margin, self.y_min - margin,
                           self.x_max + margin, self.y_max + margin)

    def union(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            min(self.x_min, other.x_min), min(self.y_min, other.y_min),
            max(self.x_max, other.x_max), max(self.y_max, other.y_max),
        )


# -- Affine transforms ---------------------------------------------------

@dataclass(frozen=True, slots=True)
class AffineTransform:
    """2D affine transform as a 2x3 matrix [a b tx; c d ty]."""
    a: float = 1.0
    b: float = 0.0
    tx: float = 0.0
    c: float = 0.0
    d: float = 1.0
    ty: float = 0.0

    def apply(self, p: Point) -> Point:
        return Point(self.a * p.x + self.b * p.y + self.tx,
                     self.c * p.x + self.d * p.y + self.ty)

    def then(self, other: AffineTransform) -> AffineTransform:
        """Compose: self then other (other applied first conceptually
        when reading left-to-right, but matrix multiply is self * other)."""
        return AffineTransform(
            a=other.a * self.a + other.c * self.b,
            b=other.b * self.a + other.d * self.b,
            tx=other.tx * self.a + other.ty * self.b + self.tx,
            c=other.a * self.c + other.c * self.d,
            d=other.b * self.c + other.d * self.d,
            ty=other.tx * self.c + other.ty * self.d + self.ty,
        )

    @staticmethod
    def identity() -> AffineTransform:
        return AffineTransform()

    @staticmethod
    def translate(dx: float, dy: float) -> AffineTransform:
        return AffineTransform(tx=dx, ty=dy)

    @staticmethod
    def scale(sx: float, sy: float | None = None) -> AffineTransform:
        if sy is None:
            sy = sx
        return AffineTransform(a=sx, d=sy)

    @staticmethod
    def rotate(angle_rad: float) -> AffineTransform:
        co, si = math.cos(angle_rad), math.sin(angle_rad)
        return AffineTransform(a=co, b=-si, c=si, d=co)

    @staticmethod
    def mirror_x() -> AffineTransform:
        return AffineTransform(a=-1.0)

    @staticmethod
    def mirror_y() -> AffineTransform:
        return AffineTransform(d=-1.0)
