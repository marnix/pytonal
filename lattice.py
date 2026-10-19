from math import gcd
from typing import Iterable, List, Tuple

Vector = Tuple[int, int]


def gcd_euclid(a: int, b: int) -> Tuple[int, int, int]:
    """Return g, p, q with g >= 0 and p*a + q*b == g, by the Euclidean algorithm."""
    if b == 0:
        return abs(a), (1 if a >= 0 else -1), 0
    g, p, q = gcd_euclid(b, a % b)
    return g, q, p - (a // b) * q


def hnf_2d(vectors: Iterable[Vector]) -> List[Vector]:
    """Return a canonical basis for the integer span of vectors in Z²."""
    vectors = [(v[0], v[1]) for v in vectors]

    # Find a lattice vector (g, y) where g is the gcd of all x-coordinates.
    g = y = 0
    for x, yy in vectors:
        new_g, p, q = gcd_euclid(g, x)
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


def canonical_rep_2d(w: Vector, basis: Iterable[Vector]) -> Vector:
    """A canonical representative of the coset w + span(basis).

    Two vectors have the same representative iff they differ by an element of
    the integer span of `basis`. Useful for hashing cosets.
    """
    h = hnf_2d(basis)
    x, y = w[0], w[1]
    if not h:
        return (x, y)
    if len(h) == 1:
        g, gy = h[0]
        if g == 0:
            # vertical generator (0, gy); only x == 0 is representable, but
            # for hashing we simply reduce y modulo gy.
            return (x, y % gy)
        x = x % g
        y = y - ((w[0] - x) // g) * gy
        return (x, y)
    (g, gy), (_, hy) = h
    x = x % g
    y = (y - ((w[0] - x) // g) * gy) % hy
    return (x, y)


def in_span_2d(w: Vector, basis: Iterable[Vector]) -> bool:
    """Is the vector `w` in the integer span of the vectors `basis`?

    Works for an arbitrary basis; internally it reduces the basis by
    Euclid-style unimodular column operations and then decides reachability
    of `w`.
    """
    vecs = [(v[0], v[1]) for v in basis]
    if not vecs:
        return w == (0, 0)

    # Euclid-reduce the x-row to a single nonzero entry d1 at column 0.
    for j in range(1, len(vecs)):
        a, b = vecs[0][0], vecs[j][0]
        if b == 0:
            continue
        g, p, q = gcd_euclid(a, b)
        u, v = vecs[0], vecs[j]
        vecs[0] = (p * u[0] + q * v[0], p * u[1] + q * v[1])
        vecs[j] = ((b // g) * u[0] - (a // g) * v[0],
                   (b // g) * u[1] - (a // g) * v[1])

    d1 = vecs[0][0]
    wx, wy = w

    if d1 == 0:
        h = 0
        for _, yy in vecs:
            h = gcd(h, yy)
        if h == 0:
            return wx == 0 and wy == 0
        return wx == 0 and wy % h == 0

    h = 0
    for _, yy in vecs[1:]:
        h = gcd(h, yy)

    if wx % d1 != 0:
        return False
    rest = wy - (wx // d1) * vecs[0][1]
    if h == 0:
        return rest == 0
    return rest % h == 0
