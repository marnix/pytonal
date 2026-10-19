#!/usr/bin/env python3

from pytonal import *
import pytest

import re


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
    assert repr(Int.sharp.mod8()) == 'pytonal.Int(min2=0, aug1=1, modMin2=7, modAug1=5)'


# --- property-based tests (hypothesis) ---------------------------------------

from hypothesis import given, settings, strategies as st
from hypothesis.strategies import DrawFn


settings.register_profile("pytonal", deadline=None)
settings.load_profile("pytonal")

_coords = st.integers(min_value=-30, max_value=30)

# an interval, optionally modulo a nonzero single direction
_intervals = st.builds(
    Int,
    min2=_coords,
    aug1=_coords,
    modMin2=_coords,
    modAug1=_coords,
)


@st.composite
def _modded_intervals(draw: DrawFn) -> Int:
    """An interval together with a nonzero modulus (modMin2, modAug1)."""
    modMin2 = draw(_coords)
    modAug1 = draw(_coords)
    if modMin2 == 0 and modAug1 == 0:
        modMin2 = 1
    return Int(min2=draw(_coords), aug1=draw(_coords),
               modMin2=modMin2, modAug1=modAug1)


def test_is_multiple_matches_brute_force() -> None:
    # w is a multiple of v iff w == k*v for some integer k.
    from pytonal import _is_multiple
    for v in [(2, 0), (0, 3), (2, 4), (-2, 1), (0, 1), (1, -1)]:
        for k in range(-8, 9):
            assert _is_multiple((k * v[0], k * v[1]), v)
        # non-multiples: (1,0) vs (2,0), (0,1) vs (0,2), etc.
        for w in [(1, 0), (0, 1), (1, 1), (3, 2), (-1, 2)]:
            ok = any((w[0], w[1]) == (k * v[0], k * v[1]) for k in range(-40, 41))
            assert _is_multiple(w, v) == ok, (w, v)


@given(_modded_intervals())
def test_eq_reflexive(i: Int) -> None:
    assert i == i


@given(_modded_intervals(), _coords, _coords)
def test_eq_is_multiple_of_modulus(i: Int, k: int, dm: int) -> None:
    # shifting by k times the modulus must not change equality
    j = Int(min2=i.min2 + k * i.modMin2, aug1=i.aug1 + k * i.modAug1,
            modMin2=i.modMin2, modAug1=i.modAug1)
    assert i == j


@given(_modded_intervals(), _coords, _coords)
def test_eq_ignores_non_multiple_difference(i: Int, dm: int, da: int) -> None:
    # a difference that is not a multiple of the modulus must break equality
    j = Int(min2=i.min2 + dm, aug1=i.aug1 + da,
            modMin2=i.modMin2, modAug1=i.modAug1)
    from pytonal import _is_multiple
    is_mult = _is_multiple((dm, da), (i.modMin2, i.modAug1))
    assert (i == j) == is_mult


@given(_modded_intervals(), _modded_intervals())
def test_hash_consistent_with_eq(i: Int, j: Int) -> None:
    # whenever two intervals are equal, their hashes must match
    if (i.modMin2, i.modAug1) != (j.modMin2, j.modAug1):
        return  # different moduli are never equal
    if i == j:
        assert hash(i) == hash(j)


@given(_modded_intervals(), _coords, _coords)
def test_add_preserves_mod_span(i: Int, dm: int, da: int) -> None:
    j = Int(min2=dm, aug1=da, modMin2=i.modMin2, modAug1=i.modAug1)
    k = i + j
    assert (k.modMin2, k.modAug1) == (i.modMin2, i.modAug1)
    assert (k.min2, k.aug1) == (i.min2 + dm, i.aug1 + da)


@given(_modded_intervals(), st.integers(min_value=-5, max_value=5),
       st.integers(min_value=-5, max_value=5))
def test_add_asserts_on_different_mod_spans(i: Int, om: int, oa: int) -> None:
    other = Int(min2=0, aug1=0, modMin2=om, modAug1=oa)
    if (om, oa) == (i.modMin2, i.modAug1):
        assert (i + other).modMin2 == i.modMin2
    else:
        with pytest.raises(AssertionError):
            i + other


@given(_modded_intervals(), st.integers(min_value=-100, max_value=100))
def test_mul_and_neg_preserve_mod_span(i: Int, k: int) -> None:
    assert (k * i).modMin2 == i.modMin2
    assert (k * i).modAug1 == i.modAug1
    assert (-i).modMin2 == i.modMin2
    assert (-i).modAug1 == i.modAug1


@given(_modded_intervals(), st.integers(min_value=-100, max_value=100))
def test_sub_preserves_mod_span(i: Int, k: int) -> None:
    j = Int(min2=k, aug1=k, modMin2=i.modMin2, modAug1=i.modAug1)
    d = i - j
    assert (d.modMin2, d.modAug1) == (i.modMin2, i.modAug1)


def test_mod_vectors_are_not_collinear_only() -> None:
    # A non-primitive modulus must NOT equate a non-multiple difference,
    # which a bare collinearity (cross-product) test got wrong.
    a = Int(min2=0, aug1=0, modMin2=2, modAug1=0)
    b = Int(min2=1, aug1=0, modMin2=2, modAug1=0)
    assert a != b
    c = Int(min2=2, aug1=0, modMin2=2, modAug1=0)
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


def test_modInterval_assert_showcase() -> None:
    # This documents the restriction that modInterval() may only be applied
    # to an as-yet-unmodded interval; this assert will be removed when the
    # modulus becomes a list (mod basis).
    assert Int.unison.mod8().modAug1 == 5
    with pytest.raises(AssertionError, match="TODO: lift this restriction"):
        Int.unison.mod8().modEnh()


if __name__ == '__main__':
    import sys
    import pytest

    sys.exit(pytest.main([__file__, '-v', '-rP']))
