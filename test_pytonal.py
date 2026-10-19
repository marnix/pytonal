#!/usr/bin/env python3

from pytonal import *
import pytest

import re
from typing import List, Tuple


def test_interval_addition_subtraction() -> None:
    assert Int.fifth + Int.octave == Int.octave + Int.fifth
    assert Int.fifth - Int.fifth == Int.unison


def test_interval_multiplication() -> None:
    assert Int.nth(11) * 3 == Int.nth(11) + 2 * Int.nth(11)


def test_named_intervals() -> None:
    assert Int.unison == Int(min2=0, aug1=0)
    assert Int.fifth == Int(min2=4, aug1=3)
    assert Int.octave == Int(min2=7, aug1=5)
    assert Int.sharp == Int(min2=0, aug1=1)
    assert Int.pythagorean_comma == Int.sharp - Int.nth(2).minor()
    assert Int.pythagorean_comma == Int(min2=-1, aug1=1)


def test_nth() -> None:
    assert Int.nth(1) == Int.unison
    assert Int.nth(5) == Int.fifth
    assert Int.nth(8) == Int.octave
    assert Int.nth(9) == Int(min2=8, aug1=6)
    assert Int.nth(-5) == -Int.fifth
    assert Int.nth(-8) == -Int.octave
    assert Int.nth(-9) == -Int(min2=8, aug1=6)


def test_perfect() -> None:
    assert Int.nth(5).perfect() == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(3).perfect()


def test_major() -> None:
    assert Int.nth(3).major() == Int.nth(3)
    with pytest.raises(AssertionError):
        Int.nth(4).major()


def test_minor() -> None:
    assert Int.nth(3).minor() + Int.nth(3) == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(4).minor()


def test_invert() -> None:
    for n in range(2, 16):
        assert not Int.nth(n).isInverted(), f"n={n}"
        assert Int.nth(n).inverted().isInverted(), f"n={n}"
        assert not Int.nth(n).inverted().inverted().isInverted(), f"n={n}"
    assert not Int(min2=1, aug1=-1).isInverted()


def test_diminished() -> None:
    assert Int.nth(3).diminished() == Int(min2=2, aug1=0)
    assert Int.nth(3).diminished().inverted() == Int(min2=-2, aug1=0)


def test_augmented() -> None:
    assert Int.nth(4).augmented(n=2) == Int(min2=3, aug1=4)
    assert Int.nth(4).augmented(n=2) \
        == Int.nth(6).augmented() - Int.nth(3).minor()
    assert Int.unison.augmented() == Int.sharp


def test_diminished_augmented() -> None:
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().augmented() \
            == nth.diminished().inverted(), f"n={n}"
        assert nthInv.inverted().augmented() \
            == nthInv.diminished().inverted(), f"n={n}, inverted"


def test_augmented_diminished() -> None:
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().diminished() \
            == nth.augmented().inverted(), f"n={n}"
        assert nthInv.inverted().diminished() \
            == nthInv.augmented().inverted(), f"n={n}, inverted"


def test_mod8() -> None:
    assert Int(min2=0, aug1=0).mod8() == Int(min2=7, aug1=5).mod8()
    assert Int(min2=0, aug1=0).mod8() != Int(min2=7, aug1=0).mod8()
    assert Int.nth(9).mod8() == Int.nth(7).minor().inverted().mod8()
    assert Int.nth(5).mod8() == Int.nth(4).inverted().mod8()


