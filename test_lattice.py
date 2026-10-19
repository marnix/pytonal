#!/usr/bin/env python3

"""
Property-based tests for lattice.py, using Hypothesis.
Run like test_pytonal.py, i.e. as ./test_lattice.py or via pytest.
"""

import itertools
from math import gcd
from typing import List, Sequence, Tuple

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.strategies import DrawFn

from lattice import extended_gcd, hnf_2d, in_span_2d, canonical_rep_2d

Vector = Tuple[int, int]

# keep the tests fast: hnf_2d is only quadratic.
settings.register_profile("pytonal", deadline=None)
settings.load_profile("pytonal")

# Small coordinates still cover every rank (zero, rank one, rank two).
vectors = st.lists(
    st.tuples(
        st.integers(min_value=-30, max_value=30),
        st.integers(min_value=-30, max_value=30),
    ),
    max_size=6,
)


def _x_gcd(vs: Sequence[Vector]) -> int:
    """The gcd of all x-coordinates (the horizontal content)."""
    g = 0
    for x, _ in vs:
        g = gcd(g, x)
    return g


def _minors_gcd(vs: Sequence[Vector]) -> int:
    """The gcd of all 2x2 minors, i.e. the index of the generated lattice."""
    d = 0
    vecs = list(vs)
    for i, (x1, y1) in enumerate(vecs):
        for x2, y2 in vecs[i + 1:]:
            d = gcd(d, x1 * y2 - y1 * x2)
    return d


