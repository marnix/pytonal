#!/usr/bin/env python3

from pytonal import *
import pytest


def test_interval_addition_subtraction():
    assert Int.fifth + Int.octave == Int.octave + Int.fifth
    assert Int.fifth - Int.fifth == Int.unison


def test_interval_multiplication():
    assert Int.nth(11) * 3 == Int.nth(11) + 2 * Int.nth(11)


def test_named_intervals():
    assert Int.unison == Int(min2=0, aug1=0)
    assert Int.fifth == Int(min2=4, aug1=3)
    assert Int.octave == Int(min2=7, aug1=5)
    assert Int.sharp == Int(min2=0, aug1=1)
    assert Int.pythagorean_comma == Int.sharp - Int.nth(2).minor()
    assert Int.pythagorean_comma == Int(min2=-1, aug1=1)


def test_nth():
    assert Int.nth(1) == Int.unison
    assert Int.nth(5) == Int.fifth
    assert Int.nth(8) == Int.octave
    assert Int.nth(9) == Int(min2=8, aug1=6)
    assert Int.nth(-5) == -Int.fifth
    assert Int.nth(-8) == -Int.octave
    assert Int.nth(-9) == -Int(min2=8, aug1=6)


def test_perfect():
    assert Int.nth(5).perfect() == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(3).perfect()


def test_major():
    assert Int.nth(3).major() == Int.nth(3)
    with pytest.raises(AssertionError):
        Int.nth(4).major()


def test_minor():
    assert Int.nth(3).minor() + Int.nth(3) == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(4).minor()


def test_invert():
    for n in range(2, 16):
        assert not Int.nth(n).isInverted(), f"n={n}"
        assert Int.nth(n).inverted().isInverted(), f"n={n}"
        assert not Int.nth(n).inverted().inverted().isInverted(), f"n={n}"
    assert not Int(min2=1, aug1=-1).isInverted()


def test_diminished():
    assert Int.nth(3).diminished() == Int(min2=2, aug1=0)
    assert Int.nth(3).diminished().inverted() == Int(min2=-2, aug1=0)


def test_augmented():
    assert Int.nth(4).augmented(n=2) == Int(min2=3, aug1=4)
    assert Int.nth(4).augmented(n=2) \
        == Int.nth(6).augmented() - Int.nth(3).minor()
    assert Int.unison.augmented() == Int.sharp


def test_diminished_augmented():
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().augmented() \
            == nth.diminished().inverted(), f"n={n}"
        assert nthInv.inverted().augmented() \
            == nthInv.diminished().inverted(), f"n={n}, inverted"


def test_augmented_diminished():
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().diminished() \
            == nth.augmented().inverted(), f"n={n}"
        assert nthInv.inverted().diminished() \
            == nthInv.augmented().inverted(), f"n={n}, inverted"


def test_mod8():
    assert Int(min2=0, aug1=0).mod8() == Int(min2=7, aug1=5).mod8()
    assert Int(min2=0, aug1=0).mod8() != Int(min2=7, aug1=0).mod8()
    assert Int.nth(9).mod8() == Int.nth(7).minor().inverted().mod8()
    assert Int.nth(5).mod8() == Int.nth(4).inverted().mod8()


def test_modEnh():
    for i in (Int.unison, Int.sharp, Int.fifth.diminished(), Int.octave.inverted()):
        assert i.modEnh() == i.modInterval(Int.pythagorean_comma)
    assert Int.sharp.modEnh() == Int.nth(2).minor().modEnh()
    # TODO:
    # assert Int.sharp.modEnh(12) == Int.nth(2).minor().modEnh(12)
    assert Int.sharp.modEnh(12, 7) == Int.nth(2).minor().modEnh(12, 7)
    # TODO:
    # with pytest.raises(AssertionError):
    #     Int.sharp.modEnh(47)
    assert (Int.nth(2).minor()*8).modEnh(47, 28) == Int.sharp.modEnh(47, 28)
    assert Int.nth(2).minor().modEnh(47, 27) == (Int.sharp*6).modEnh(47, 27)


def test_modAcc():
    assert Int.sharp.modAcc() == Int.unison.diminished(n=9).modAcc()
    assert Int.sharp.modAcc() == (-Int.sharp).modAcc()
    assert Int.unison != Int.nth(2)
    assert Int.unison.augmented() != Int.nth(2).diminished()


if __name__ == '__main__':
    import sys
    import pytest

    sys.exit(pytest.main([__file__, '-v', '-rP']))
