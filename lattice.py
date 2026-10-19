from math import gcd
from typing import Iterable, List, Tuple

Vector = Tuple[int, int]


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Return g, p, q with g >= 0 and p*a + q*b == g."""
    old_r, r = abs(a), abs(b)
    old_p, p = 1, 0
    old_q, q = 0, 1

    while r:
        k = old_r // r
        old_r, r = r, old_r - k * r
        old_p, p = p, old_p - k * p
        old_q, q = q, old_q - k * q

    if a < 0:
        old_p = -old_p
    if b < 0:
        old_q = -old_q

    return old_r, old_p, old_q


def hnf_2d(vectors: Iterable[Vector]) -> List[Vector]:
    """Return a canonical basis for the integer span of vectors in Z²."""
    vectors = [(v[0], v[1]) for v in vectors]

    # Find a lattice vector (g, y) where g is the gcd of all x-coordinates.
    g = y = 0
    for x, yy in vectors:
        new_g, p, q = extended_gcd(g, x)
        y = p * y + q * yy
        g = new_g

    # If every x-coordinate is zero, the lattice is vertical or zero.
    if g == 0:
        h = 0
        for _, yy in vectors:
            h = gcd(h, yy)
        return [(0, h)] if h else []

    # The gcd of all 2x2 determinants is the rank-two lattice index.
    d = 0
    for i, (x1, y1) in enumerate(vectors):
        for x2, y2 in vectors[i + 1:]:
            d = gcd(d, x1 * y2 - y1 * x2)

    # Rank one: (g, y) is the canonical generator.
    if d == 0:
        return [(g, y)]

    # Rank two: reduce y modulo h to obtain canonical row-HNF.
    h = d // g
    return [(g, y % h), (0, h)]