def in_span(w: Vector, vs: Sequence[Vector]) -> bool:
    """Is w an integer linear combination of the arbitrary vectors `vs`?

    This is an independent ORACLE for the implicit lattice L = span(vs): it
    is written as an integer column-elimination solver that directly attempts
    to decide whether the target w is reachable, rather than calling hnf_2d
    or reusing its canonical (g, y), (0, h) row-HNF. Concretely it reduces
    the columns of the 2 x n matrix [v1 | ... | vn] by unimodular integer
    column operations (Euclid-style, as in Smith reduction), which preserves
    the column lattice, and then reads off reachability of w from the reduced
    generators. Sharing the gcd-combination primitive is unavoidable in Z^2,
    but the code path and the membership decision are different from hnf_2d's.
    """
    if not vs:
        return w == (0, 0)

    cols = [(x, y) for x, y in vs]

    # Euclid-reduce the x-row to a single nonzero entry d1 at column 0, by
    # unimodular combinations of column 0 with each later column j:
    #   col0 <- p*col0 + q*colj          (x becomes gcd(a, b))
    #   colj <- (b/g)*col0 - (a/g)*colj  (x becomes 0)
    # where (g, p, q) = extended_gcd(a, b) for a = col0.x, b = colj.x.
    for j in range(1, len(cols)):
        a, b = cols[0][0], cols[j][0]
        if b == 0:
            continue
        g, p, q = extended_gcd(a, b)
        u, v = cols[0], cols[j]
        cols[0] = (p * u[0] + q * v[0], p * u[1] + q * v[1])
        cols[j] = ((b // g) * u[0] - (a // g) * v[0],
                   (b // g) * u[1] - (a // g) * v[1])

    d1 = cols[0][0]
    wx, wy = w

    if d1 == 0:
        # All x-coordinates vanished: the lattice is vertical or zero.
        h = 0
        for _, yy in cols:
            h = gcd(h, yy)
        if h == 0:
            return wx == 0 and wy == 0
        return wx == 0 and wy % h == 0

    # Vertical remainder of the lattice from the x-free columns.
    h = 0
    for _, yy in cols[1:]:
        h = gcd(h, yy)

    # Reduce w against the generator (d1, y0) and then the vertical step h.
    if wx % d1 != 0:
        return False
    rest = wy - (wx // d1) * cols[0][1]
    if h == 0:
        return rest == 0
    return rest % h == 0


def _in_span(w: Vector, basis: Sequence[Vector]) -> bool:
    """Is w an integer linear combination of the (canonical) basis?"""
    wx, wy = w
    if not basis:
        return wx == 0 and wy == 0
    if len(basis) == 1:
        bx, by = basis[0]
        if bx == 0:
            return wx == 0 and wy % by == 0
        if wx % bx != 0:
            return False
        return (wx // bx) * by == wy
    assert len(basis) == 2
    (g, y), (z, h) = basis
    assert z == 0
    if wx % g != 0:
        return False
    return (wy - (wx // g) * y) % h == 0


def _scaled_basis(basis: Sequence[Vector], k: int) -> List[Vector]:
    """The canonical HNF of k times a lattice with the given HNF (k > 0)."""
    if not basis:
        return []
    if len(basis) == 1:
        (g, y), = basis
        return [(k * g, k * y)]
    (g, y), (_, h) = basis
    return [(k * g, k * y), (0, k * h)]


@st.composite
def canonical_bases(draw: DrawFn) -> List[Vector]:
    """Canonical row-HNF bases: empty, vertical, rank one, or rank two."""
    kind = draw(st.integers(min_value=0, max_value=3))
    if kind == 0:
        return []
    if kind == 1:
        h = draw(st.integers(min_value=1, max_value=30))
        return [(0, h)]
    g = draw(st.integers(min_value=1, max_value=30))
    if kind == 2:
        y = draw(st.integers(min_value=-30, max_value=30))
        return [(g, y)]
    h = draw(st.integers(min_value=1, max_value=30))
    y = draw(st.integers(min_value=0, max_value=h - 1))
    return [(g, y), (0, h)]


@given(
    st.integers(min_value=-(10 ** 6), max_value=10 ** 6),
    st.integers(min_value=-(10 ** 6), max_value=10 ** 6),
)
def test_extended_gcd_bézout(a: int, b: int) -> None:
    g, p, q = extended_gcd(a, b)
    assert g == gcd(a, b)
    assert g >= 0
    assert p * a + q * b == g


@given(vectors)
def test_hnf_is_canonical(vs: List[Vector]) -> None:
    basis = hnf_2d(vs)
    assert len(basis) <= 2
    for x, y in basis:
        assert isinstance(x, int) and isinstance(y, int)
    if len(basis) == 1:
        bx, by = basis[0]
        assert bx > 0 or (bx == 0 and by > 0)
    if len(basis) == 2:
        (g, y), (z, h) = basis
        assert g > 0 and z == 0 and h > 0
        assert 0 <= y < h


@given(vectors)
def test_hnf_contains_its_input(vs: List[Vector]) -> None:
    basis = hnf_2d(vs)
    for w in vs:
        assert _in_span(w, basis)


@given(vectors)
def test_hnf_preserves_lattice_invariants(vs: List[Vector]) -> None:
    basis = hnf_2d(vs)
    assert _x_gcd(basis) == _x_gcd(vs)
    d = _minors_gcd(vs)
    if len(basis) == 2:
        (g, _), (_, h) = basis
        assert g * h == d
    else:
        assert d == 0


@given(vectors)
def test_hnf_is_idempotent(vs: List[Vector]) -> None:
    once = hnf_2d(vs)
    assert hnf_2d(once) == once


@given(vectors, vectors)
def test_hnf_is_order_invariant(vs: List[Vector], ws: List[Vector]) -> None:
    assert hnf_2d(vs + ws) == hnf_2d(ws + vs)


@given(vectors)
def test_hnf_of_negation(vs: List[Vector]) -> None:
    assert hnf_2d([(-x, -y) for x, y in vs]) == hnf_2d(vs)


@given(vectors, st.sampled_from([-3, -2, -1, 1, 2, 3]))
def test_hnf_scales_with_the_lattice(vs: List[Vector], k: int) -> None:
    scaled = [(k * x, k * y) for x, y in vs]
    assert hnf_2d(scaled) == _scaled_basis(hnf_2d(vs), abs(k))


@given(vectors, st.integers(min_value=-5, max_value=5), st.integers(min_value=-5, max_value=5))
def test_adding_a_spanning_vector_changes_nothing(vs: List[Vector], c1: int, c2: int) -> None:
    basis = hnf_2d(vs)
    if not basis:
        return
    v = (c1 * basis[0][0], c1 * basis[0][1])
    if len(basis) == 2:
        v = (v[0] + c2 * basis[1][0], v[1] + c2 * basis[1][1])
    assert hnf_2d(vs + [v]) == basis


@given(canonical_bases())
def test_canonical_basis_is_a_fixed_point(basis: List[Vector]) -> None:
    assert hnf_2d(basis) == basis


@given(st.lists(st.integers(min_value=-100, max_value=100), min_size=1))
def test_hnf_of_vertical_vectors(ys: List[int]) -> None:
    g = 0
    for y in ys:
        g = gcd(g, y)
    expected = [(0, g)] if g else []
    assert hnf_2d([(0, y) for y in ys]) == expected


def test_hnf_of_nothing_is_nothing() -> None:
    assert hnf_2d([]) == []
    assert hnf_2d([(0, 0)]) == []
    assert hnf_2d([(0, 0), (0, 0), (0, 0)]) == []


# --- span preservation -------------------------------------------------------

@st.composite
def vectors_with_coefficients(draw: DrawFn) -> Tuple[List[Vector], List[int]]:
    """A list of vectors plus coefficients, so draw(_)[0] spans their sum."""
    vs = draw(vectors)
    cs = draw(st.lists(
        st.integers(min_value=-3, max_value=3),
        min_size=len(vs),
        max_size=len(vs),
    ))
    return vs, cs


@given(vectors, st.tuples(st.integers(min_value=-90, max_value=90),
                          st.integers(min_value=-90, max_value=90)))
def test_hnf_preserves_the_spanned_space(vs: List[Vector], w: Vector) -> None:
    """w is in span(vs) iff w is in span(hnf_2d(vs)) -- the core property."""
    assert in_span(w, vs) == in_span(w, hnf_2d(vs))


@given(vectors_with_coefficients())
def test_hnf_preserves_every_spanned_vector(data: Tuple[List[Vector], List[int]]) -> None:
    """Every integer combination of the inputs is still in the HNF's span."""
    vs, cs = data
    w = (sum(c * v[0] for c, v in zip(cs, vs)),
         sum(c * v[1] for c, v in zip(cs, vs)))
    assert in_span(w, vs)
    assert in_span(w, hnf_2d(vs))


@given(vectors)
def test_hnf_returned_vectors_are_in_the_input_span(vs: List[Vector]) -> None:
    """Soundness: each returned generator is spanned by the inputs."""
    for b in hnf_2d(vs):
        assert in_span(b, vs) or b == (0, 0)


@given(vectors)
def test_hnf_returns_at_most_two_vectors(vs: List[Vector]) -> None:
    """Regardless of how many inputs, the canonical basis has at most two."""
    assert len(hnf_2d(vs)) <= 2


# --- in_span_2d and canonical_rep_2d -----------------------------------------

@given(vectors, vectors)
def test_in_span_2d_matches_input_span(vs: List[Vector], ws: List[Vector]) -> None:
    """in_span_2d agrees with hnf_2d's span, on both members and non-members."""
    for w in ws:
        assert in_span_2d(w, vs) == in_span(w, hnf_2d(vs))


@given(vectors, st.lists(st.integers(min_value=-5, max_value=5), max_size=6))
def test_in_span_2d_includes_combinations(vs: List[Vector], coeffs: List[int]) -> None:
    """Any integer combination of the basis is reported as in span."""
    total = (0, 0)
    for c, v in zip(coeffs, vs):
        total = (total[0] + c * v[0], total[1] + c * v[1])
    assert in_span_2d(total, vs)


def _brute_in_span(w: Vector, vs: Sequence[Vector], bound: int) -> bool:
    """Exhaustive-search membership reference, independent of Euclid reduction.

    Searches for integer coefficients in [-bound, bound] with sum(c_i*v_i) == w.
    For the tiny inputs used below (|coords| <= 3, |w| <= 6, at most two
    vectors), any existing solution has coefficients of magnitude <= 36, so
    bound=40 makes this a reliable oracle.
    """
    if not vs:
        return w == (0, 0)
    ranges = [range(-bound, bound + 1) for _ in vs]
    for cs in itertools.product(*ranges):
        total = (sum(c * v[0] for c, v in zip(cs, vs)),
                 sum(c * v[1] for c, v in zip(cs, vs)))
        if total == w:
            return True
    return False


@given(
    st.lists(st.tuples(st.integers(min_value=-3, max_value=3),
                       st.integers(min_value=-3, max_value=3)), max_size=2),
    st.tuples(st.integers(min_value=-6, max_value=6),
              st.integers(min_value=-6, max_value=6)),
)
def test_in_span_2d_matches_brute_force(vs: List[Vector], w: Vector) -> None:
    """Independent check against exhaustive coefficient search (small inputs)."""
    assert in_span_2d(w, vs) == _brute_in_span(w, vs, 40)


@given(vectors, vectors)
def test_canonical_rep_2d_consistent_with_in_span(vs: List[Vector],
                                                  ws: List[Vector]) -> None:
    """Equal representatives iff the difference is in the span."""
    for w in ws:
        same_rep = canonical_rep_2d(w, vs) == canonical_rep_2d((0, 0), vs)
        assert same_rep == in_span_2d(w, vs)


@given(vectors, st.lists(st.integers(min_value=-3, max_value=3), max_size=4))
def test_canonical_rep_2d_is_coset_invariant(vs: List[Vector], coeffs: List[int]) -> None:
    """Shifting by a span element does not change the representative."""
    shift = (0, 0)
    for c, v in zip(coeffs, vs):
        shift = (shift[0] + c * v[0], shift[1] + c * v[1])
    w = canonical_rep_2d((0, 0), vs)
    w_shifted = canonical_rep_2d(shift, vs)
    assert w == w_shifted


if __name__ == '__main__':
    import sys
    import pytest

    # hypothesis is already imported above (for its decorators), so pytest's
    # assertion-rewrite warning about it is expected and harmless.
    sys.exit(pytest.main([__file__, '-v', '-rP',
                          '-W', 'ignore::pytest.PytestAssertRewriteWarning']))