def test_modEnh() -> None:
    for i in (Int.unison, Int.sharp, Int.fifth.diminished(), Int.octave.inverted()):
        assert i.modEnh() == i.modInterval(Int.pythagorean_comma)
    assert Int.sharp.modEnh() == Int.nth(2).minor().modEnh()
    assert Int.sharp.modEnh(12) == Int.nth(2).minor().modEnh(12)
    assert Int.sharp.modEnh(12, 7) == Int.nth(2).minor().modEnh(12, 7)
    assert Int.sharp.modEnh(19, 11) == Int.nth(2).diminished().modEnh(19, 11)
    assert Int.sharp.modEnh(19) == Int.nth(2).diminished().modEnh(19)
    with pytest.raises(AssertionError, match=re.escape("expected exactly one option for fifthSteps, instead of set()")):
        Int.sharp.modEnh(11)
    with pytest.raises(AssertionError, match=re.escape("expected exactly one option for fifthSteps, instead of {27, 28}")):
        Int.sharp.modEnh(47)
    assert (Int.nth(2).minor()*8).modEnh(47, 28) == Int.sharp.modEnh(47, 28)
    assert Int.nth(2).minor().modEnh(47, 27) == (Int.sharp*6).modEnh(47, 27)


def test_modAcc() -> None:
    assert Int.sharp.modAcc() == Int.unison.diminished(n=9).modAcc()
    assert Int.sharp.modAcc() == (-Int.sharp).modAcc()
    assert Int.unison != Int.nth(2)
    assert Int.unison.augmented() != Int.nth(2).diminished()


def test_repr() -> None:
    assert repr(Int.sharp.mod8()) == 'pytonal.Int(min2=0, aug1=1, modBasis=[(7, 5)])'


# --- property-based tests (hypothesis) ---------------------------------------

from hypothesis import given, settings, strategies as st
from hypothesis.strategies import DrawFn

from lattice import in_span_2d, hnf_2d


settings.register_profile("pytonal", deadline=None)
settings.load_profile("pytonal")

_coords = st.integers(min_value=-30, max_value=30)

_raw_basis = st.lists(st.tuples(_coords, _coords), max_size=3)


@st.composite
def _modded_intervals(draw: DrawFn) -> Int:
    """An interval together with a canonical mod basis."""
    return Int(min2=draw(_coords), aug1=draw(_coords),
               modBasis=draw(_raw_basis))


@given(_modded_intervals())
def test_eq_reflexive(i: Int) -> None:
    assert i == i


@given(_modded_intervals(), st.lists(_coords, max_size=3))
def test_eq_is_span_membership(i: Int, coeffs: List[int]) -> None:
    # shifting by any combination of the mod basis must not change equality
    dm = sum(c * v[0] for c, v in zip(coeffs, i.modBasis))
    da = sum(c * v[1] for c, v in zip(coeffs, i.modBasis))
    j = Int(min2=i.min2 + dm, aug1=i.aug1 + da, modBasis=i.modBasis)
    assert i == j


@given(_modded_intervals(), _coords, _coords)
def test_eq_iff_in_span(i: Int, dm: int, da: int) -> None:
    j = Int(min2=i.min2 + dm, aug1=i.aug1 + da, modBasis=i.modBasis)
    assert (i == j) == in_span_2d((dm, da), i.modBasis)


@given(_modded_intervals(), _modded_intervals())
def test_hash_consistent_with_eq(i: Int, j: Int) -> None:
    # whenever two intervals are equal, their hashes must match
    if i.modBasis != j.modBasis:
        return  # different mod bases are never equal
    if i == j:
        assert hash(i) == hash(j)


@given(_modded_intervals(), _coords, _coords)
def test_add_preserves_mod_basis(i: Int, dm: int, da: int) -> None:
    j = Int(min2=dm, aug1=da, modBasis=i.modBasis)
    k = i + j
    assert k.modBasis == i.modBasis
    assert (k.min2, k.aug1) == (i.min2 + dm, i.aug1 + da)


@given(_modded_intervals(), st.lists(st.tuples(_coords, _coords), max_size=3))
def test_add_raises_on_different_mod_spans(i: Int, other_basis: List[Tuple[int, int]]) -> None:
    other = Int(min2=0, aug1=0, modBasis=other_basis)
    if other.modBasis == i.modBasis:
        assert (i + other).modBasis == i.modBasis
    else:
        with pytest.raises(TypeError):
            i + other


@given(_modded_intervals(), st.integers(min_value=-100, max_value=100))
def test_mul_and_neg_preserve_mod_basis(i: Int, k: int) -> None:
    assert (k * i).modBasis == i.modBasis
    assert (-i).modBasis == i.modBasis


@given(_modded_intervals(), st.integers(min_value=-100, max_value=100))
def test_sub_preserves_mod_basis(i: Int, k: int) -> None:
    j = Int(min2=k, aug1=k, modBasis=i.modBasis)
    d = i - j
    assert d.modBasis == i.modBasis


def test_non_primitive_modulus_equates_only_multiples() -> None:
    # A non-primitive modulus must NOT equate a non-multiple difference,
    # which a bare collinearity (cross-product) test got wrong.
    a = Int(min2=0, aug1=0, modBasis=[(2, 0)])
    b = Int(min2=1, aug1=0, modBasis=[(2, 0)])
    assert a != b
    c = Int(min2=2, aug1=0, modBasis=[(2, 0)])
    assert a == c


def test_docstring_octave_modulo() -> None:
    # mod8 makes an interval equal to itself plus/minus any number of octaves.
    for k in (-3, -1, 1, 2):
        shifted = Int(min2=Int.fifth.min2 + k * Int.octave.min2,
                      aug1=Int.fifth.aug1 + k * Int.octave.aug1)
        assert Int.fifth.mod8() == shifted.mod8()
    # but the fourth is NOT equal to the fifth under mod8
    assert Int.fifth.mod8() != Int.nth(4).mod8()


def test_docstring_enharmonics() -> None:
    # modEnh makes chromatic enharmonics equal: C# == Db.
    assert Int.sharp.modEnh() == Int.nth(2).minor().modEnh()
    # but e.g. a major third is not equal to a minor third.
    assert Int.nth(3).modEnh() != Int.nth(3).minor().modEnh()


def test_docstring_accidentals() -> None:
    # modAcc makes intervals that differ only by sharps/flats equal, so
    # Cb, C, and C# collapse.
    Cb = Int.unison.diminished()
    assert Cb.modAcc() == Int.unison.modAcc() == Int.sharp.modAcc()
    # but a major second (different min2) stays distinct.
    assert Int.unison.modAcc() != Int.nth(2).modAcc()


def test_modInterval_accumulates_basis() -> None:
    # modInterval now accumulates: the mod basis grows into a canonical
    # lattice, and repeated mods compose regardless of order.
    i = Int.unison.mod8().modEnh()
    assert i.modBasis == hnf_2d([(7, 5), (Int.pythagorean_comma.min2,
                                           Int.pythagorean_comma.aug1)])
    # order independence
    assert Int.unison.mod8().modEnh() == Int.unison.modEnh().mod8()


def test_mod8_modEnh_canonical_use_case() -> None:
    # The canonical case: under mod8().modEnh(), B# equals C, and the octave
    # (and its multiples) also equals C, but the other simple named intervals
    # stay distinct (i.e. nothing else collapses into the unison).
    M = Int.unison.mod8().modEnh()
    Bsharp = Int.nth(7).augmented().mod8().modEnh()
    assert Bsharp == M
    # the octave is also equal to the unison (that is what mod8 does)
    assert Int.octave.mod8().modEnh() == M
    # but genuinely different pitch classes stay distinct
    for iv in (Int.sharp, Int.nth(2), Int.nth(3), Int.fifth):
        assert iv.mod8().modEnh() != M, iv


if __name__ == '__main__':
    import sys
    import pytest

    # hypothesis is already imported above (for its decorators), so pytest's
    # assertion-rewrite warning about it is expected and harmless.
    sys.exit(pytest.main([__file__, '-v', '-rP',
                          '-W', 'ignore::pytest.PytestAssertRewriteWarning']))
